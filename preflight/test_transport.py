import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import transport as t
class TransportTests(unittest.TestCase):
    def test_real_payload_keys(self):
        p=t.batch_payload(t.BASE/'data','controls','test')
        self.assertEqual(len(p['batch']['inputConfig']['requests']['requests']),24)
        self.assertEqual(len({r['metadata']['key'] for r in p['batch']['inputConfig']['requests']['requests']}),24)
    def test_no_launch_before_handoff(self):
        with self.assertRaises(ValueError):t.send_once(t.BASE/'data',Path('.'),'controls','test',{}, {},lambda *_:self.fail('Network must not occur'))
    def test_timeout_not_retried(self):
        calls=[]
        gates={k:True for k in ('repository_handoff_complete','protocol_frozen','launch_authorized','model_project_verified','batch_quota_verified','token_count_verified','output_cap_verified','price_current','billing_decision_recorded','retention_plan_confirmed')}
        gates.update(model=t.MODEL,expected_model_version='SYNTHETIC-v1',input_price=.125,output_price=.75,available_batch_tokens=1000000)
        receipt=json.loads((t.ROOT/'token-receipt.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as d:
            def fail(*args):calls.append(args);raise TimeoutError()
            with self.assertRaises(RuntimeError):t.send_once(t.BASE/'data',Path(d),'controls','test',receipt,gates,fail)
            self.assertEqual(len(calls),1)
            self.assertEqual(json.loads((Path(d)/'budget.json').read_text())['attempts']['test']['state'],'PREPARED_UNCERTAIN')
    def test_missing_key_not_position(self):
        r=t.normalize_inline({'response':{'inlinedResponses':{'inlinedResponses':[{'response':{}}]}}})
        self.assertIsNone(r[0]['key'])
    def test_http_methods_and_pagination_encoding(self):
        paths=[('models/'+t.MODEL+':batchGenerateContent',{},'POST'),('batches/job',None,'GET'),('batches?pageSize=100&pageToken=a%2Fb',None,'GET'),('batches/job:cancel',{},'POST')]
        for path,body,method in paths:
            with self.subTest(path=path),patch.object(t,'_open',return_value=io.BytesIO(b'{}')) as op:
                t.http_transport('SYNTHETIC-NOT-A-KEY')(path,body)
                req=op.call_args.args[0]
                self.assertEqual(req.get_method(),method)
                self.assertEqual(req.full_url,'https://generativelanguage.googleapis.com/v1beta/'+path)
                self.assertEqual(op.call_args.kwargs['timeout'],60)
    def test_http_rejects_unknown_endpoint_or_wrong_method_before_network(self):
        cases=[('https://evil.example',None),('batches/job',{}),('batches/job:cancel',None),('batches?filter=anything',None),('models/'+t.MODEL+':generateContent',{}),('batches/job:delete',{}),('batches?pageSize=100&pageSize=100',None)]
        with patch.object(t,'_open',side_effect=AssertionError('Network forbidden')):
            for path,body in cases:
                with self.subTest(path=path),self.assertRaises(ValueError):t.http_transport('FAKE')(path,body)
    def test_http_does_not_retry(self):
        with patch.object(t,'_open',side_effect=TimeoutError) as op:
            with self.assertRaises(TimeoutError):t.http_transport('FAKE')('batches/job')
            self.assertEqual(op.call_count,1)
    def test_redirect_refused(self):
        with self.assertRaises(ValueError):t.NoRedirect().redirect_request(None,None,302,'',{},'https://elsewhere.invalid')
    def test_malformed_and_file_output_fail_closed(self):
        for raw in [{},{'response':{'responsesFile':'files/x'}},{'response':{'inlinedResponses':[]}}]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):t.normalize_inline(raw)
if __name__=='__main__':unittest.main(verbosity=2)
