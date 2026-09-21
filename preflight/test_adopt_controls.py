"""External-control recovery never submits or releases money/launch gates."""
import copy
import unittest
from unittest.mock import patch
import adopt_controls as a
import orchestration as o
import test_orchestration as fixtures


class AdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.OrchestrationTests.setUpClass()

    def setUp(self):
        self.f = fixtures.OrchestrationTests('runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.raw = self.f.operation()
        self.provenance = {'user_confirmed_source': True, 'original_payload_available': False}
        self.marker = {'job': self.raw['name'], 'main_authorized': False}
        self.budget = {'cap': '30', 'attempts': {'control-attempt': {
            'provider_job': self.raw['name'], 'keys': o._keys(self.f.data, 'controls'),
            'reserved_usd': '30', 'billing_reconciled': False}}}
        o.save_json(self.f.state / 'external-job.json', self.marker)
        o.save_json(self.f.state / 'budget.json', self.budget)

    def adopt(self, raw=None, provenance=None):
        ref = o._archive(self.f.state, 'external-get', self.raw if raw is None else raw)
        return a.adopt_controls(self.f.data, self.f.state, ref, self.f.version,
                                self.provenance if provenance is None else provenance)

    def test_idempotent_and_main_blocked_even_without_marker(self):
        first = self.adopt()
        journal = (self.f.state / 'operations.json').read_bytes()
        self.assertEqual(first, self.adopt())
        self.assertEqual(journal, (self.f.state / 'operations.json').read_bytes())
        self.assertEqual(self.budget, o.read(self.f.state / 'budget.json'))
        self.assertEqual(self.marker, o.read(self.f.state / 'external-job.json'))
        self.assertFalse(first['launch_authorized'])
        self.f.assert_main_blocked()
        (self.f.state / 'external-job.json').unlink()  # Temporary fixture only.
        self.f.assert_main_blocked()
        with self.assertRaises(ValueError):
            self.f.submit(provider=lambda *args: self.fail('No resubmission'))

    def test_crash_after_intent_resumes_without_duplicate(self):
        with patch.object(o, '_observe', side_effect=OSError('Synthetic crash')):
            with self.assertRaises(OSError): self.adopt()
        self.f.assert_main_blocked()
        self.assertTrue(self.adopt()['controls_verified'])
        self.assertEqual(len(o.read(self.f.state / 'operations.json')['attempts']), 1)
        self.assertEqual(self.budget, o.read(self.f.state / 'budget.json'))

    def test_provenance_or_identity_refused(self):
        with self.assertRaises(ValueError): self.adopt(provenance={})
        raw = copy.deepcopy(self.raw)
        raw['name'] = 'batches/other'
        with self.assertRaises(ValueError): self.adopt(raw)
        self.assertFalse((self.f.state / 'operations.json').exists())

    def test_failed_validation_cannot_promote(self):
        raw = copy.deepcopy(self.raw)
        raw['response']['inlinedResponses']['inlinedResponses'].pop()
        with self.assertRaises(ValueError): self.adopt(raw)
        self.f.assert_main_blocked()
        self.assertEqual(self.budget, o.read(self.f.state / 'budget.json'))
        # A different observation cannot silently replace the failed evidence.
        with self.assertRaises(ValueError): self.adopt()

    def test_conflicting_journal_or_budget_refused(self):
        self.adopt()
        changed = dict(self.provenance, note='different attestation')
        with self.assertRaises(ValueError): self.adopt(provenance=changed)
        budget = copy.deepcopy(self.budget)
        budget['attempts']['control-attempt']['reserved_usd'] = '.03'
        o.save_json(self.f.state / 'budget.json', budget)
        with self.assertRaises(ValueError): self.adopt()

    def test_corrupt_archive_refused(self):
        ref = o._archive(self.f.state, 'external-get', self.raw)
        o.save_json(self.f.state / 'archive' / (ref + '.json'), {})
        with self.assertRaises((ValueError, KeyError)):
            a.adopt_controls(self.f.data, self.f.state, ref, self.f.version, self.provenance)


if __name__ == '__main__':
    unittest.main()
