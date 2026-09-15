import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import sys

from common import read_json
from corpus import build, specification, vendor_files
from experiment import default_config, execute, fixture_response, parse_answer, prepare
from analyze_v2 import analyze
from rag import Extractor, load_chunks


class PipelineTests(unittest.TestCase):
    def test_retrieval_identical_across_process_hash_seeds(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'corpus'
            build(root,specification(vendors=32,assignments=1,repetitions=1))
            code='from experiment import prepare,default_config; from common import digest; import sys; print(digest(prepare(sys.argv[1],default_config())[1]))'
            results=[subprocess.check_output([sys.executable,'-c',code,str(root)],cwd=Path(__file__).parent,env={**os.environ,'PYTHONHASHSEED':str(seed)}) for seed in (1,2,17)]
            self.assertEqual(len(set(results)),1)

    def test_resume_preserves_changed_saved_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'corpus'; out=Path(temp)/'run'
            build(root,specification(vendors=4,assignments=1,repetitions=1))
            execute(root,out,default_config(),max_calls=1)
            trace=next((out/'retrieval').glob('*.json'))
            trace.write_text('{}',encoding='utf-8')
            ledger=(out/'ledger.json').read_bytes()
            with self.assertRaises(ValueError):
                execute(root,out,default_config(),max_calls=2)
            self.assertEqual(trace.read_text(),'{}')
            self.assertEqual((out/'ledger.json').read_bytes(),ledger)

    def test_facts_and_visible_prose_identical_across_bundles(self):
        vendor = specification(vendors=4,assignments=1)["identities"][0]
        visible=[]
        for b in "ABCD":
            parser=Extractor()
            parser.feed(vendor_files(vendor,b,"https://v001.audit.invalid")["index.html"])
            visible.append(" ".join(parser.plain))
            if b in "CD":
                schema=json.loads(parser.schema[0])
                self.assertEqual(schema["offers"]["price"],vendor["facts"]["price"])
                self.assertEqual(schema["offers"]["seller"]["name"],vendor["name"])
        self.assertEqual(len(set(visible)),1)

    def test_treatments_disabled_make_rankings_invariant(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"corpus"
            build(root,specification(vendors=8,assignments=4,repetitions=1))
            config=default_config()
            config.update(schema_in_index=False,llms_in_index=False)
            spec,traces,indexes=prepare(root,config)
            for query in spec["queries"]:
                rankings=[]
                for a in spec["assignments"]:
                    trace=traces[a["assignment_id"]+":"+query["query_id"]]
                    rankings.append([(c["url"],c["bm25_score"]) for c in trace["retrieved"]])
                self.assertTrue(all(r==rankings[0] for r in rankings))

    def test_tampering_fails_before_retrieval(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"corpus"
            build(root,specification(vendors=4,assignments=1))
            (root/"sites/a000/v001/index.html").write_text("changed")
            with self.assertRaises(ValueError):
                load_chunks(root,"a000")

    def test_schema_is_actually_indexed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"corpus"
            build(root,specification(vendors=4,assignments=1))
            on=load_chunks(root,"a000",True)
            off=load_chunks(root,"a000",False)
            self.assertTrue(any('priceCurrency' in c["text"] for c in on))
            self.assertFalse(any('priceCurrency' in c["text"] for c in off))

    def test_missing_response_and_error_not_zero(self):
        def failing(*args):
            raise TimeoutError()
        with tempfile.TemporaryDirectory() as temp:
            corpus=Path(temp)/"corpus"
            output=Path(temp)/"run"
            build(corpus,specification(vendors=4,assignments=1,repetitions=1))
            execute(corpus,output,default_config(),max_calls=1,generator=failing)
            result=analyze(output)
            self.assertEqual(result["response_statuses"]["api_error"],1)
            self.assertEqual(result["response_statuses"]["not_run"],23)
            self.assertTrue(all(b["p_recommended_valid_responses_only"] is None for b in result["bundles"].values()))

    def test_resuming_completed_fixture_uses_no_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus=Path(temp)/"corpus"
            output=Path(temp)/"run"
            build(corpus,specification(vendors=4,assignments=1,repetitions=1))
            result=execute(corpus,output,default_config(),max_calls=24)
            self.assertTrue(result["complete"])
            def forbidden(*args):
                self.fail("Previously completed response called again")
            execute(corpus,output,default_config(),max_calls=24,generator=forbidden)
            result=analyze(output)
            self.assertIsNone(result["D_minus_A_interval"])
            self.assertTrue(result["synthetic_generation"])

    def test_unknown_name_and_wrong_source_logged(self):
        vendor=specification(vendors=4,assignments=1)["identities"]
        shown=[{"vendor_id":vendor[0]["vendor_id"],"shown_text":vendor[0]["name"]}]
        text=json.dumps({"decision":"recommend","recommendations":[{"name":"Unknown Store","source":1}],"explanation":"x"})
        parsed=parse_answer(text,shown,vendor)
        self.assertEqual(parsed["unknown_names"],["Unknown Store"])
        self.assertEqual(len(parsed["unsupported_recommendations"]),1)

    def test_invalid_abstention_is_not_accepted(self):
        with self.assertRaises(ValueError):
            parse_answer('{"decision":"recommend","recommendations":[],"explanation":"x"}',[],[])


if __name__ == "__main__":
    unittest.main()
