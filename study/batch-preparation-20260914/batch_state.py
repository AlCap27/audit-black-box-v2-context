"""Offline admission and reconciliation. Deliberately contains NO submit method.
No credentials, network, automated retry, or release of uncertain reservations.
"""
import argparse, hashlib, json, sys
from decimal import Decimal
from pathlib import Path
from prepare import ROOT, MODEL, dump, digest, sha
from common import directory_lock, save_json
from experiment import parse_answer, response_text

def admit_shard(data, state_dir, shard, attempt, token_receipt, gates):
    """Calculate reservation from exact request hashes, not a caller-supplied cost.
    Receipt must be collected during the separate, authorized live preflight.
    No provisional bytes/token estimate can pass this gate.
    """
    verify(data)
    shards=json.loads((data/'shards.json').read_text(encoding='utf-8'))
    s=next(x for x in shards if x['name']==shard)
    if shard!='controls' and gates.get('controls_pass') is not True:
        raise ValueError('Controls must be reconciled before main shards')
    if token_receipt.get('model')!=MODEL or token_receipt.get('method')!='Google countTokens':
        raise ValueError('Exact provider token count required')
    # Use verified current prices, refusing any increase over this reviewed rate.
    if gates.get('input_price')!=0.125 or gates.get('output_price')!=0.75:
        raise ValueError('Pricing changed: recalculate before admission')
    rows=list(map(json.loads,(data/s['path']).read_text(encoding='utf-8').splitlines()))
    amount=Decimal(0);inputs=0
    for row in rows:
        receipt=token_receipt.get('requests',{}).get(row['key'],{})
        count=receipt.get('tokens')
        if receipt.get('request_sha256')!=digest(row) or type(count) is not int or count<=0:
            raise ValueError('Token receipt missing or hash mismatch')
        inputs+=count
        amount+=(Decimal(count)*Decimal('.125')+Decimal(1200)*Decimal('.75'))/Decimal(1000000)
    available=gates.get('available_batch_tokens')
    if type(available) is not int or inputs>available:
        raise ValueError('Insufficient verified enqueued-token capacity')
    # Reserve extra 20% for billing rounding/uncertainty, never assume free credits.
    return reserve(state_dir,attempt,s['keys'],amount*Decimal('1.20'),gates)

def verify(data):
    manifest=json.loads((data/'manifest.json').read_text(encoding='utf-8'))
    for name,expected in manifest.items():
        p=(data/name).resolve()
        if not p.is_relative_to(data.resolve()) or sha(p)!=expected:
            raise ValueError('Manifest mismatch: '+name)
    return len(manifest)

def reserve(state_dir, attempt, keys, amount, gates):
    """Durable PREPARED_UNCERTAIN reservation BEFORE a future external submission.
    A lost connection leaves this reservation in place; never infer nonacceptance.
    This is a conservative admission primitive, NOT a cloud billing cap.
    """
    required=('protocol_frozen','launch_authorized','model_project_verified',
              'batch_quota_verified','token_count_verified','output_cap_verified',
              'price_current','billing_decision_recorded','retention_plan_confirmed')
    if any(gates.get(k) is not True for k in required): raise ValueError('Launch gates closed')
    if gates.get('model')!=MODEL: raise ValueError('No model fallback')
    amount=Decimal(str(amount))
    if not amount.is_finite() or amount<=0 or not keys or len(keys)!=len(set(keys)):
        raise ValueError('Invalid reservation')
    with directory_lock(state_dir):
        p=Path(state_dir)/'budget.json'
        s=json.loads(p.read_text()) if p.exists() else {'cap':'30','attempts':{}}
        if attempt in s['attempts']: raise ValueError('Attempt already recorded')
        used={k for a in s['attempts'].values() for k in a['keys']}
        if used.intersection(keys): raise ValueError('Request already reserved; manual reconciliation required')
        committed=sum((Decimal(a['reserved_usd']) for a in s['attempts'].values()),Decimal(0))
        if committed+amount>Decimal('30'): raise ValueError('USD30 global cap exceeded')
        s['attempts'][attempt]={'keys':keys,'reserved_usd':str(amount),'state':'PREPARED_UNCERTAIN','provider_job':None}
        save_json(p,s)
    return s

