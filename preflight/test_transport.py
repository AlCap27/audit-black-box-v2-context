import json,tempfile,unittest
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
        with tempfile.TemporaryDirectory() as d,patch.object(t,'admit_shard') as admission:
            def fail(*args):calls.append(args);raise TimeoutError()
            with self.assertRaises(RuntimeError):t.send_once(t.BASE/'data',Path(d),'controls','test',{}, {'repository_handoff_complete':True},fail)
            self.assertEqual(len(calls),1);self.assertTrue((Path(d)/'test-uncertain.json').exists())
    def test_missing_key_not_position(self):
        r=t.normalize_inline({'response':{'inlinedResponses':{'inlinedResponses':[{'response':{}}]}}})
        self.assertIsNone(r[0]['key'])
if __name__=='__main__':unittest.main(verbosity=2)
