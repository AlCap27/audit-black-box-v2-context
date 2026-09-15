"""Single-attempt Gemini Batch transport. No polling loop and no automatic retries.
Current prepared gates remain CLOSED. Importing this module does not use network.
"""
import json,re,sys
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent
# Also works after this directory is copied to context-repo/preflight.
BASE=ROOT.parent/'batch-preparation-20260914'
if not BASE.exists():BASE=ROOT.parent/'study/batch-preparation-20260914'
sys.path.insert(0,str(BASE))
from batch_state import admit_shard
from common import directory_lock,save_json
from prepare import MODEL,digest

def batch_payload(data,shard,attempt):
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',attempt):raise ValueError('Invalid attempt identifier')
    rows=[json.loads(l) for l in (data/'requests'/f'{shard}.jsonl').read_text(encoding='utf-8').splitlines()]
    body={'batch':{'displayName':'abbv2-'+attempt,'inputConfig':{'requests':{'requests':[{'request':r['request'],'metadata':{'key':r['key']}} for r in rows]}}}}
    if len(json.dumps(body).encode())>=20_000_000:raise ValueError('Inline batch exceeds20MB')
    return body

def send_once(data,state,shard,attempt,receipt,gates,transport):
    if shard not in ('controls',*[f'main-{i:02}' for i in range(12)]):raise ValueError('Unknown shard')
    if gates.get('repository_handoff_complete') is not True:raise ValueError('Repository handoff required before generation')
    body=batch_payload(data,shard,attempt)
    admit_shard(data,state,shard,attempt,receipt,gates)
    # Budget already persists PREPARED_UNCERTAIN. Any interruption below retains it.
    save_json(state/(attempt+'-request.json'),body)
    try:raw=transport('models/'+MODEL+':batchGenerateContent',body)
    except Exception as e:
        save_json(state/(attempt+'-uncertain.json'),{'error_type':type(e).__name__,'resubmit_allowed':False})
        raise RuntimeError('Submission uncertain; reconcile manually; reservation retained') from None
    save_json(state/(attempt+'-create.json'),raw)
    name=raw.get('name')
    if not isinstance(name,str) or not re.fullmatch(r'batches/[a-zA-Z0-9_-]+',name):
        raise RuntimeError('Unrecognized job name; keep uncertain reservation')
    with directory_lock(state):
        ledger=json.loads((state/'budget.json').read_text(encoding='utf-8'))
        ledger['attempts'][attempt].update(state='ACCEPTED',provider_job=name,payload_sha256=digest(body))
        save_json(state/'budget.json',ledger)
    return name

def http_transport(key):
    def send(path,body=None):
        if not (re.fullmatch(r'models/gemini-3\.1-flash-lite:batchGenerateContent',path) or re.fullmatch(r'batches/[a-zA-Z0-9_-]+',path)):
            raise ValueError('Endpoint outside allowlist')
        req=Request('https://generativelanguage.googleapis.com/v1beta/'+path,data=json.dumps(body).encode() if body is not None else None,headers={'x-goog-api-key':key,'Content-Type':'application/json'})
        with urlopen(req,timeout=60) as r:return json.load(r)
    return send

def normalize_inline(raw):
    # Strictly use provider metadata; no positional association on missing keys.
    output=raw.get('response',raw.get('output',{}))
    rows=output.get('inlinedResponses',{}).get('inlinedResponses',[])
    return [dict({k:v for k,v in r.items() if k!='metadata'},key=r.get('metadata',{}).get('key')) for r in rows]