def reconcile(expected, records, traces, identities, terminal=False, allowed_version=None):
    """Key-based, order invariant. Conflicting duplicates never pick a winner."""
    expected=set(expected); grouped={}; quarantine=[]
    for i,r in enumerate(records):
        if not isinstance(r,dict) or not isinstance(r.get('key'),str) or r.get('key') not in expected:
            quarantine.append({'record':i,'reason':'unknown_or_missing_key','raw':r}); continue
        grouped.setdefault(r['key'],[]).append(r)
    result={};versions=set()
    for key in sorted(expected):
        rows=grouped.get(key,[])
        if not rows:
            result[key]={'status':'missing_terminal' if terminal else 'pending','resubmit_allowed':False};continue
        unique={digest(r):r for r in rows}
        if len(unique)>1:
            result[key]={'status':'conflicting_duplicate','copies':len(rows),'resubmit_allowed':False};continue
        r=next(iter(unique.values())); rec={'copies':len(rows),'resubmit_allowed':False}
        if 'error' in r or 'status' in r or ('response' in r and 'error' in r):
            rec.update(status='provider_error',raw=r)
        elif not isinstance(r.get('response'),dict): rec.update(status='malformed_response',raw=r)
        else:
            raw=r['response'];version=raw.get('modelVersion'); rec['model_version']=version
            if isinstance(version,str): versions.add(version)
            try:
                parsed=parse_answer(response_text(raw,'gemini'),traces[key]['shown'],identities)
                rec.update(status='valid',answer=parsed,usage=raw.get('usageMetadata'))
                if allowed_version is not None and version!=allowed_version: rec['status']='version_mismatch'
                if traces[key]['role']=='control':
                    t=traces[key]
                    rec['control_pass']=(parsed['decision']==t['expected_decision'] and not parsed['unknown_names'] and not parsed['unsupported_recommendations'] and (t['expected_vendor'] is None or parsed['recommended']==[t['expected_vendor']]))
            except (ValueError,TypeError,KeyError,IndexError,AttributeError) as e: rec.update(status='invalid_output',reason=str(e),raw=r)
        result[key]=rec
    controls=[x for k,x in result.items() if traces[k]['role']=='control']
    issues=bool(quarantine) or len(versions)>1 or any(x['status']!='valid' or x.get('control_pass') is False for x in result.values())
    return {'records':result,'quarantine':quarantine,'versions':sorted(versions),'stop_future_submissions':issues,'controls_pass':len(controls)==24 and all(x.get('control_pass') is True for x in controls),'automatic_resubmission':False,'terminal':terminal,'billing_reconciled':False}

def import_file(data,rawfile,out,shard,terminal=False,version=None):
    verify(data)
    if out.exists(): raise ValueError('New import output directory required')
    shards=json.loads((data/'shards.json').read_text(encoding='utf-8'))
    selected=next((x for x in shards if x['name']==shard),None)
    if selected is None: raise ValueError('Unknown shard')
    traces={t['key']:t for t in map(json.loads,(data/'traces.jsonl').read_text(encoding='utf-8').splitlines())}
    identities=json.loads((data/'design.json').read_text(encoding='utf-8'))['identities']
    records=[]; malformed=[]
    for i,l in enumerate(rawfile.read_text(encoding='utf-8-sig').splitlines(),1):
        try: records.append(json.loads(l))
        except ValueError: malformed.append({'line':i,'raw':l})
    report=reconcile(selected['keys'],records,traces,identities,terminal,version)
    report['malformed_lines']=malformed
    if malformed: report['stop_future_submissions']=True
    report['input_sha256']=sha(rawfile);report['expected_shard_sha256']=selected['sha256']
    out.mkdir(parents=True);(out/'raw.jsonl').write_bytes(rawfile.read_bytes());dump(out/'reconciliation.json',report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('rawfile',type=Path);p.add_argument('out',type=Path);p.add_argument('--shard',required=True);p.add_argument('--terminal',action='store_true');p.add_argument('--version')
    a=p.parse_args(); r=import_file(a.data,a.rawfile,a.out,a.shard,a.terminal,a.version)
    print(json.dumps({'stop_future_submissions':r['stop_future_submissions'],'versions':r['versions'],'records':len(r['records'])}))
