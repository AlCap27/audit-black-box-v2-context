"""Render reproducible experimental fixtures, not real merchant websites."""
import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import random

from common import digest, save_json

BUNDLES = {
    "A": {"sitemap": False, "schema": False, "llms": False},
    "B": {"sitemap": True, "schema": False, "llms": False},
    "C": {"sitemap": True, "schema": True, "llms": False},
    "D": {"sitemap": True, "schema": True, "llms": True},
}
FACTS = {"product": "Rosso italiano", "price": "20.00", "currency": "EUR",
         "volume_ml": 750, "stock": "disponibile", "delivery_days": "3-5",
         "shipping_eur": "6.00", "destination": "Italia"}
PHRASES = [
    "{name} è un'enoteca online indipendente. Vende Rosso italiano in bottiglia da 750 ml a 20.00 EUR. Il vino è disponibile. Spedizione in Italia: 6.00 EUR, consegna in 3-5 giorni.",
    "Da {name}, enoteca indipendente online, puoi acquistare Rosso italiano: bottiglia da 750 ml, prezzo 20.00 EUR, disponibile. La consegna in Italia richiede 3-5 giorni; la spedizione costa 6.00 EUR.",
    "Acquisto online da {name}, enoteca indipendente: Rosso italiano disponibile a 20.00 EUR per bottiglia da 750 ml. Il costo di spedizione è 6.00 EUR e la consegna in Italia avviene in 3-5 giorni.",
    "{name} vende vino online come enoteca indipendente. Rosso italiano costa 20.00 EUR, è disponibile e viene offerto in bottiglie da 750 ml. Spedisce in Italia per 6.00 EUR con consegna in 3-5 giorni.",
]
QUERY_BASES = [
    "vino rosso italiano da 20 euro", "bottiglia di vino rosso con spedizione in Italia",
    "Rosso italiano disponibile online", "vino italiano in bottiglia da 750 ml",
    "rosso italiano con consegna in 3-5 giorni", "vino rosso con spedizione da 6 euro",
    "bottiglia di rosso italiano sotto 25 euro", "vino da un'enoteca indipendente online",
    "vino rosso con prezzo e disponibilità dichiarati", "Rosso italiano con costi di spedizione chiari",
    "vino italiano da 750 ml a 20 euro", "bottiglia di vino da un negozio specializzato",
]


