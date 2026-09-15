"""Auditable fixed-corpus BM25. No crawler, automatic dedup or opaque extraction."""
from collections import Counter
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import unicodedata

from common import digest, read_json


def tokens(text):
    return re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold())


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.plain, self.schema = [], []
        self.script_type = None
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self.hidden += 1
        if tag == "script":
            self.script_type = dict(attrs).get("type", "")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self.hidden = max(0, self.hidden - 1)
        if tag == "script":
            self.script_type = None

    def handle_data(self, data):
        if self.script_type == "application/ld+json":
            self.schema.append(data)
        elif not self.hidden:
            self.plain.append(data)


def load_chunks(corpus, assignment_id, schema_in_index=True, llms_in_index=True, chunk_words=100):
    if chunk_words < 10:
        raise ValueError("chunk_words must be >=10")
    corpus = Path(corpus)
    chunks = []
    for item in read_json(corpus / "files.json"):
        if item["assignment_id"] != assignment_id:
            continue
        path = (corpus / item["path"]).resolve()
        if not path.is_relative_to(corpus.resolve()):
            raise ValueError("Corpus path escapes root")
        content = path.read_text(encoding="utf-8")
        if digest(content) != item["sha256"]:
            raise ValueError("Corpus modified: " + item["path"])
        sources = []
        if item["file"] == "index.html":
            parser = Extractor()
            parser.feed(content)
            plain = " ".join(parser.plain)
            # Schema serialized in the SAME document to expose length/repetition effects in BM25.
            structured = " ".join(json.dumps(json.loads(s), ensure_ascii=False, sort_keys=True)
                                  for s in parser.schema)
            sources = [("html+schema" if structured and schema_in_index else "html",
                        plain + ("\n" + structured if schema_in_index else ""))]
        elif item["file"] == "llms.txt" and llms_in_index:
            sources = [("llms", content)]
        elif item["kind"] == "editorial":
            sources = [("editorial", content)]
        for source, text in sources:
            words = text.split()
            for start in range(0, len(words), chunk_words):
                passage = " ".join(words[start:start+chunk_words])
                chunk = {"chunk_id": f"{item['path']}:{source}:{start}",
                         "vendor_id": item["vendor_id"], "url": item["url"],
                         "source": source, "text": passage, "word_start": start,
                         "word_end": min(start+chunk_words, len(words))}
                chunk["sha256"] = digest(chunk)
                chunks.append(chunk)
    return chunks


class BM25:
    def __init__(self, chunks, k1=1.2, b=0.75):
        if not chunks:
            raise ValueError("Empty index")
        self.chunks, self.k1, self.b = chunks, k1, b
        self.counts = [Counter(tokens(c["text"])) for c in chunks]
        self.lengths = [sum(c.values()) for c in self.counts]
        self.average = sum(self.lengths) / len(chunks)
        self.df = Counter(t for c in self.counts for t in c)

    def search(self, query, k=5, tie_seed=0, max_per_vendor=1):
        ranking = []
        for chunk, counts, length in zip(self.chunks, self.counts, self.lengths):
            score = 0.0
            # Fix floating-point accumulation order across Python processes.
            for term in sorted(set(tokens(query))):
                tf = counts[term]
                if tf:
                    idf = math.log(1 + (len(self.chunks)-self.df[term]+0.5)/(self.df[term]+0.5))
                    score += idf * tf * (self.k1+1)/(tf+self.k1*(1-self.b+self.b*length/self.average))
            if score > 0:
                # Tie-break uses seed + opaque IDs, independent of treatment labels and disk ordering.
                tie = digest([tie_seed, chunk["url"], chunk["word_start"]])
                ranking.append((score, tie, chunk))
        ranking.sort(key=lambda x: (-x[0], x[1]))
        selected, seen = [], Counter()
        for score, tie, chunk in ranking:
            vid = chunk["vendor_id"]
            if vid and seen[vid] >= max_per_vendor:
                continue
            selected.append(dict(chunk, bm25_score=score, rank=len(selected)+1))
            if vid:
                seen[vid] += 1
            if len(selected) == k:
                break
        return selected


def make_context(chunks, max_words=700):
    """Log the exact shown passages; no hidden list of nonretrieved candidate names."""
    shown, remaining = [], max_words
    for chunk in chunks:
        words = chunk["text"].split()
        if not remaining:
            break
        actual = " ".join(words[:remaining])
        shown.append(dict(chunk, shown_text=actual, truncated=len(words)>remaining))
        remaining -= min(remaining, len(words))
    # IDs returned to the generator are context-only ordinals, not vendor/bundle/assignment labels.
    text = "\n\n".join(f"Fonte {i+1}\nURL: {c['url']}\n{c['shown_text']}" for i, c in enumerate(shown))
    return text, shown
