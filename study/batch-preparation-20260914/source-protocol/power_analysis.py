"""Offline planning only. Reads sealed pilots; no keys/network/generation."""
import sys, math, hashlib, json, statistics
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.stats import t, nct, norm, chi2
from scipy.integrate import quad
P=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from common import read_json,save_json

def tpower(n,delta,sd,alpha):
    critical=t.ppf(1-alpha/2,n-1);nc=delta*math.sqrt(n)/sd
    value=float(nct.sf(critical,n-1,nc)+nct.cdf(-critical,n-1,nc))
    if not math.isfinite(value):
        # Independent integral of (Z+nc)/sqrt(V/df), for numerical tail failures.
        def integrand(u):
            cutoff=critical*math.sqrt(chi2.ppf(u,n-1)/(n-1))
            return norm.sf(cutoff-nc)+norm.cdf(-cutoff-nc)
        value=quad(integrand,0,1,epsabs=1e-9,limit=150)[0]
    return value

def required_n(delta,sd,alpha,target):
    lo,hi=2,4
    while tpower(hi,delta,sd,alpha)<target:hi*=2
    while lo<hi:
        mid=(lo+hi)//2
        if tpower(mid,delta,sd,alpha)>=target:hi=mid
        else:lo=mid+1
    return lo

def guaranteed_n(delta,alpha,target,span=.375):
    # Hoeffding test |mean| > span sqrt(log(2/alpha)/(2n)).
    # Power bound for |E mean| >= delta; independent bounded contrasts.
    return math.ceil(span**2*(math.sqrt(math.log(2/alpha))+math.sqrt(math.log(1/(1-target))))**2/(2*delta**2))

def collect():
    clusters=[]; token_counts=[]; observations=[]; verified={}
    for name in ['pilot-expanded-20260910','extension-20260913']:
        c=P/name;seal=read_json(c/'sha256.json')
        for f,h in seal.items():assert hashlib.sha256((c/f).read_bytes()).hexdigest()==h
        verified[name]=len(seal)
        spec=read_json(c/'run/run.json')['spec']
        for a in spec['assignments']:
            counts=np.zeros((4,3),dtype=int)
            for q in spec['queries']:
                r=read_json(c/'run/responses'/f"{a['assignment_id']}-{q['query_id']}-r000.json")
                assert r['status']=='valid'
                tr=read_json(c/'run/retrieval'/f"{a['assignment_id']}-{q['query_id']}.json")
                retrieved={ch['vendor_id'] for ch in tr['retrieved'] if ch['vendor_id']}
                recommended=set(r['parsed']['recommended'])
                token_counts.append(r['raw_response']['usageMetadata']['totalTokenCount'])
                for v in spec['identities']:
                    j='ABCD'.index(a['bundles'][v['vendor_id']]);z=v['vendor_id'] in retrieved;y=v['vendor_id'] in recommended
                    counts[j]+=[z,y,z and y]
                    observations.append({'assignment':a['assignment_id'],'intent':q['intent'],'template':v['template'],'bundle':'ABCD'[j],'retrieved':int(z),'recommended':int(y)})
            clusters.append(counts)
    x=np.array(clusters,dtype=float); denom=192
    totals=x.sum(axis=0);baseline={b:{'opportunities':len(x)*denom,'retrieved':int(totals[j,0]),'recommended':int(totals[j,1]),'p_retrieval':totals[j,0]/(len(x)*denom),'p_total':totals[j,1]/(len(x)*denom),'p_conditional':totals[j,2]/totals[j,0] if totals[j,0] else None} for j,b in enumerate('ABCD')}
    # Pilot D-A is variance proxy only; it is not the new factorial main effect.
    proxies={'total':(x[:,3,1]-x[:,0,1])/denom,'retrieval':(x[:,3,0]-x[:,0,0])/denom}
    mu=x[:,:,0].mean(axis=0);ratio=totals[:,2]/totals[:,0]
    proxies['conditional']=(x[:,3,2]-ratio[3]*x[:,3,0])/mu[3]-(x[:,0,2]-ratio[0]*x[:,0,0])/mu[0]
    grouping={}
    for key in ['intent','template']:
        grouping[key]={}
        for val in sorted({r[key] for r in observations},key=str):
            rr=[r for r in observations if r[key]==val]
            grouping[key][str(val)]={'n':len(rr),'retrieval':sum(r['retrieved'] for r in rr)/len(rr),'total':sum(r['recommended'] for r in rr)/len(rr)}
    return x,proxies,{'verified_seals':verified,'baseline':baseline,'grouping':grouping,'mean_total_tokens_per_call':statistics.mean(token_counts),'pilot_assignments':20,'pilot_calls':480,'variance_note':'Pilot D-A contrasts or conditional ratio influence functions, not observed new-factorial effects; conditional C has only two retrieved observations.'}

