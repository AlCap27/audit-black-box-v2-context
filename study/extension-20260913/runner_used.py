import sys, os, random, shutil
from pathlib import Path
import campaign224 as base
from common import read_json, save_json, digest, code_hash, directory_lock
from corpus import build

C = base.PROJECT/'extension-20260913'

def prepare():
    C.mkdir(exist_ok=True)
    old = read_json(base.PROJECT/'design/next-pilot-spec-PROPOSED.json')
    spec = dict(old)
    spec['seed'] = 202609130
    spec['assignments'] = []
    for i in range(12):
        labels = list('ABCD')*8
        seed = 202609130+1000+i
        random.Random(seed).shuffle(labels)
        spec['assignments'].append({'assignment_id':f'a{i+8:03}', 'seed':seed,
            'bundles':dict(zip([v['vendor_id'] for v in old['identities']],labels))})
    assert not any(a['bundles']==b['bundles'] for a in spec['assignments'] for b in old['assignments'])
    plan = {'authorized_attempt_cap':289, 'pilot_attempt_cap':288, 'probe_attempt_cap':1,
        'spec_sha256':digest(spec), 'code_sha256':code_hash(),
        'analysis':'Exploratory extension; report new 12 and combined 20 assignments separately. Primary contrast D-A. Keep all assignments; missing outcome bounds. No significance-based stopping; no automatic retries. Model/config unchanged.',
        'stop':'Stop on any new API or validation error. No infrastructure changes.'}
    if (C/'plan.json').exists():
        assert read_json(C/'plan.json')==plan
        assert read_json(C/'spec.json')==spec
    else:
        save_json(C/'plan.json',plan);save_json(C/'spec.json',spec)
        shutil.copy2(__file__,C/'runner_used.py')
        (C/'source-snapshot').mkdir(exist_ok=True)
        for p in base.PROJECT.glob('*.py'):shutil.copy2(p,C/'source-snapshot'/p.name)
    if not (C/'corpus').exists():build(C/'corpus',spec)
    return spec

def live():
    spec=prepare()
    os.environ['GEMINI_API_KEY']=(base.ROOT/'work/ssh/gemini-api-key.txt').read_text(encoding='utf-8-sig').strip()
    # Reuse the validated probe implementation with every other identity marked skipped.
    out=C/'probes'
    if not (out/'ledger.json').exists():
        save_json(out/'ledger.json',{'attempts':0,'records':{v['vendor_id']:'not_scheduled' for v in spec['identities'] if v['vendor_id']!='v019'}})
    base.CAMPAIGN=C
    base.probes()
    probe=read_json(out/'v019.json')
    if probe['status']!='valid' or probe['parsed']['known']:
        raise RuntimeError('Probe requires review; pilot not started')
    cfg=base.experiment.default_config('gemini')
    prepared=base.experiment.prepare(C/'corpus',cfg)
    base.experiment.prepare=lambda c,config:prepared
    run=C/'run'
    ledger=read_json(run/'ledger.json') if (run/'ledger.json').exists() else {'attempts':0,'records':{}}
    if any(v!='valid' for v in ledger['records'].values()):raise RuntimeError('Prior error requires review')
    def generate(trace,identities):
        base.throttle()
        return base.experiment.gemini_response(trace,base.MODEL,cfg['temperature'],cfg['max_output_tokens'])
    for limit in range(ledger['attempts']+1,289):
        summary=base.experiment.execute(C/'corpus',run,cfg,max_calls=limit,generator=generate)
        print(summary,flush=True)
        if any(k!='valid' and v for k,v in summary['statuses'].items()):break
    base.analyze(run)

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare();print('Plan frozen; 12 new assignments; no API calls')
    else:
        with directory_lock(C/'campaign-lock'):live()
