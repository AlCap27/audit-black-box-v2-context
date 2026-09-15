import json
from pathlib import Path
import numpy as np
from scipy.stats import t
C=Path(__file__).resolve().parents[1]/'outputs/audit-black-box-v2/pilot-expanded-20260910'
analysis=json.loads((C/'run/analysis.json').read_text())
x=np.array(analysis['D_minus_A_complete_assignment_contrasts'])
assert len(x)==8
centered=x-x.mean();rng=np.random.default_rng(20260913);rows=[]
for n in [8,23,32,64,88]:
    samples=rng.choice(centered,size=(10000,n),replace=True)
    means=samples.mean(axis=1);se=samples.std(axis=1,ddof=1)/np.sqrt(n)
    critical=t.ppf(.975,n-1)
    for effect in [0,.02]:
        rate=float(np.mean(np.abs(means+effect)>critical*se))
        rows.append({'assignments':n,'assumed_additive_effect':effect,'rejection_rate':rate,'monte_carlo_se':float(np.sqrt(rate*(1-rate)/10000))})
r={'status':'EMPIRICAL_SHAPE_SENSITIVITY_NOT_VALIDATED_GENERATIVE_MODEL','simulations_per_scenario':10000,'seed':20260913,'source':'Eight observed assignment contrasts centered to zero; resampling with replacement; alternative is additive +.02.','limits':['Only eight empirical contrasts, unknown tail shape.','Resampling preserves observed between-assignment shape, but additive alternative is not a mechanistic model of retrieval or top-3 competition.','Not sufficient alone to pass confirmatory power gate.'],'rows':rows}
(C/'bootstrap_sensitivity.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps(r))