def simulate(vector,n,delta,alpha,kind,multiplier=1,reps=10000):
    rng=np.random.default_rng(20260914+n+int(delta*10000)+int(alpha*1e6))
    centered=vector-vector.mean();sd=vector.std(ddof=1);counts=[0,0]
    for start in range(0,reps,250):
        size=min(250,reps-start)
        if kind=='empirical':sample=rng.choice(centered,(size,n))*multiplier
        elif kind=='normal':sample=rng.normal(0,sd,(size,n))*multiplier
        else:sample=rng.standard_t(5,(size,n))*sd*math.sqrt(3/5)*multiplier
        se=sample.std(axis=1,ddof=1)/math.sqrt(n);critical=t.ppf(1-alpha/2,n-1)
        for k,shift in enumerate([0,delta]):counts[k]+=int(np.sum(np.abs(sample.mean(axis=1)+shift)>critical*se))
    return {'n':n,'delta':delta,'alpha':alpha,'kind':kind,'sd_multiplier':multiplier,'simulations':reps,'null_rejection':counts[0]/reps,'power':counts[1]/reps,'null_mcse':math.sqrt((counts[0]/reps)*(1-counts[0]/reps)/reps),'power_mcse':math.sqrt((counts[1]/reps)*(1-counts[1]/reps)/reps),'scope':'cluster-contrast scenario; conditional uses linearized ratio; not full new-pipeline validation'}

def main():
    x,proxies,metadata=collect();rows=[];guarantees=[]
    for endpoint,vector in proxies.items():
        sd=float(vector.std(ddof=1));alpha=.025 if endpoint=='total' else .025/8
        for delta in [.02,.05,.10]:
            for multiplier in [1,1.5,2]:
                for target in [.8,.9]:
                    n=required_n(delta,sd*multiplier,alpha,target)
                    practical=max(40,n)
                    rows.append({'endpoint':endpoint,'delta':delta,'alpha':alpha,'target_power':target,'pilot_proxy_sd':sd,'sd_multiplier':multiplier,'n_normal_theory':n,'n_with_minimum_40':practical,'power_at_proposed_n':tpower(practical,delta,sd*multiplier,alpha),'queries':24,'conditions':8,'vendors':32,'repetitions':1,'calls_if_recommendation':practical*24,'calls_retrieval_only':0,'index_snapshots':practical,'minimum_40_note':'Prespecified planning safeguard, not evidence of calibrated coverage'})
    for endpoint,alpha in [('total',.025),('retrieval',.025/8)]:
        for delta in [.02,.05,.10]:
            for target in [.8,.9]:
                n=guaranteed_n(delta,alpha,target,span=.375 if endpoint=='total' else .625)
                guarantees.append({'endpoint':endpoint,'delta':delta,'alpha':alpha,'target_power_lower_bound':target,'n':n,'calls':24*n if endpoint=='total' else 0,'offline_query_retrievals':24*n,'support_span':.375 if endpoint=='total' else .625})
    sims=[]
    for endpoint,v in proxies.items():
        alpha=.025 if endpoint=='total' else .025/8
        n=max(40,required_n(.05,float(v.std(ddof=1))*2,alpha,.8))
        for kind in ['normal','empirical','student_t5']:
            sims.append({'endpoint':endpoint,**simulate(v,n,.05,alpha,kind,2)})
    metadata['proxy_sds']={k:float(v.std(ddof=1)) for k,v in proxies.items()}
    metadata['proxy_covariance_total_retrieval']=np.cov(proxies['total'],proxies['retrieval']).tolist()
    result={'metadata':metadata,'planning':rows,'bounded_guarantees':guarantees,'simulations':sims,'assumptions':['Independent assignment clusters; fixed queries and identities; no guarantee against temporal dependence','New factorial cell llms-only absent in pilot; proxy variances and multipliers are scenarios, not estimates for that cell','48 or 72 calls per assignment for 2 or 3 generation repetitions; no assumed variance reduction without within-cell repetition data','20 pilot assignments are not included in confirmatory n; all allocations must be approved','No p-value or observed effect used to select delta; 5 pp retained as requested']}
    save_json(OUT/'power-results.json',result)
    print(json.dumps({'metadata':metadata,'guarantees':guarantees,'simulations':sims},ensure_ascii=False))
if __name__=='__main__':main()
