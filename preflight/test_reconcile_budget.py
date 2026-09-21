import unittest
from unittest.mock import patch
import test_adopt_controls as fixtures
import orchestration as o
import reconcile_budget as b

AUTH = 'USER_APPROVED_COMPLETED_CONTROLS_BUDGET_RECONCILIATION'


class BudgetReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.AdoptionTests.setUpClass()

    def setUp(self):
        self.a = fixtures.AdoptionTests('runTest')
        self.a.setUp()
        self.addCleanup(self.a.doCleanups)
        self.a.adopt()
        self.f = self.a.f

    def review(self):
        return b.reconcile_controls_budget(self.f.data, self.f.state, AUTH)

    def test_completed_budget_once_without_unlocking_or_losing_keys(self):
        journal = (self.f.state/'operations.json').read_bytes()
        marker = (self.f.state/'external-job.json').read_bytes()
        first = self.review()
        budget = (self.f.state/'budget.json').read_bytes()
        self.assertEqual(first, self.review())
        self.assertEqual(budget, (self.f.state/'budget.json').read_bytes())
        self.assertEqual(journal, (self.f.state/'operations.json').read_bytes())
        self.assertEqual(marker, (self.f.state/'external-job.json').read_bytes())
        entry = o.read(self.f.state/'budget.json')['attempts']['control-attempt']
        self.assertEqual(entry['reserved_usd'], '0.03')
        self.assertEqual(entry['keys'], self.a.budget['attempts']['control-attempt']['keys'])
        self.assertFalse(entry['billing_reconciled'])
        self.f.assert_main_blocked()

    def test_crash_before_atomic_write_preserves_full_reservation(self):
        original = o.save_json
        def fail_budget(path, value):
            if path.name == 'budget.json': raise OSError('Synthetic crash')
            original(path, value)
        with patch.object(o, 'save_json', side_effect=fail_budget):
            with self.assertRaises(OSError): self.review()
        self.assertEqual(o.read(self.f.state/'budget.json'), self.a.budget)
        self.review()

    def test_pending_or_changed_ledger_refused(self):
        journal = o.read(self.f.state/'operations.json')
        journal['attempts']['control-attempt']['recovery_pending'] = True
        o._save(self.f.state, journal)
        with self.assertRaises(ValueError): self.review()
        self.assertEqual(o.read(self.f.state/'budget.json'), self.a.budget)

    def test_no_authorization_or_changed_review_refused(self):
        with self.assertRaises(ValueError):
            b.reconcile_controls_budget(self.f.data, self.f.state, '')
        self.review()
        budget = o.read(self.f.state/'budget.json')
        budget['attempts']['control-attempt']['reserved_usd'] = '0'
        o.save_json(self.f.state/'budget.json', budget)
        with self.assertRaises(ValueError): self.review()
