"""One explicitly authorized controls-only Batch, outside sealed campaign gates.

Unknown quota, response version and enforcement remain unknown. They are probe
outcomes, never fabricated True flags. Same journal/ledger/recovery as campaign;
the CANARY_ONLY marker permanently prevents using this runtime for main shards.
"""
import json
import uuid
from decimal import Decimal
from pathlib import Path

import orchestration as o
import transport as wire

PROJECT = 'gen-lang-client-0393363402'
RUNTIME = wire.ROOT.parent / 'runtime' / 'audit-v2'
ATTEMPT = 'controls-canary-20260921'


def submit_controls_once(data, state, receipt, authorization, provider):
    """Exactly 24 frozen controls; no shard argument, no retry or promotion."""
    required = ('controls_batch_authorized', 'billing_reported_active',
                'project_key_confirmed', 'unknowns_accepted',
                'no_other_submission_confirmed', 'price_checked')
    if any(authorization.get(k) is not True for k in required):
        raise ValueError('Explicit controls-only authorization/evidence required')
    if authorization.get('project_id') != PROJECT or authorization.get('model') != wire.MODEL:
        raise ValueError('Wrong canary project/model')
    if authorization.get('budget_usd') != '30':
        raise ValueError('Reviewed global budget must remain USD30')
    state = o._state_dir(state)
    data = Path(data).resolve()
    with o.directory_lock(state / 'orchestration-lock'):
        # Never initialize over an existing campaign, attempt or uncertain POST.
        if any((state / name).exists() for name in ('operations.json', 'budget.json', 'external-job.json')):
            raise ValueError('Existing runtime: recover; never resubmit controls')
        o.verify(data)
        rows = [json.loads(line) for line in (data / 'requests/controls.jsonl').read_text(encoding='utf-8').splitlines()]
        keys = o._keys(data, 'controls')
        if len(rows) != 24 or len(set(keys)) != 24 or [r['key'] for r in rows] != keys:
            raise ValueError('Only the complete frozen controls shard is allowed')
        if receipt.get('model') != wire.MODEL or receipt.get('method') != 'Google countTokens':
            raise ValueError('Provider token receipt required')
        total_input = 0
        for row in rows:
            entry = receipt.get('requests', {}).get(row['key'], {})
            count = entry.get('tokens')
            if entry.get('request_sha256') != o.digest(row) or type(count) is not int or count <= 0:
                raise ValueError('Token receipt mismatch')
            total_input += count
        body = wire.batch_payload(data, 'controls', ATTEMPT)
        body['batch']['displayName'] += '-' + uuid.uuid4().hex
        estimate = (Decimal(total_input) * Decimal('.125') + Decimal(24*1200) * Decimal('.75')) / 1000000 * Decimal('1.20')
        # Reserve the whole remaining allocation for this one experiment until
        # manual billing reconciliation. This is NOT a Google billing hard cap.
        journal = {'schema': 1, 'manifest': o.digest(o.read(data/'manifest.json')),
                   'version': 'CANARY_OBSERVE_ONLY', 'mode': 'CANARY_ONLY',
                   'halted': False, 'authorization': o._archive(state, 'authorization', authorization),
                   'unknowns': ['batch_quota', 'response_model_version', 'output_cap_enforcement', 'final_freeze'],
                   'attempts': {ATTEMPT: {'shard': 'controls', 'phase': 'INTENT',
                       'job': None, 'request': o._archive(state, 'request', body),
                       'observations': [], 'report': None, 'recovery_pending': True,
                       'cancel_requested': False}}}
        o._save(state, journal)
        o.save_json(state/'budget.json', {'cap': '30', 'attempts': {ATTEMPT: {
            'keys': keys, 'reserved_usd': '30', 'estimated_usd_with_margin': str(estimate),
            'reservation_basis': 'Full allocation held pending manual reconciliation',
            'state': 'PREPARED_UNCERTAIN', 'provider_job': None}}})
        item = journal['attempts'][ATTEMPT]
        item['phase'] = 'PREPARED_UNCERTAIN'
        o._save(state, journal)
        try:
            raw = provider('models/' + wire.MODEL + ':batchGenerateContent', body)
            item['create'] = o._archive(state, 'create', raw)
            o._save(state, journal)
            if not isinstance(raw, dict) or not isinstance(raw.get('name'), str) or not o.JOB.fullmatch(raw['name']):
                raise ValueError('Unrecognized provider job ID')
            o._bind(state, journal, None, ATTEMPT, raw['name'])
        except Exception as exc:
            item['last_error'] = type(exc).__name__
            o._save(state, journal)
            raise RuntimeError('Canary submission uncertain; recover, never resend') from None
        return item['job']
