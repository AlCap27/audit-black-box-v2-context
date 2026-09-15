import tempfile
import unittest
from scan_orchestrator import run, measurement, validate_manifest


class ScanTests(unittest.TestCase):
    def manifest(self):
        return {"expected_checks_version": "2026-09-04.2", "targets": [
            {"vendor_id": "v001", "url": "https://v001.example.org/",
             "bundle": "A", "corpus_sha256": "test-fixture-only"}]}

    def job(self):
        return {"job_id": "id1", "input": {"url": "https://v001.example.org"},
                "status": "done", "result": {"reliable": True, "network_error_ratio": 0,
                "axes": [{"axis": "visibility", "score": 0}], "evidences": [
                {"requirement_id": "R", "outcome": "pass",
                 "observed": {"checks_version": "2026-09-04.2"}}]}}

    def test_resume_does_not_resubmit(self):
        calls = []
        def api(base, method, path, payload=None):
            calls.append(method)
            return {"job_id": "id1"} if method == "POST" else self.job()
        with tempfile.TemporaryDirectory() as directory:
            run(self.manifest(), directory, transport=api)
            run(self.manifest(), directory, transport=api)
        self.assertEqual(calls, ["POST", "GET"])

    def test_ambiguous_submission_is_not_retried(self):
        calls = []
        def api(*args):
            calls.append(1)
            raise TimeoutError()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(TimeoutError):
                run(self.manifest(), directory, transport=api)
            with self.assertRaises(RuntimeError):
                run(self.manifest(), directory, transport=api)
        self.assertEqual(len(calls), 1)

    def test_poll_failure_resumes_job(self):
        calls = []
        def api(base, method, path, payload=None):
            calls.append(method)
            if method == "POST":
                return {"job_id": "id1"}
            if calls.count("GET") == 1:
                raise TimeoutError()
            return self.job()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(TimeoutError):
                run(self.manifest(), directory, transport=api)
            run(self.manifest(), directory, transport=api)
        self.assertEqual(calls, ["POST", "GET", "GET"])

    def test_incomplete_is_not_reliable_measurement(self):
        job = self.job()
        job["result"]["evidences"][0]["outcome"] = "unverifiable"
        self.assertEqual(measurement(job, "2026-09-04.2")["measurement_status"], "review_required")

    def test_zero_and_missing_are_different(self):
        job = self.job()
        self.assertEqual(measurement(job, "2026-09-04.2")["reasons"], [])
        job["result"]["axes"] = []
        self.assertIn("visibility_score_missing_or_invalid", measurement(job, "2026-09-04.2")["reasons"])

    def test_reject_path_sites(self):
        manifest = self.manifest()
        manifest["targets"][0]["url"] += "v001/"
        with self.assertRaises(ValueError):
            validate_manifest(manifest)

    def test_version_mismatch(self):
        self.assertIn("checks_version_missing_or_mismatched", measurement(self.job(), "different")["reasons"])


if __name__ == "__main__":
    unittest.main()
