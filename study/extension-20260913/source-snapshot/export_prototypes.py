"""Export the same identity under A-D to isolated, user-supplied origins."""
import argparse
from pathlib import Path

from common import digest, read_json, save_json
from corpus import vendor_files
from scan_orchestrator import origin, validate_manifest


def export(corpus, origins, output):
    spec=read_json(Path(corpus)/"spec.json")
    if set(origins) != set("ABCD") or len({origin(u) for u in origins.values()}) != 4:
        raise ValueError("Provide four distinct site roots keyed A/B/C/D")
    output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Use a new empty export directory")
    vendor=spec["identities"][0]
    manifest={"api_base":"https://api.agentabile.dev", "expected_checks_version":"2026-09-04.2",
              "repetitions":3, "purpose":"prototype calibration, same identity across four isolated origins",
              "targets":[]}
    for bundle in "ABCD":
        site=origin(origins[bundle])
        files=vendor_files(vendor,bundle,site)
        for filename,content in files.items():
            path=output/bundle/filename
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8")
        manifest["targets"].append({"vendor_id":"calibration-"+bundle,"url":site,
                                     "bundle":bundle,"corpus_sha256":digest(files)})
    validate_manifest(manifest)
    save_json(output/"scan-manifest.json",manifest)
    return manifest


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("corpus",type=Path)
    parser.add_argument("origins",type=Path,help='JSON object {"A":"https://...",...}')
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    export(args.corpus,read_json(args.origins),args.output)
    print("Prototype files and scan-manifest.json exported; nothing deployed or submitted.")
