import sys,os,json,time,argparse
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/audit-black-box-v2'
sys.path.insert(0,str(PROJECT))
import experiment
from corpus import build
from common import save_json,read_json,digest,directory_lock
from analyze_v2 import analyze
CAMPAIGN=PROJECT/'pilot-expanded-20260910'
MODEL='gemini-3.1-flash-lite'
SYSTEM='Rispondi sulla base delle tue conoscenze, senza strumenti web. Non inventare informazioni. Dichiara esplicitamente se non conosci il nome richiesto. Rispondi solo con JSON: {"known":true oppure false,"description":"breve descrizione oppure stringa vuota","sources":["URL se realmente noto"]}.'
last=0
def throttle():
    global last
    time.sleep(max(0,5-(time.monotonic()-last)))
    last=time.monotonic()
def request(payload):
    throttle()
    req=Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','x-goog-api-key':os.environ['GEMINI_API_KEY']})
    with urlopen(req,timeout=90) as response:return json.load(response)
def probes():
    spec=read_json(PROJECT/'design/next-pilot-spec-PROPOSED.json')
    out=CAMPAIGN/'probes'
    with directory_lock(out):
        ledger_path=out/'ledger.json'
        ledger=read_json(ledger_path) if ledger_path.exists() else {'attempts':0,'records':{}}
        if 'pending' in ledger['records'].values():raise RuntimeError('Pending probe requires reconciliation')
        for vendor in spec['identities']:
            vid=vendor['vendor_id']
            if vid in ledger['records']:continue
            if ledger['attempts']>=32:break
            payload={'systemInstruction':{'parts':[{'text':SYSTEM}]},'contents':[{'role':'user','parts':[{'text':f"Conosci un venditore chiamato {vendor['name']}? Se sì, indica soltanto ciò che sai e le eventuali fonti note. Se no, dichiaralo."}]}],'generationConfig':{'temperature':0,'maxOutputTokens':256,'responseMimeType':'application/json'}}
            ledger['attempts']+=1;ledger['records'][vid]='pending';save_json(ledger_path,ledger)
            r={'vendor_id':vid,'name':vendor['name'],'request':payload,'started_at':time.time(),'status':'api_error'}
            try:
                r['raw_response']=request(payload)
                r['status']='invalid_response'
                text=experiment.response_text(r['raw_response'],'gemini');r['text']=text
                parsed=json.loads(text)
                assert set(parsed)=={'known','description','sources'} and type(parsed['known']) is bool and isinstance(parsed['description'],str) and isinstance(parsed['sources'],list) and all(isinstance(s,str) for s in parsed['sources'])
                r['parsed']=parsed;r['status']='valid'
            except HTTPError as e:r['http_status']=e.code
            except Exception as e:r['error_type']=type(e).__name__
            r['finished_at']=time.time();save_json(out/(vid+'.json'),r)
            ledger['records'][vid]=r['status'];save_json(ledger_path,ledger)
            print(json.dumps({'phase':'probes','attempts':ledger['attempts'],'status':r['status'],'known':r.get('parsed',{}).get('known')}),flush=True)
            if r['status']!='valid':break
def pilot():
    gate=read_json(CAMPAIGN/'probe_review.json')
    if not gate['proceed']:raise RuntimeError('Probe review unresolved')
    spec=read_json(PROJECT/'design/next-pilot-spec-PROPOSED.json')
    corpus=CAMPAIGN/'corpus';out=CAMPAIGN/'run'
    if not corpus.exists():build(corpus,spec)
    cfg=experiment.default_config('gemini')
    # One fully validated immutable corpus snapshot for this single process.
    prepared=experiment.prepare(corpus,cfg)
    experiment.prepare=lambda c,config:prepared
    ledger=read_json(out/'ledger.json') if (out/'ledger.json').exists() else {'attempts':0,'records':{}}
    before=sum(v!='valid' for v in ledger['records'].values())
    def generate(trace,identities):
        throttle()
        try:return experiment.gemini_response(trace,MODEL,cfg['temperature'],cfg['max_output_tokens'])
        except HTTPError as e:
            save_json(CAMPAIGN/'last_http_error.json',{'status':e.code,'time':time.time()})
            raise
    for limit in range(ledger['attempts']+1,193):
        summary=experiment.execute(corpus,out,cfg,max_calls=limit,generator=generate)
        print(json.dumps({'phase':'pilot',**summary}),flush=True)
        if sum(v for k,v in summary['statuses'].items() if k!='valid')>before:break
    analyze(out)
if __name__=='__main__':
    os.environ['GEMINI_API_KEY']=(ROOT/'work/ssh/gemini-api-key.txt').read_text(encoding='utf-8-sig').strip()
    CAMPAIGN.mkdir(parents=True,exist_ok=True)
    {'probes':probes,'pilot':pilot}[sys.argv[1]]()
