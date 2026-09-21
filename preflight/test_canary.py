"""Offline regressions for the explicitly authorized controls-only route."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import canary as c
import orchestration as o
import test_orchestration as fixtures


class CanaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.OrchestrationTests.setUpClass()

    def setUp(self):
        self.f = fixtures.OrchestrationTests('runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.auth = {k: True for k in ('controls_batch_authorized', 'billing_reported_active',
                     'project_key_confirmed', 'unknowns_accepted', 'no_other_submission_confirmed', 'price_checked')}
        self.auth.update(project_id=c.PROJECT, model=c.wire.MODEL, budget_usd='30')
        self.calls = []

    def submit(self, provider=None):
        def fake(path, body):
            self.calls.append((path, body))
            ledger = o.read(self.f.state/'budget.json')
            self.assertEqual(ledger['attempts'][c.ATTEMPT]['reserved_usd'], '30')
            self.assertEqual(o.read(self.f.state/'operations.json')['mode'], 'CANARY_ONLY')
            self.assertEqual(len(body['batch']['inputConfig']['requests']['requests']), 24)
            return {'name': 'batches/'+c.ATTEMPT}
        return c.submit_controls_once(self.f.data, self.f.state, self.f.receipt, self.auth, provider or fake)

    def recover(self, raw):
        return o.recover_once(self.f.data, self.f.state, c.ATTEMPT, lambda _: copy.deepcopy(raw))

    def blocked(self):
        self.f.assert_main_blocked()
        with self.assertRaises(ValueError): self.submit()

    def test_success_observes_version_but_cannot_admit_main_or_repeat(self):
        self.submit()
        raw = self.f.operation(attempt=c.ATTEMPT)
        first = self.recover(raw)
        journal = (self.f.state/'operations.json').read_bytes()
        ledger = (self.f.state/'budget.json').read_bytes()
        self.assertTrue(first['canary_pass'])
        self.assertTrue(first['controls_pass'])
        self.assertTrue(first['stop_future_submissions'])
        self.assertFalse(first['operational_approval'])
        self.assertEqual(first['versions'], [self.f.version])
        self.assertEqual(first, self.recover(raw))
        self.assertEqual(journal, (self.f.state/'operations.json').read_bytes())
        self.assertEqual(ledger, (self.f.state/'budget.json').read_bytes())
        # Even removing the ordinary halted/phase barriers cannot bypass mode.
        j = o.read(self.f.state/'operations.json')
        j['halted'] = False
        with self.assertRaisesRegex(ValueError, 'Canary runtime'):
            o._admission(self.f.state, self.f.data, j, o.read(self.f.state/'budget.json'), 'main-00', 'main')
        self.blocked()
        self.assertEqual(len(self.calls), 1)

    def test_pending_failed_partial_and_mixed_versions_remain_blocked(self):
        for kind in ('pending', 'failed', 'partial', 'mixed', 'usage'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                self.f.state = Path(folder)/'state'
                self.submit()
                rows = self.f.rows()
                raw = self.f.operation(attempt=c.ATTEMPT, rows=rows)
                if kind == 'pending': raw = self.f.operation(attempt=c.ATTEMPT, status='RUNNING')
                if kind == 'failed': raw = self.f.operation(attempt=c.ATTEMPT, status='FAILED')
                if kind == 'partial': raw = self.f.operation(attempt=c.ATTEMPT, rows=rows[:12])
                if kind == 'mixed': rows[0]['response']['modelVersion'] = 'other'
                if kind == 'usage': rows[0]['response'].pop('usageMetadata')
                report = self.recover(raw)
                self.assertFalse(report['canary_pass'])
                self.blocked()

    def test_timeout_and_crash_do_not_resubmit(self):
        calls = []
        def fail(*args): calls.append(args); raise TimeoutError()
        with self.assertRaises(RuntimeError): self.submit(fail)
        self.blocked()
        self.assertEqual(len(calls), 1)

    def test_crash_after_journal_before_budget_blocks_all_resubmission(self):
        save = o.save_json
        def fail(path, value):
            if Path(path).name == 'budget.json': raise OSError('synthetic')
            save(path, value)
        with patch.object(o, 'save_json', side_effect=fail), self.assertRaises(OSError): self.submit()
        self.blocked()
        self.assertEqual(self.calls, [])

    def test_authorization_receipt_and_existing_ledger_fail_before_provider(self):
        for kind in ('auth', 'project', 'receipt', 'ledger', 'external'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                auth = dict(self.auth)
                receipt = copy.deepcopy(self.f.receipt)
                state = Path(folder)/'state'
                if kind == 'auth': auth['controls_batch_authorized'] = False
                if kind == 'project': auth['project_id'] = 'other'
                if kind == 'receipt': receipt['requests'] = {}
                if kind == 'ledger': o.save_json(state/'budget.json', {'attempts': {}})
                if kind == 'external': o.save_json(state/'external-job.json', {'job': 'batches/existing'})
                with self.assertRaises(ValueError):
                    c.submit_controls_once(self.f.data, state, receipt, auth, lambda *a: self.fail('Provider forbidden'))
                if kind == 'external':
                    with self.assertRaisesRegex(ValueError, 'Pre-existing provider job'):
                        o._load(state, self.f.data, self.f.version)


if __name__ == '__main__': unittest.main()
