"""Single-attempt Gemini Batch transport. No polling loop and no automatic retries.
Current prepared gates remain CLOSED. Importing this module does not use network.
"""
import json,re,sys
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parent
# Also works after this directory is copied to context-repo/preflight.
BASE=ROOT.parent/'batch-preparation-20260914'
if not BASE.exists():BASE=ROOT.parent/'study/batch-preparation-20260914'
sys.path.insert(0,str(BASE))
from prepare import MODEL

def batch_payload(data,shard,attempt):
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',attempt):raise ValueError('Invalid attempt identifier')
    rows=[json.loads(l) for l in (data/'requests'/f'{shard}.jsonl').read_text(encoding='utf-8').splitlines()]
    body={'batch':{'displayName':'abbv2-'+attempt,'inputConfig':{'requests':{'requests':[{'request':r['request'],'metadata':{'key':r['key']}} for r in rows]}}}}
    if len(json.dumps(body).encode())>=20_000_000:raise ValueError('Inline batch exceeds20MB')
    return body

def send_once(data,state,shard,attempt,receipt,gates,transport):
    # Single public submission path. Never trust a caller-supplied controls_pass.
    from orchestration import submit_once
    return submit_once(data,state,shard,attempt,receipt,gates,transport)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ValueError('Provider redirect refused; no automatic follow-up')

def _open(request,timeout):
    return build_opener(NoRedirect()).open(request,timeout=timeout)

def http_transport(key):
    def send(path,body=None):
        parsed=urlsplit(path)
        query=parse_qs(parsed.query,keep_blank_values=True)
        create=path=='models/'+MODEL+':batchGenerateContent'
        cancel=bool(re.fullmatch(r'batches/[a-zA-Z0-9_-]+:cancel',path))
        get=bool(re.fullmatch(r'batches/[a-zA-Z0-9_-]+',path))
        listing=(parsed.path=='batches' and not parsed.scheme and not parsed.netloc
                 and not parsed.fragment and set(query)<= {'pageSize','pageToken'}
                 and all(len(v)==1 for v in query.values())
                 and query.get('pageSize',['100'])[0]=='100')
        if not (create or cancel or get or listing):
            raise ValueError('Endpoint outside allowlist')
        if (create and not isinstance(body,dict)) or (cancel and body!={}) or ((get or listing) and body is not None):
            raise ValueError('Body/method mismatch')
        req=Request('https://generativelanguage.googleapis.com/v1beta/'+path,
                    data=json.dumps(body,allow_nan=False).encode() if body is not None else None,
                    method='POST' if create or cancel else 'GET',
                    headers={'x-goog-api-key':key,'Content-Type':'application/json'})
        with _open(req,timeout=60) as r:return json.load(r)
    return send

def normalize_inline(raw):
    # Strictly use provider metadata; no positional association on missing keys.
    output=raw.get('response',raw.get('output',{}))
    if not isinstance(output,dict) or 'responsesFile' in output:
        raise ValueError('Only documented inline output supported; archive and review')
    container=output.get('inlinedResponses')
    if not isinstance(container,dict) or not isinstance(container.get('inlinedResponses'),list):
        raise ValueError('Missing or malformed inline response envelope')
    rows=container['inlinedResponses']
    result=[]
    for r in rows:
        if not isinstance(r,dict):
            result.append(r)  # Reconciler quarantines malformed records.
            continue
        metadata=r.get('metadata')
        key=metadata.get('key') if isinstance(metadata,dict) else None
        result.append(dict({k:v for k,v in r.items() if k!='metadata'},key=key))
    return result
