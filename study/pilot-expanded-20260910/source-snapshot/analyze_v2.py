"""Complete-denominator audit tables, conditional-corpus inference and optional A2."""
import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path
import statistics

from common import digest, read_json, save_json
from experiment import literal_names


def analyze(directory):
    directory = Path(directory)
    manifest = read_json(directory/"run.json")
    spec = manifest["spec"]
    if digest(spec) != manifest["spec_sha256"]:
        raise ValueError("Run manifest spec hash mismatch")
    responses = {p.stem: read_json(p) for p in (directory/"responses").glob("*.json")}
    rows, retrieval_rows = [], []
    for assignment in spec["assignments"]:
        aid = assignment["assignment_id"]
        for query in spec["queries"]:
            qid = query["query_id"]
            trace = read_json(directory/"retrieval"/f"{aid}-{qid}.json")
            retrieved = {c["vendor_id"] for c in trace["retrieved"] if c["vendor_id"]}
            exposed = {vid for c in trace["shown"] for vid in literal_names(c["shown_text"], spec["identities"])}
            for vendor in spec["identities"]:
                vid = vendor["vendor_id"]
                base = {"assignment_id": aid, "query_id": qid, "intent": query["intent"],
                        "vendor_id": vid, "bundle": assignment["bundles"][vid],
                        "retrieved": int(vid in retrieved), "name_in_context": int(vid in exposed)}
                retrieval_rows.append(base)
                for repetition in range(spec["repetitions"]):
                    rid = f"{aid}-{qid}-r{repetition:03}"
                    record = responses.get(rid)
                    if record and record["trace_sha256"] != digest(trace):
                        raise ValueError("Response/trace hash mismatch")
                    valid = record and record["status"] == "valid"
                    parsed = record["parsed"] if valid else {}
                    rows.append(dict(base, request_id=rid, repetition=repetition,
                        status=record["status"] if record else "not_run",
                        recommended=int(vid in parsed["recommended"]) if valid else None,
                        literal_mention=int(vid in parsed["literal_mentions"]) if valid else None,
                        abstained=int(parsed["decision"] == "abstain") if valid else None,
                        leakage=int(vid in parsed["recommended"] and vid not in exposed) if valid else None))
    for filename, table in [("vendor_responses.csv", rows), ("retrieval_units.csv", retrieval_rows)]:
        with (directory/filename).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
    bundles = {}
    for bundle in "ABCD":
        r = [x for x in retrieval_rows if x["bundle"] == bundle]
        valid = [x for x in rows if x["bundle"] == bundle and x["status"] == "valid"]
        conditioned = [x for x in valid if x["name_in_context"]]
        bundles[bundle] = {
            "retrieval_units": len(r), "p_retrieved": statistics.mean(x["retrieved"] for x in r),
            "p_name_in_context": statistics.mean(x["name_in_context"] for x in r),
            "valid_vendor_response_units": len(valid),
            "p_recommended_valid_responses_only": statistics.mean(x["recommended"] for x in valid) if valid else None,
            "p_recommended_given_name_in_context_descriptive": statistics.mean(x["recommended"] for x in conditioned) if conditioned else None}
    counts = Counter(x["status"] for x in responses.values())
    planned = len(spec["assignments"])*len(spec["queries"])*spec["repetitions"]
    counts["not_run"] = planned-len(responses)
    valid_responses = [r for r in responses.values() if r["status"] == "valid"]
    versions = sorted({r.get("raw_response", {}).get("modelVersion", "missing") for r in responses.values()})
    contrasts = []
    for aid in [a["assignment_id"] for a in spec["assignments"]]:
        r = [x for x in rows if x["assignment_id"] == aid]
        if all(x["status"] == "valid" for x in r):
            contrasts.append(statistics.mean(x["recommended"] for x in r if x["bundle"] == "D") -
                             statistics.mean(x["recommended"] for x in r if x["bundle"] == "A"))
    interval = None
    # Assignment-level repeated randomization; conditional on THIS finite corpus and query set.
    # Do not report an interval if missing data, mixed versions, synthetic outputs or <8 assignments.
    if not manifest["synthetic_generation"] and len(versions)==1 and len(contrasts)==len(spec["assignments"]) and len(contrasts)>=8:
        from scipy.stats import t
        mean = statistics.mean(contrasts)
        margin = t.ppf(.975, len(contrasts)-1)*statistics.stdev(contrasts)/(len(contrasts)**.5)
        interval = {"estimate": mean, "lower": mean-margin, "upper": mean+margin,
                    "method": "exploratory t interval over independent balanced assignments",
                    "scope": "fixed identities and fixed query set; no population or natural mediation claim"}
    result = {"synthetic_generation": manifest["synthetic_generation"], "response_statuses": dict(counts),
              "resolved_model_versions": versions, "bundles": bundles,
              "D_minus_A_complete_assignment_contrasts": contrasts,
              "D_minus_A_interval": interval,
              "valid_response_abstentions": sum(r["parsed"]["decision"]=="abstain" for r in valid_responses),
              "responses_with_unsupported_recommendations": sum(bool(r["parsed"]["unsupported_recommendations"]) for r in valid_responses),
              "responses_with_unknown_names": sum(bool(r["parsed"]["unknown_names"]) for r in valid_responses),
              "leakage_recommendations": sum(x["leakage"] or 0 for x in rows),
              "inference_note": "Retrieval is counted once per assignment-query-vendor; API/parse failures are missing, not zero."}
    save_json(directory/"analysis.json", result)
    label = "DEMO: generazione sintetica, nessuna evidenza sul comportamento di un LLM" if manifest["synthetic_generation"] else "Esperimento con generatore API"
    lines = ["# Audit Black Box V2", "", label, "", "| Bundle | P(recuperato) | P(nome nel contesto) | P(raccomandato), risposte valide |",
             "|---|---:|---:|---:|"]
    for b, stats in bundles.items():
        p = stats["p_recommended_valid_responses_only"]
        lines.append(f"| {b} | {stats['p_retrieved']:.3f} | {stats['p_name_in_context']:.3f} | {p if p is not None else 'NA'} |")
    lines += ["", f"Stati risposte: {dict(counts)}.", "",
              "Il retrieval è realmente eseguito sul corpus artificiale. La sitemap non interviene nella scoperta: tutti i file sono caricati da manifest.",
              "I punteggi Agentabile non sono ancora calibrati. I bundle non equivalgono a dosi 20/40/60/80.",
              "Le probabilità condizionate sono descrittive; non quantificano mediazione causale."]
    (directory/"report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return result


def hierarchical(directory, draws=1000, tune=1000, chains=4):
    """Secondary descriptive crossed-effects logistic model; not a mediation estimator."""
    import numpy as np
    import pymc as pm
    import arviz as az
    directory = Path(directory)
    manifest = read_json(directory/"run.json")
    if manifest["synthetic_generation"]:
        raise ValueError("Refuse inferential fit on fixture-generated answers")
    with (directory/"vendor_responses.csv").open(encoding="utf-8") as stream:
        data = list(csv.DictReader(stream))
    data = [r for r in data if r["status"] == "valid"]
    if not data:
        raise ValueError("No valid responses")
    coord_names = ["vendor_id", "query_id", "assignment_id", "request_id"]
    levels = {c: sorted({r[c] for r in data}) for c in coord_names}
    idx = {c: np.array([levels[c].index(r[c]) for r in data]) for c in coord_names}
    bundle_idx = np.array(["ABCD".index(r["bundle"]) for r in data])
    observed = np.array([int(r["recommended"]) for r in data])
    with pm.Model(coords={**levels, "contrast": ["B-A", "C-A", "D-A"]}) as model:
        intercept = pm.Normal("intercept", -3, 1.5)
        beta = pm.Normal("bundle_log_odds", 0, 1, dims="contrast")
        effects = pm.math.concatenate([pm.math.zeros(1), beta])
        eta = intercept + effects[bundle_idx]
        for name in coord_names:
            sd = pm.HalfNormal(name+"_sd", 1)
            z = pm.Normal(name+"_z", 0, 1, dims=name)
            eta = eta + sd*z[idx[name]]
        pm.Bernoulli("recommended", logit_p=eta, observed=observed)
        prior = pm.sample_prior_predictive(samples=200, random_seed=42)
        trace = pm.sample(draws=draws, tune=tune, chains=chains, cores=1, target_accept=.95,
                          random_seed=42, return_inferencedata=True)
        pm.sample_posterior_predictive(trace, extend_inferencedata=True, random_seed=42)
    trace.extend(prior)
    trace.to_netcdf(directory/"hierarchical.nc")
    summary = az.summary(trace, var_names=["intercept", "bundle_log_odds"])
    summary.to_csv(directory/"hierarchical_summary.csv")
    draws_beta = trace.posterior["bundle_log_odds"].values.reshape(-1,3)
    save_json(directory/"hierarchical_intervals.json", {"central_95_log_odds": np.quantile(draws_beta,[.025,.5,.975],axis=0).tolist(),
        "note": "Secondary association model. Shared intercepts do not enforce top-3 competition; inspect posterior predictive diagnostics. No mediation percentage."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--hierarchical", action="store_true")
    args = parser.parse_args()
    result = analyze(args.run)
    print("Analysis saved. Synthetic generation:", result["synthetic_generation"])
    if args.hierarchical:
        hierarchical(args.run)
