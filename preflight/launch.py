"""Activate reviewed external controls after a published freeze; one main at a time."""
import hashlib
from pathlib import Path
import orchestration as o
import transport as t

AUTH = 'AUTHORIZE_12_SEQUENTIAL_MAIN_BATCHES_USD30_AFTER_FREEZE_PUSH'


def activate(data, state, freeze_path, published_commit, authorization):
    if authorization != AUTH or not isinstance(published_commit, str) or len(published_commit) != 40:
        raise ValueError('Explicit main authorization and published commit required')
    state = o._state_dir(state)
    freeze_path = Path(freeze_path)
    freeze = o.read(freeze_path)
    if freeze.get('launch_readiness') != 'READY_FOR_LAUNCH':
        raise ValueError('Freeze not ready')
    for name, expected in freeze['operational_snapshot']['files'].items():
        if hashlib.sha256((t.ROOT.parent/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Operational freeze changed: '+name)
    o.verify(Path(data))
    approval = {'authorization': authorization, 'published_commit': published_commit,
                'freeze_sha256': hashlib.sha256(freeze_path.read_bytes()).hexdigest()}
    with o.directory_lock(state/'orchestration-lock'):
        journal = o.read(state/'operations.json')
        budget = o.read(state/'budget.json')
        if journal.get('mode') == 'CAMPAIGN':
            if o._archived(state, journal['launch_approval'], 'launch-approval') != approval:
                raise ValueError('Conflicting activation')
        else:
            if journal.get('mode') != 'EXTERNAL_REVIEW' or journal.get('halted') is not False:
                raise ValueError('Only successfully reviewed external controls can activate')
            if budget.get('economic_reconciliation', {}).get('journal_sha256') != o.digest(journal):
                raise ValueError('Economic review mismatch')
            for name, expected in freeze['runtime_snapshot']['files'].items():
                if hashlib.sha256((state/name).read_bytes()).hexdigest() != expected:
                    raise ValueError('Frozen runtime changed: '+name)
            candidate = dict(journal, mode='CAMPAIGN')
            o._admission(state, Path(data), candidate, budget, 'main-00', 'activation-check')
            candidate['launch_approval'] = o._archive(state, 'launch-approval', approval)
            o._save(state, candidate)
        # Rename only after durable approval; crash before rename remains blocked.
        # Preserve the old marker as evidence instead of deleting it.
        marker = state/'external-job.json'
        archived = state/'external-job-adopted.json'
        if marker.exists():
            if archived.exists():
                raise ValueError('Conflicting marker archive; review before sending')
            marker.rename(archived)
        if not archived.exists():
            raise ValueError('Missing preserved external job marker')
        return approval


def submit_main(data, state, shard, receipt, gates, provider):
    if shard not in o.SHARDS[1:]:
        raise ValueError('Main-only path: controls cannot be repeated')
    state = o._state_dir(state)
    journal = o.read(state/'operations.json')
    if journal.get('mode') != 'CAMPAIGN' or not journal.get('launch_approval'):
        raise ValueError('Campaign activation required')
    # A fresh complete list establishes current occupancy; no optimistic
    # subtraction or retry if there is any active/ambiguous job.
    raw = provider('batches?pageSize=100')
    o._archive(state, 'main-admission-list', raw)
    if (not isinstance(raw, dict) or raw.get('nextPageToken') or raw.get('unreachable')
            or not isinstance(raw.get('operations'), list)):
        raise ValueError('Incomplete Batch list')
    # List projections need not contain the response body required by GET
    # reconciliation; check terminal status and done without demanding outputs.
    terminal_labels = {prefix + status for prefix in ('BATCH_STATE_', 'JOB_STATE_')
                       for status in o.TERMINAL}
    if any(not isinstance(job, dict) or job.get('done') is not True
           or not isinstance(job.get('metadata'), dict)
           or job['metadata'].get('state') not in terminal_labels for job in raw['operations']):
        raise ValueError('Another active Batch prevents sequential submission')
    if gates.get('batch_quota_verified') is not True or gates.get('available_batch_tokens') != 10000000:
        raise ValueError('Reviewed project quota required')
    return o.submit_once(Path(data), state, shard, 'audit-v2-'+shard, receipt, gates, provider)
