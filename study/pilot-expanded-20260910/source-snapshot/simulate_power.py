"""Scenario screening with competitive top-k selection. NOT a validated power guarantee."""
import argparse
from pathlib import Path

from common import save_json


def simulate(seed=42, simulations=200, vendors=32, queries=24, repetitions=5,
             assignments=(4, 8, 16, 32)):
    import numpy as np
    from scipy.stats import t
    if vendors % 4 or vendors < 8 or simulations < 20 or queries < 1 or repetitions < 1:
        raise ValueError("Invalid simulation scale")
    rng = np.random.default_rng(seed)
    results = []
    max_a = max(assignments)
    # Alternatives are log-score shifts, NOT a claimed 0.15 -> 0.35 marginal probability.
    for retrieval_effect, generation_effect in [(0, 0), (.4, 0), (0, .4), (.4, .4)]:
        estimates = {a: [] for a in assignments}
        rejects = {a: [] for a in assignments}
        for sim in range(simulations):
            vendor_latent = rng.normal(0, .7, vendors)
            rank_base = rng.normal(0, 1, (queries, vendors*2))
            rank_base[:, :vendors] += vendor_latent
            # Half the finite query set favors editorial material.
            rank_base[queries//2:, vendors:] += .7
            generator_latent = rng.normal(0, .4, vendors)
            contrasts = []
            for a in range(max_a):
                dose = rng.permutation(np.tile(np.arange(4), vendors//4))
                scores = rank_base.copy()
                scores[:, :vendors] += retrieval_effect*dose
                selected = np.argsort(-scores, axis=1)[:, :5]
                mention_counts = np.zeros(vendors)
                for q in range(queries):
                    candidates = selected[q][selected[q]<vendors]
                    if not len(candidates):
                        continue
                    for rep in range(repetitions):
                        if rng.random() < .1:  # scenario refusal, fixed across treatment
                            continue
                        g = generator_latent[candidates] + generation_effect*dose[candidates]
                        # Stochastic top-three without replacement, competition enforced.
                        g += rng.gumbel(size=len(candidates))
                        chosen = candidates[np.argsort(-g)[:3]]
                        mention_counts[chosen] += 1
                rates = mention_counts/(queries*repetitions)
                contrasts.append(rates[dose==3].mean()-rates[dose==0].mean())
                if a+1 in assignments:
                    n=a+1
                    mean=float(np.mean(contrasts))
                    se=float(np.std(contrasts,ddof=1)/np.sqrt(n))
                    margin=float(t.ppf(.975,n-1))*se
                    estimates[n].append(mean)
                    rejects[n].append(abs(mean)>margin)
            
        for a in assignments:
            rate=float(np.mean(rejects[a]))
            results.append({"retrieval_log_score_step": retrieval_effect,
                            "generation_log_score_step": generation_effect, "assignments": a,
                            "estimated_rejection_rate": rate,
                            "monte_carlo_se": float(np.sqrt(rate*(1-rate)/simulations)),
                            "mean_D_minus_A": float(np.mean(estimates[a])),
                            "interpretation": "type_I_error" if retrieval_effect==generation_effect==0 else "scenario_power"})
    return {"status": "SCENARIO_SCREENING_NOT_CALIBRATED", "seed": seed,
            "simulations_per_scenario": simulations, "vendors": vendors, "queries": queries,
            "repetitions": repetitions, "results": results,
            "limits": ["Stochastic score model is not BM25 or a fitted LLM model.",
                       "Calibrate latent variance/refusal/effect scenarios with an independent real pilot.",
                       "No assurance of power for +20 readiness points; scores are not calibrated.",
                       "Finite fixed corpus/query target; no external population generalization."]}


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--simulations", type=int, default=200)
    args=parser.parse_args()
    result=simulate(simulations=args.simulations)
    save_json(args.output,result)
    print("Scenario results saved:", args.output)
