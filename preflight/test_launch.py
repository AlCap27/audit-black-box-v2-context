import hashlib
import unittest
from unittest.mock import patch
import test_reconcile_budget as fixtures
import orchestration as o
import launch as l


class LaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): fixtures.BudgetReviewTests.setUpClass()

    def setUp(self):
        self.b = fixtures.BudgetReviewTests('runTest'); self.b.setUp()
        self.addCleanup(self.b.doCleanups)
        self.b.review(); self.f = self.b.f
        self.freeze = self.f.state.parent/'freeze.json'
        files = {p.relative_to(self.f.state).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.f.state.rglob('*') if p.is_file()}
        o.save_json(self.freeze, {'launch_readiness':'READY_FOR_LAUNCH',
            'operational_snapshot':{'files':{}}, 'runtime_snapshot':{'files':files}})

    def activate(self, auth=l.AUTH):
        return l.activate(self.f.data,self.f.state,self.freeze,'a'*40,auth)

    def test_activation_idempotent_and_controls_not_repeated(self):
        result=self.activate(); journal=(self.f.state/'operations.json').read_bytes()
        self.assertEqual(result,self.activate())
        self.assertEqual(journal,(self.f.state/'operations.json').read_bytes())
        with self.assertRaises(ValueError):
            l.submit_main(self.f.data,self.f.state,'controls',self.f.receipt,self.f.gates,
                          lambda *a:self.fail('Controls must never submit'))
        calls=[]
        def provider(path,body=None):
            if body is None:return {'operations':[{'name':'batches/control-attempt',
                'done':True,'metadata':{'state':'BATCH_STATE_SUCCEEDED'}}]}
            calls.append(path);return {'name':'batches/main0'}
        self.f.gates['available_batch_tokens']=10000000
        l.submit_main(self.f.data,self.f.state,'main-00',self.f.receipt,self.f.gates,provider)
        with self.assertRaises(ValueError):
            l.submit_main(self.f.data,self.f.state,'main-00',self.f.receipt,self.f.gates,provider)
        self.assertEqual(len(calls),1)
        self.assertEqual(len(o.read(self.f.state/'budget.json')['attempts']),2)

    def test_crash_before_marker_rename_recoverable(self):
        with patch('pathlib.Path.rename',side_effect=OSError('Synthetic crash')):
            with self.assertRaises(OSError):self.activate()
        self.f.assert_main_blocked()
        self.activate()
        self.assertTrue((self.f.state/'external-job-adopted.json').exists())

    def test_missing_authorization_and_changed_freeze_fail(self):
        with self.assertRaises(ValueError):self.activate('')
        budget=o.read(self.f.state/'budget.json');budget['cap']='31'
        o.save_json(self.f.state/'budget.json',budget)
        with self.assertRaises(ValueError):self.activate()

    def test_active_or_incomplete_list_cannot_submit(self):
        self.activate()
        for raw in [{'operations':[],'nextPageToken':'next'},
                    {'operations':[self.f.operation(status='RUNNING')]}, {}]:
            with self.assertRaises(ValueError):
                l.submit_main(self.f.data,self.f.state,'main-00',self.f.receipt,self.f.gates,
                              lambda *a:raw)
        self.assertEqual(len(o.read(self.f.state/'budget.json')['attempts']),1)