def specification(seed=20260905, vendors=32, assignments=8, repetitions=5):
    if vendors < 4 or vendors > 96 or vendors % 4 or assignments < 1 or repetitions < 1:
        raise ValueError("Require 4..96 vendors divisible by four and positive assignments/repetitions")
    # Fixed-length synthetic identities; no claim of verified absence from training data.
    syllables = [a + b for a in ("Zel", "Vor", "Lum", "Ner", "Tal", "Fes", "Ral", "Sov")
                 for b in ("davo", "mira", "nelo", "rivo", "sula", "taro", "vemi", "zuno", "pali", "goro", "ceni", "bula")]
    rng = random.Random(seed)
    rng.shuffle(syllables)
    identities = [{"vendor_id": f"v{i+1:03}", "name": f"Enoteca {syllables[i]}",
                   "template": i % 4, "facts": FACTS} for i in range(vendors)]
    layouts = []
    for a in range(assignments):
        # Independent balanced random assignments. No claim of full Latin-square crossover.
        labels = list("ABCD") * (vendors // 4)
        random.Random(seed + 1000 + a).shuffle(labels)
        layouts.append({"assignment_id": f"a{a:03}", "seed": seed + 1000 + a,
                        "bundles": dict(zip([v["vendor_id"] for v in identities], labels))})
    queries = []
    for intent, prefix in [("transactional", "Dove posso comprare "),
                           ("evaluative", "Quali enoteche online valuteresti per ")]:
        for q in QUERY_BASES:
            queries.append({"query_id": f"q{len(queries)+1:02}", "intent": intent,
                            "text": prefix + q + "?"})
    return {"version": "2.0.0-pilot", "seed": seed, "identities": identities,
            "assignments": layouts, "queries": queries, "repetitions": repetitions,
            "bundles": BUNDLES, "facts_sha256": digest(FACTS),
            "names_screened_web": False, "names_screened_memory": False,
            "scanner_calibrated": False, "score_targets": None,
            "scope": "fixed corpus; direct manifest indexing; sitemap discovery excluded",
            "assignment_policy": "independent balanced random permutations"}


def vendor_files(vendor, bundle, site):
    name = vendor["name"]
    prose = PHRASES[vendor["template"]].format(name=name)
    structured = {"@context": "https://schema.org", "@type": "Product",
                  "name": FACTS["product"], "description": prose,
                  "offers": {"@type": "Offer", "price": FACTS["price"],
                             "priceCurrency": "EUR", "availability": "https://schema.org/InStock",
                             "seller": {"@type": "Organization", "name": name}}}
    script = ('<script type="application/ld+json">' +
              json.dumps(structured, ensure_ascii=False) + "</script>") if BUNDLES[bundle]["schema"] else ""
    html = ('<!doctype html><html lang="it"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex"><title>' + escape(name) +
            '</title>' + script + '</head><body><main><h1>' + escape(name) +
            '</h1><p>' + escape(prose) + '</p></main></body></html>')
    files = {"index.html": html, "robots.txt": "User-agent: *\nAllow: /\n"}
    if BUNDLES[bundle]["sitemap"]:
        files["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>'
                                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                f'<url><loc>{escape(site)}/</loc></url></urlset>')
        files["robots.txt"] += f"Sitemap: {site}/sitemap.xml\n"
    if BUNDLES[bundle]["llms"]:
        files["llms.txt"] = f"# {name}\n\n{prose}\n"
    return files


def build(directory, spec):
    directory = Path(directory)
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Use a new empty corpus directory; artifacts are immutable")
    directory.mkdir(parents=True, exist_ok=True)
    index = []
    for assignment in spec["assignments"]:
        aid = assignment["assignment_id"]
        for vendor in spec["identities"]:
            vid = vendor["vendor_id"]
            # The same virtual root across assignments; URL length carries no bundle labels.
            site = f"https://{vid}.audit.invalid"
            files = vendor_files(vendor, assignment["bundles"][vid], site)
            for filename, content in files.items():
                rel = f"sites/{aid}/{vid}/{filename}"
                dest = directory / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
                index.append({"assignment_id": aid, "vendor_id": vid, "kind": "vendor",
                              "path": rel, "url": site + ("/" if filename == "index.html" else "/"+filename),
                              "file": filename, "sha256": digest(content)})
        # One editorial document per target homepage; not a claim of equal indexed tokens/chunks.
        for i in range(len(spec["identities"])):
            text = (f"Guida editoriale {i+1}. " + QUERY_BASES[i % len(QUERY_BASES)] +
                    ". Una bottiglia di vino rosso italiano si può valutare per stile, "
                    "prezzo e abbinamenti. Questa guida non identifica venditori o negozi.")
            rel = f"editorial/{aid}/e{i:03}.txt"
            dest = directory / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            index.append({"assignment_id": aid, "vendor_id": None, "kind": "editorial",
                          "path": rel, "file": f"e{i:03}.txt", "url": f"https://e{i:03}.editorial.invalid/",
                          "sha256": digest(text)})
    save_json(directory / "spec.json", spec)
    save_json(directory / "files.json", index)
    checks = {"balanced_assignments": all(Counter(a["bundles"].values()) ==
                Counter({b: len(spec["identities"])//4 for b in BUNDLES}) for a in spec["assignments"]),
              "fact_sheets_identical": all(digest(v["facts"]) == spec["facts_sha256"] for v in spec["identities"]),
              "prose_stable_within_vendor": True,
              "names_unique": len({v["name"] for v in spec["identities"]}) == len(spec["identities"]),
              "score_calibration": "not_run", "name_collision_checks": "not_run",
              "files": len(index), "spec_sha256": digest(spec), "files_sha256": digest(index)}
    save_json(directory / "qc.json", checks)
    return checks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--vendors", type=int, default=32)
    parser.add_argument("--assignments", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260905)
    args = parser.parse_args()
    print(json.dumps(build(args.output, specification(args.seed, args.vendors,
          args.assignments, args.repetitions)), indent=2))
