"""Agentabile scan client. Standard library only; see README.md for scope."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit, quote
from urllib.request import Request, urlopen

SOURCE_REVISION = "3ed4163a929525f514638effe83e4e156a2d798a"


def origin(url):
    parts = urlsplit(url)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.path not in ("", "/")
            or parts.query or parts.fragment):
        raise ValueError("Scan targets must be HTTP(S) site roots, without credentials")
    port = parts.port
    host = parts.hostname.lower()
    if ":" in host:
        host = "[" + host + "]"
    if port and port != (443 if parts.scheme == "https" else 80):
        host += f":{port}"
    return f"{parts.scheme}://{host}"


def validate_manifest(manifest):
    targets = manifest["targets"]
    if not targets:
        raise ValueError("No targets")
    ids, sites = set(), set()
    for target in targets:
        site = origin(target["url"])
        if target["vendor_id"] in ids or site in sites:
            raise ValueError("Duplicate vendor or site origin")
        ids.add(target["vendor_id"])
        sites.add(site)
        if not target.get("corpus_sha256") or not target.get("bundle"):
            raise ValueError("Each target requires corpus_sha256 and bundle")
    if not isinstance(manifest.get("repetitions", 1), int) or manifest.get("repetitions", 1) < 1:
        raise ValueError("repetitions must be positive")
    if not manifest.get("expected_checks_version"):
        raise ValueError("Freeze expected_checks_version before scanning")


def measurement(job, expected_version):
    """Keep score and acquisition quality separate; never convert missing into zero."""
    result = job.get("result") or {}
    evidence = result.get("evidences") or []
    versions = sorted({e.get("observed", {}).get("checks_version")
                       for e in evidence if e.get("observed", {}).get("checks_version")})
    missing_versions = sum(not e.get("observed", {}).get("checks_version") for e in evidence)
    unknown = [e.get("requirement_id") for e in evidence
               if e.get("outcome") in ("unverifiable", "not_checked")]
    scores = {a["axis"]: a.get("score") for a in result.get("axes", [])}
    score = scores.get("visibility")
    valid_score = (isinstance(score, (int, float)) and not isinstance(score, bool)
                   and math.isfinite(score) and 0 <= score <= 100)
    reasons = []
    if job.get("status") != "done":
        reasons.append("job_not_done")
    if result.get("reliable") is not True:
        reasons.append("network_reliability_not_confirmed")
    if not evidence or versions != [expected_version] or missing_versions:
        reasons.append("checks_version_missing_or_mismatched")
    if not valid_score:
        reasons.append("visibility_score_missing_or_invalid")
    return dict(scores=scores, network_reliable=result.get("reliable"),
                network_error_ratio=result.get("network_error_ratio"),
                checks_versions=versions, missing_versions=missing_versions,
                incomplete_requirements=unknown, pages_fetched=result.get("pages_fetched"),
                measurement_status="review_required" if reasons or unknown else "ready_for_review",
                reasons=reasons, coverage_confirmed=False)


def atomic_json(path, value):
    temp = path.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def request_json(base, method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(base + path, data=data, method=method,
                  headers={"Content-Type": "application/json", "User-Agent": "AuditBlackBoxV2/0.1"})
    with urlopen(req, timeout=30) as response:
        return json.load(response)


def run(manifest, state_dir, max_submissions=4, poll_seconds=5, deadline_seconds=180,
        transport=request_json):
    validate_manifest(manifest)
    if max_submissions < 1 or poll_seconds <= 0 or deadline_seconds <= 0:
        raise ValueError("Budget and timing must be positive")
    base = origin(manifest.get("api_base", "https://api.agentabile.dev"))
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    # Exclusive process lock: interrupted process may require manual stale-lock removal.
    lock = state_dir / "runner.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        state_path = state_dir / "state.json"
        digest = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {
            "manifest_sha256": digest, "manifest": manifest, "source_revision": SOURCE_REVISION,
            "source_revision_is_deployment_attestation": False, "submissions": 0, "scans": {}}
        if state["manifest_sha256"] != digest:
            raise ValueError("Manifest changed: use a new state directory")
        save = lambda: atomic_json(state_path, state)
        for target in manifest["targets"]:
            for repetition in range(manifest.get("repetitions", 1)):
                key = f"{target['vendor_id']}:{repetition}"
                record = state["scans"].get(key)
                if record and record["status"] in ("done", "error"):
                    continue
                if record and not record.get("job_id"):
                    raise RuntimeError("Submission unresolved; reconcile with server before retrying")
                if record is None:
                    if state["submissions"] >= max_submissions:
                        raise RuntimeError("Persistent submission budget reached")
                    record = {"target": target, "repetition": repetition,
                              "status": "submission_pending", "events": []}
                    state["scans"][key] = record
                    state["submissions"] += 1
                    save()  # A crash or ambiguous POST must never silently submit twice.
                    try:
                        response = transport(base, "POST", "/v1/jobs",
                                             {"type": "scan", "input": {"url": origin(target["url"])}})
                        record["job_id"] = response["job_id"]
                        record["status"] = "queued"
                        record["submission_response"] = response
                        save()
                    except Exception as exc:
                        record["status"] = "submission_unresolved"
                        record["submission_error_type"] = type(exc).__name__
                        save()
                        raise
                deadline = time.monotonic() + deadline_seconds
                while time.monotonic() < deadline:
                    job = transport(base, "GET", "/v1/jobs/" + quote(record["job_id"], safe=""))
                    if job.get("job_id") != record["job_id"] or origin(job["input"]["url"]) != origin(target["url"]):
                        raise ValueError("Job identity/target mismatch")
                    status = job.get("status")
                    if status not in ("queued", "running", "done", "error"):
                        raise ValueError("Unknown job status")
                    record["events"].append({"received_at": time.time(), "payload": job})
                    record["status"] = status
                    if status in ("done", "error"):
                        record["measurement"] = measurement(job, manifest["expected_checks_version"])
                    save()
                    if status in ("done", "error"):
                        break
                    time.sleep(poll_seconds)
                else:
                    raise TimeoutError("Polling deadline reached: rerun to resume the same job")
        return state
    finally:
        lock.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state-dir", type=Path, default=Path("scan-state"))
    parser.add_argument("--max-submissions", type=int, default=4)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    validate_manifest(config)
    if args.execute:
        result = run(config, args.state_dir, args.max_submissions)
        print(json.dumps({"submissions": result["submissions"], "records": len(result["scans"])}))
    else:
        print("Manifest valid. No network calls. Add --execute to submit scans.")
