"""Offline adoption of archived controls, without releasing launch/budget gates.

No provider argument, network call, synthesized submission payload, or deletion
of the external-job marker. A crash can be resumed only with identical evidence.
"""
from pathlib import Path
import orchestration as o


def adopt_controls(data, state, archive_ref, version, provenance):
    if not isinstance(version, str) or not version.strip():
        raise ValueError('Explicit observed response version required')
    if not isinstance(provenance, dict) or provenance.get('user_confirmed_source') is not True:
        raise ValueError('User-confirmed provenance required')
    if provenance.get('original_payload_available') is not False:
        raise ValueError('This recovery route records the missing original payload')
    state = o._state_dir(state)
    data = Path(data).resolve()
    with o.directory_lock(state / 'orchestration-lock'):
        o.verify(data)
        marker = o.read(state / 'external-job.json')
        budget = o.read(state / 'budget.json')
        raw = o._archived(state, archive_ref, 'external-get')
        job = marker.get('job')
        if (not isinstance(job, str) or not o.JOB.fullmatch(job)
                or marker.get('main_authorized') is not False
                or raw.get('name') != job or o._job_state(raw) != 'SUCCEEDED'):
            raise ValueError('External job identity or terminal status mismatch')
        keys = o._keys(data, 'controls')
        entries = budget.get('attempts', {})
        if budget.get('cap') != '30' or len(entries) != 1:
            raise ValueError('Expected the isolated reconstructed controls ledger')
        attempt, reservation = next(iter(entries.items()))
        if (not o.ATTEMPT.fullmatch(attempt) or reservation.get('provider_job') != job
                or reservation.get('keys') != keys or reservation.get('reserved_usd') != '30'
                or reservation.get('billing_reconciled') is not False):
            raise ValueError('Unreconciled full reservation must remain intact')
        evidence = {'source_archive': archive_ref, 'provenance': provenance,
                    'budget_sha256': o.digest(budget), 'marker_sha256': o.digest(marker)}
        evidence_ref = o._archive(state, 'external-adoption', evidence)
        manifest = o.digest(o.read(data / 'manifest.json'))
        if (state / 'operations.json').exists():
            journal = o.read(state / 'operations.json')
            if (journal.get('schema') != 1 or journal.get('mode') != 'EXTERNAL_REVIEW'
                    or journal.get('manifest') != manifest or journal.get('version') != version
                    or journal.get('external_adoption') != evidence_ref
                    or set(journal.get('attempts', {})) != {attempt}
                    or journal['attempts'][attempt].get('job') != job
                    or journal['attempts'][attempt].get('shard') != 'controls'):
                raise ValueError('Existing journal conflicts with adoption evidence')
        else:
            journal = {'schema': 1, 'mode': 'EXTERNAL_REVIEW', 'manifest': manifest,
                       'version': version, 'halted': False, 'external_adoption': evidence_ref,
                       'attempts': {attempt: {'shard': 'controls', 'phase': 'ACCEPTED',
                           'job': job, 'request': None, 'observations': [], 'report': None,
                           'recovery_pending': True, 'cancel_requested': False}}}
            o._save(state, journal)
        # Reuse the full canonical validator, including provider statistics,
        # exact keys, semantics, version and usage. It is not a launch grant.
        report = o._observe(state, data, journal, attempt, raw)
        if report.get('operational_approval') is not True:
            raise ValueError('Archived controls failed complete validation; journal retained blocked')
        return {'attempt': attempt, 'job': job, 'report': journal['attempts'][attempt]['report'],
                'controls_verified': True, 'launch_authorized': False,
                'budget_released': False, 'source_archive': archive_ref}
