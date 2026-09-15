import json, random, tempfile, unittest
from pathlib import Path
from collections import Counter
from prepare import *
from batch_state import reserve, reconcile, verify, import_file, admit_shard

class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.path=Path(cls.tmp.name);cls.data=cls.path/'data'
        build(cls.data,2)
        cls.design=json.loads((cls.data/'design.json').read_text(encoding='utf-8'))
        cls.traces={t['key']:t for t in map(json.loads,(cls.data/'traces.jsonl').read_text(encoding='utf-8').splitlines())}
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_reproducibility(self):
        b=self.path/'rebuild';build(b,2)
        self.assertEqual(sha(b/'manifest.json'),sha(self.data/'manifest.json'))
        self.assertGreater(verify(b),900)
    def test_balance_and_factor_isolation(self):
        for a in self.design['assignments']:
            for t in range(4):self.assertEqual(Counter(a['conditions'][v['vendor_id']] for v in self.design['identities'] if v['template']==t),Counter(CELLS))
        for v in self.design['identities']:
            for s,l in itertools.product((0,1),repeat=2):
                a,b=fixtures(v,f'{s}{l}0'),fixtures(v,f'{s}{l}1')
                for fn in a:
                    if fn!='index.html':self.assertEqual(a[fn],b[fn])
                x,y=Extractor(),Extractor();x.feed(a['index.html']);y.feed(b['index.html'])
                self.assertEqual(x.schema,y.schema)
                self.assertEqual(len(y.plain),len(x.plain)+1)
    def test_discovery(self):
        rows=discovery_benchmarks();self.assertEqual(len(rows),16)
        self.assertEqual(sum(not x['discovered'] for x in rows),2)
    def test_requests_and_context(self):
        keys=[]
        for p in (self.data/'requests').glob('*.jsonl'):
            for r in map(json.loads,p.read_text(encoding='utf-8').splitlines()):
                keys.append(r['key']); t=self.traces[r['key']]
                self.assertEqual(t['request_sha256'],digest(r))
                self.assertEqual(r['request']['contents'][0]['parts'][0]['text'],t['prompt'])
                self.assertNotIn('tools',r['request'])
                self.assertLessEqual(len(t['shown']),5)
        self.assertEqual(len(keys),72);self.assertEqual(len(set(keys)),72)
    def fake(self,key,version=MODEL):
        return {'key':key,'response':{'modelVersion':version,'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'decision':'abstain','recommendations':[],'explanation':'SYNTHETIC TEST ONLY'})}]}}]}}
    def test_shuffle_identical_duplicate_missing(self):
        keys=list(self.traces)[:8];rows=[self.fake(k) for k in keys[:-1]];rows.append(rows[0]);random.Random(1).shuffle(rows)
        r=reconcile(keys,rows,self.traces,self.design['identities'],True,MODEL)
        self.assertEqual(r['records'][keys[-1]]['status'],'missing_terminal')
        self.assertEqual(r['records'][keys[0]]['copies'],2)
        self.assertTrue(r['stop_future_submissions'])
        self.assertTrue(all(not x['resubmit_allowed'] for x in r['records'].values()))
    def test_conflicts_versions_errors_pending(self):
        keys=list(self.traces)[:4]
        rows=[self.fake(keys[0]),self.fake(keys[0],'different'),self.fake(keys[1],'changed'),{'key':keys[2],'error':{'code':429}}, {'key':'unknown'}]
        r=reconcile(keys,rows,self.traces,self.design['identities'],False,MODEL)
        self.assertEqual([r['records'][k]['status'] for k in keys],['conflicting_duplicate','version_mismatch','provider_error','pending'])
        self.assertEqual(len(r['quarantine']),1)
    def test_truncation_not_abstention(self):
        k=next(iter(self.traces));r=self.fake(k);r['response']['candidates'][0]['finishReason']='MAX_TOKENS'
        self.assertEqual(reconcile([k],[r],self.traces,self.design['identities'])['records'][k]['status'],'invalid_output')
    def test_budget_restart_uncertain_and_cap(self):
        gates={k:True for k in ('protocol_frozen','launch_authorized','model_project_verified','batch_quota_verified','token_count_verified','output_cap_verified','price_current','billing_decision_recorded','retention_plan_confirmed')};gates['model']=MODEL
        d=self.path/'state'
        reserve(d,'controls',['c'],1,gates);reserve(d,'main',['m'],29,gates)
        for attempt,keys,amount in [('again',['m'],1),('new',['n'],'.000001')]:
            with self.assertRaises(ValueError):reserve(d,attempt,keys,amount,gates)
        with self.assertRaises(ValueError):reserve(self.path/'blocked','a',['a'],1,{})
        with self.assertRaises(ValueError):reserve(self.path/'nan','a',['a'],'NaN',gates)
        self.assertEqual(json.loads((d/'budget.json').read_text())['attempts']['main']['state'],'PREPARED_UNCERTAIN')
    def test_malformed_raw_import_preserved(self):
        raw=self.path/'malformed.jsonl';raw.write_text('{bad\n',encoding='utf-8')
        r=import_file(self.data,raw,self.path/'import','controls',True,MODEL)
        self.assertEqual(len(r['malformed_lines']),1);self.assertTrue(r['stop_future_submissions'])
        self.assertEqual((self.path/'import/raw.jsonl').read_bytes(),raw.read_bytes())
    def test_admission_requires_exact_counts_and_controls(self):
        with self.assertRaises(ValueError):admit_shard(self.data,self.path/'admit','controls','a',{}, {})
        with self.assertRaises(ValueError):admit_shard(self.data,self.path/'admit','main-00','a',{}, {})
    def test_admission_calculates_reservation(self):
        rows=list(map(json.loads,(self.data/'requests/controls.jsonl').read_text(encoding='utf-8').splitlines()))
        receipt={'model':MODEL,'method':'Google countTokens','requests':{r['key']:{'request_sha256':digest(r),'tokens':100} for r in rows}}
        gates={k:True for k in ('protocol_frozen','launch_authorized','model_project_verified','batch_quota_verified','token_count_verified','output_cap_verified','price_current','billing_decision_recorded','retention_plan_confirmed')}
        gates.update(model=MODEL,input_price=.125,output_price=.75,available_batch_tokens=2400)
        s=admit_shard(self.data,self.path/'calculated','controls','a',receipt,gates)
        self.assertAlmostEqual(float(s['attempts']['a']['reserved_usd']),.02628)
        gates['available_batch_tokens']=2399
        with self.assertRaises(ValueError):admit_shard(self.data,self.path/'quota','controls','a',receipt,gates)
        gates['available_batch_tokens']=2400;receipt['requests'][rows[0]['key']]['request_sha256']='tampered'
        with self.assertRaises(ValueError):admit_shard(self.data,self.path/'hash','controls','a',receipt,gates)
    def test_malformed_key_quarantined(self):
        k=next(iter(self.traces))
        r=reconcile([k],[{'key':[]}],self.traces,self.design['identities'])
        self.assertEqual(len(r['quarantine']),1)
    def test_all_control_outcomes(self):
        keys=[k for k,t in self.traces.items() if t['role']=='control'];rows=[]
        names={v['vendor_id']:v['name'] for v in self.design['identities']}
        for k in keys:
            t=self.traces[k];r=self.fake(k)
            answer={'decision':t['expected_decision'],'recommendations':[],'explanation':'SYNTHETIC ONLY'}
            if t['expected_vendor']:answer['recommendations']=[{'name':names[t['expected_vendor']],'source':1}]
            r['response']['candidates'][0]['content']['parts'][0]['text']=json.dumps(answer)
            rows.append(r)
        r=reconcile(keys,rows,self.traces,self.design['identities'],True,MODEL)
        self.assertTrue(r['controls_pass']);self.assertFalse(r['stop_future_submissions'])

if __name__=='__main__':unittest.main(verbosity=2)
