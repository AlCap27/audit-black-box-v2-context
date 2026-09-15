"""Normal-model planning sensitivity using completed pilot assignments, not a power gate."""
import json,math
from pathlib import Path
from scipy.stats import nct,t,chi2
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'outputs/audit-black-box-v2/pilot-expanded-20260910'
s=json.loads((C/'SUMMARY.json').read_text())
complete=[r for r in s['assignment_rows'] if r['valid']==24]
sd=s['complete_assignment_sd']
result={'status':'PILOT_INFORMED_NORMAL_SENSITIVITY_ONLY','complete_assignments':len(complete),'observed_sd_complete_only':sd,'warnings':['Small exploratory pilot, fixed corpus and queries.','Complete-assignment selection may depend on missingness.','Normal contrast assumption and top-3 competition require validation before confirmation.','No recommendation to start confirmatory collection automatically.'],'scenarios':[]}
if sd and len(complete)>1:
    df=len(complete)-1
    upper=math.sqrt(df*sd*sd/chi2.ppf(.025,df))
    result['sd_upper_normal_95']=upper
    for scale,label in [(sd,'observed_SD'),(upper,'normal_SD_upper_95')]:
        for effect in [.01,.02,.03]:
            chosen=None
            for n in range(8,513):
                critical=t.ppf(.975,n-1);delta=math.sqrt(n)*effect/scale
                power=float(nct.cdf(-critical,n-1,delta)+nct.sf(critical,n-1,delta))
                if power>=.8:chosen={'assignments':n,'calls_at_24_queries_one_rep':24*n,'normal_model_power':power};break
            result['scenarios'].append({'SD_assumption':label,'SD':scale,'absolute_effect':effect,'first_N_with_power_80':chosen})
(C/'power_followup.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
