"""Operational overlay; never writes to the sealed experiment.

No CLI, background worker, automatic submission retry or budget release.
All provider access is injected. Persisted state must be retained for the whole
campaign; making a fresh directory is NOT a supported retry/recovery procedure.
"""
import json
import re
import uuid
from pathlib import Path
from urllib.parse import urlencode

import transport as wire
from batch_state import admit_shard, reconcile, verify
from common import directory_lock, save_json, digest

JOB = re.compile(r'batches/[a-zA-Z0-9_-]+')
ATTEMPT = re.compile(r'[a-zA-Z0-9_-]{1,80}')
SHARDS = ['controls'] + [f'main-{i:02}' for i in range(12)]
TERMINAL = {'SUCCEEDED', 'FAILED', 'CANCELLED', 'EXPIRED'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _state_dir(state):
    state = Path(state).resolve()
    for protected in (wire.BASE.parent.resolve(), wire.ROOT.resolve(),
                      (wire.ROOT.parent / '.git').resolve()):
        if state == protected or state.is_relative_to(protected):
            raise ValueError('Runtime state must be outside source/sealed directories')
    return state


def _archive(state, kind, value):
    """Content-addressed parsed raw JSON. Repeated observations do not overwrite."""
    document = {'kind': kind, 'value': value}
    ref = digest(document)
    path = state / 'archive' / (ref + '.json')
    if path.exists():
        if digest(read(path)) != ref:
            raise ValueError('Corrupt archive')
    else:
        save_json(path, document)
    return ref


def _archived(state, ref, kind):
    if not isinstance(ref, str) or not re.fullmatch('[0-9a-f]{64}', ref):
        raise ValueError('Invalid archive reference')
    doc = read(state / 'archive' / (ref + '.json'))
    if digest(doc) != ref or doc['kind'] != kind:
        raise ValueError('Archive hash/type mismatch')
    return doc['value']


def _load(state, data, version=None):
    data = Path(data).resolve()
    verify(data)
    manifest = digest(read(data / 'manifest.json'))
    path = state / 'operations.json'
    if path.exists():
        journal = read(path)
        if (journal['schema'] != 1 or journal['manifest'] != manifest
                or (version is not None and journal['version'] != version)):
            raise ValueError('Campaign data/version changed')
    else:
        if not isinstance(version, str) or not version.strip():
            raise ValueError('Explicit expected response modelVersion required')
        journal = {'schema': 1, 'manifest': manifest, 'version': version,
                   'attempts': {}, 'halted': False}
    # Budget entries without their operational intent indicate a legacy or
    # interrupted migration, never an empty campaign eligible for new requests.
    budget = read(state / 'budget.json') if (state / 'budget.json').exists() else {'attempts': {}}
    if set(budget['attempts']) - set(journal['attempts']):
        raise ValueError('Orphan budget reservations: manual recovery required')
    return journal, budget


def _save(state, journal):
    save_json(state / 'operations.json', journal)


def _keys(data, shard):
    return next(s['keys'] for s in read(Path(data) / 'shards.json') if s['name'] == shard)


def report_allows(report, keys, version, controls=False):
    """Canonical fail-closed report predicate (not the legacy controls_pass)."""
    if not isinstance(report, dict) or not isinstance(version, str) or not version:
        return False
    if (report.get('terminal') is not True
            or report.get('stop_future_submissions') is not False
            or report.get('automatic_resubmission') is not False
            or report.get('quarantine') != []
            or report.get('malformed_lines', []) != []
            or report.get('versions') != [version]):
        return False
    records = report.get('records')
    if not isinstance(records, dict) or set(records) != set(keys) or not keys:
        return False
    if controls and (len(keys) != 24 or report.get('controls_pass') is not True):
        return False
    for row in records.values():
        if not isinstance(row, dict) or row.get('status') != 'valid' or row.get('model_version') != version:
            return False
        if controls and row.get('control_pass') is not True:
            return False
        usage = row.get('usage')
        if not isinstance(usage, dict):
            return False
        counts = [usage.get('promptTokenCount'), usage.get('candidatesTokenCount'),
                  usage.get('thoughtsTokenCount', 0)]
        if any(type(n) is not int or n < 0 for n in counts) or sum(counts[1:]) > 1200:
            return False
    return True


def _admission(state, data, journal, budget, shard, attempt):
    if journal['halted'] or attempt in journal['attempts']:
        raise ValueError('Campaign halted or attempt already recorded')
    completed = []
    for name, item in journal['attempts'].items():
        if name not in budget['attempts']:
            raise ValueError('Interrupted intent; manual recovery required')
        if item['phase'] != 'RECONCILED' or item.get('recovery_pending'):
            raise ValueError('Unresolved previous job; no subsequent submission')
        report = _archived(state, item['report'], 'report')
        reservation = budget['attempts'][name]
        if (report.get('provider_job') != item['job']
                or report.get('provider_state') != 'SUCCEEDED'
                or report.get('operational_approval') is not True
                or reservation.get('provider_job') != item['job']
                or reservation.get('keys') != _keys(data, item['shard'])
                or not report_allows(report, _keys(data, item['shard']),
                                     journal['version'], item['shard'] == 'controls')):
            raise ValueError('Previous complete report does not permit admission')
        completed.append(item['shard'])
    if completed != SHARDS[:len(completed)] or len(completed) >= len(SHARDS) or shard != SHARDS[len(completed)]:
        raise ValueError('Controls first, then one main shard at a time in order')


def submit_once(data, state, shard, attempt, receipt, gates, provider):
    if shard not in SHARDS or not isinstance(attempt, str) or not ATTEMPT.fullmatch(attempt):
        raise ValueError('Invalid shard/attempt')
    if gates.get('repository_handoff_complete') is not True:
        raise ValueError('Repository handoff required before generation')
    state = _state_dir(state)
    with directory_lock(state / 'orchestration-lock'):
        journal, budget = _load(state, data, gates.get('expected_model_version'))
        if not gates.get('expected_model_version'):
            raise ValueError('Expected response modelVersion required')
        _admission(state, data, journal, budget, shard, attempt)
        body = wire.batch_payload(Path(data), shard, attempt)
        # Unique, persisted correlation identity: never use list order/position.
        body['batch']['displayName'] += '-' + uuid.uuid4().hex
        item = {'shard': shard, 'phase': 'INTENT', 'job': None,
                'request': _archive(state, 'request', body),
                'observations': [], 'report': None, 'recovery_pending': True,
                'cancel_requested': False}
        journal['attempts'][attempt] = item
        _save(state, journal)
        derived = dict(gates, controls_pass=(shard != 'controls'))
        # This primitive only provides immutable-data checks and budget reserve.
        # Its weak controls flag is reached ONLY after the canonical predicate.
        try:
            admit_shard(Path(data), state, shard, attempt, receipt, derived)
        except Exception:
            # Proven local refusal before the POST: discard only the unused
            # intent. If a reservation exists (or cannot be read), retain it.
            ledger = read(state / 'budget.json') if (state / 'budget.json').exists() else {'attempts': {}}
            if attempt not in ledger['attempts']:
                del journal['attempts'][attempt]
                _save(state, journal)
            raise
        item['phase'] = 'PREPARED_UNCERTAIN'
        _save(state, journal)
        try:
            raw = provider('models/' + wire.MODEL + ':batchGenerateContent', body)
            item['create'] = _archive(state, 'create', raw)
            _save(state, journal)
            if not isinstance(raw, dict) or not isinstance(raw.get('name'), str) or not JOB.fullmatch(raw['name']):
                raise ValueError('Missing provider job ID')
            _bind(state, journal, budget=None, attempt=attempt, job=raw['name'])
        except Exception as exc:
            item['last_error'] = type(exc).__name__  # no key/payload in messages
            _save(state, journal)
            raise RuntimeError('Submission uncertain; reservation retained; do not resubmit') from None
        return item['job']


def _bind(state, journal, budget, attempt, job):
    item = journal['attempts'][attempt]
    if item['job'] not in (None, job) or any(i['job'] == job for a, i in journal['attempts'].items() if a != attempt):
        raise ValueError('Conflicting job identity')
    budget = read(state / 'budget.json') if budget is None else budget
    if attempt not in budget['attempts']:
        raise ValueError('Missing reservation')
    if budget['attempts'][attempt].get('provider_job') not in (None, job):
        raise ValueError('Budget job identity conflict')
    item.update(job=job, phase='ACCEPTED', recovery_pending=True)
    # Journal first: a crash before budget metadata update must still prevent send.
    _save(state, journal)
    budget['attempts'][attempt].update(state='ACCEPTED', provider_job=job)
    save_json(state / 'budget.json', budget)


def _job_state(raw):
    if not isinstance(raw, dict) or not isinstance(raw.get('metadata'), dict):
        raise ValueError('Missing operation metadata')
    value = raw['metadata'].get('state')
    if not isinstance(value, str):
        raise ValueError('Missing job state')
    # REST reference uses BATCH_STATE_; the public guide shows JOB_STATE_.
    if value.startswith('BATCH_STATE_'):
        value = value[len('BATCH_STATE_'):]
    elif value.startswith('JOB_STATE_'):
        value = value[len('JOB_STATE_'):]
    else:
        raise ValueError('Unknown state namespace')
    if value not in TERMINAL | {'PENDING', 'RUNNING'}:
        raise ValueError('Unknown job state')
    done = raw.get('done', False)  # Proto JSON may omit false.
    if type(done) is not bool or done != (value in TERMINAL):
        raise ValueError('Ambiguous operation terminality')
    if value == 'SUCCEEDED' and ('error' in raw or 'response' not in raw):
        raise ValueError('Success without a successful result')
    if 'error' in raw and value not in TERMINAL:
        raise ValueError('Nonterminal operation with error')
    return value


def _observe(state, data, journal, attempt, raw):
    item = journal['attempts'][attempt]
    ref = _archive(state, 'get', raw)
    if ref not in item['observations']:
        item['observations'].append(ref)
    _save(state, journal)  # Persist evidence before parsing; failures stay blocked.
    if not isinstance(raw, dict) or raw.get('name') != item['job']:
        raise ValueError('Wrong job identity')
    status = _job_state(raw)
    if 'response' in raw:
        wire.normalize_inline(raw)  # Fail explicitly on unsupported current output.
    previous = item.get('terminal_state')
    if previous and status not in TERMINAL:
        raise ValueError('Terminal state regressed')
    if previous and status != previous:
        journal['halted'] = True  # Preserve late results, never silently lift stop.
    if status in TERMINAL:
        item['terminal_state'] = status
    rows = {}
    observation_errors = []
    for observation in item['observations']:
        old = _archived(state, observation, 'get')
        try:
            if not isinstance(old, dict) or old.get('name') != item['job']:
                raise ValueError('Archived job mismatch')
            _job_state(old)
            if 'response' in old:
                for row in wire.normalize_inline(old):
                    rows[digest(row)] = row  # Same snapshot/row never counted twice.
        except (ValueError, TypeError, KeyError, AttributeError):
            # Keep the stop sticky, but allow later valid evidence to be parsed.
            observation_errors.append(observation)
            journal['halted'] = True
    traces = {r['key']: r for r in map(json.loads, (Path(data) / 'traces.jsonl').read_text(encoding='utf-8').splitlines())}
    report = reconcile(_keys(data, item['shard']), list(rows.values()), traces,
                       read(Path(data) / 'design.json')['identities'],
                       status in TERMINAL, journal['version'])
    success = status == 'SUCCEEDED' and report_allows(
        report, _keys(data, item['shard']), journal['version'], item['shard'] == 'controls')
    stats = raw['metadata'].get('batchStats')
    if stats is not None and status == 'SUCCEEDED':
        expected = len(_keys(data, item['shard']))
        required = {'requestCount': expected, 'successfulRequestCount': expected,
                    'failedRequestCount': 0, 'pendingRequestCount': 0}
        if not isinstance(stats, dict) or any(
                str(stats.get(key, '0')) != str(value) for key, value in required.items()):
            success = False
            report['batch_stats_inconsistent'] = True
    # A provider job failure/cancel cannot be hidden by otherwise valid rows.
    report['provider_job'] = item['job']
    report['provider_state'] = status
    report['observation_errors'] = observation_errors
    report['operational_approval'] = success and not journal['halted']
    if status in TERMINAL and not success:
        journal['halted'] = True
    # Detect a definite row anomaly even in partial observations. Missing rows
    # before terminality remain pending, and still prohibit subsequent jobs.
    if report['quarantine'] or any(r['status'] not in ('valid', 'pending') or r.get('control_pass') is False for r in report['records'].values()):
        journal['halted'] = True
    if item['shard'] == 'controls':
        report['controls_pass'] = success and not journal['halted']
    report['stop_future_submissions'] = not success or journal['halted']
    report['operational_approval'] = success and not journal['halted']
    item['report'] = _archive(state, 'report', report)
    item['phase'] = 'RECONCILED' if report['operational_approval'] else ('HALTED' if journal['halted'] else 'PENDING')
    item['recovery_pending'] = False
    _save(state, journal)
    return report


def recover_once(data, state, attempt, provider):
    """One read, durable evidence, cumulative keyed reconciliation; never submit."""
    state = _state_dir(state)
    with directory_lock(state / 'orchestration-lock'):
        journal, budget = _load(state, data)
        item = journal['attempts'][attempt]
        if item['job'] is None:
            # Reuse durable create evidence after a crash before _bind.
            if item.get('create'):
                create = _archived(state, item['create'], 'create')
                if isinstance(create, dict) and isinstance(create.get('name'), str) and JOB.fullmatch(create['name']):
                    _bind(state, journal, None, attempt, create['name'])
            if item['job'] is None:
                raise ValueError('Job ID unknown; explicit locate required, never resend')
        elif budget['attempts'].get(attempt, {}).get('provider_job') != item['job']:
            # Repair a crash after journal binding but before budget metadata.
            _bind(state, journal, budget, attempt, item['job'])
        item['recovery_pending'] = True
        _save(state, journal)
        try:
            return _observe(state, Path(data), journal, attempt, provider(item['job']))
        except Exception as exc:
            item['last_error'] = type(exc).__name__
            journal['halted'] = True
            _save(state, journal)
            raise RuntimeError('Recovery incomplete; evidence/reservation retained; campaign blocked') from None


def locate_once(data, state, attempt, provider, max_pages=10):
    """Bounded explicit list traversal. Zero/ambiguous matches NEVER permit retry.

    Requires an exact random displayName AND model in metadata; if the service
    does not expose them/list, retain uncertainty for manual provider review.
    """
    if type(max_pages) is not int or not 1 <= max_pages <= 10:
        raise ValueError('List traversal bound must be 1..10')
    state = _state_dir(state)
    with directory_lock(state / 'orchestration-lock'):
        journal, _ = _load(state, data)
        item = journal['attempts'][attempt]
        if item['job']:
            return item['job']
        body = _archived(state, item['request'], 'request')
        item['recovery_pending'] = True
        _save(state, journal)
        matches = set()
        token = None
        tokens = set()
        try:
            for _ in range(max_pages):
                query = {'pageSize': '100'}
                if token:
                    query['pageToken'] = token
                raw = provider('batches?' + urlencode(query))
                ref = _archive(state, 'list', raw)
                item.setdefault('lists', [])
                if ref not in item['lists']:
                    item['lists'].append(ref)
                _save(state, journal)
                if not isinstance(raw, dict) or raw.get('unreachable') or not isinstance(raw.get('operations', []), list):
                    raise ValueError('Incomplete list response')
                for operation in raw.get('operations', []):
                    if not isinstance(operation, dict):
                        raise ValueError('Malformed list entry')
                    meta = operation.get('metadata', {})
                    if not isinstance(meta, dict):
                        raise ValueError('Malformed list metadata')
                    if meta.get('displayName') == body['batch']['displayName']:
                        if meta.get('model') != 'models/' + wire.MODEL or not isinstance(operation.get('name'), str) or not JOB.fullmatch(operation['name']):
                            raise ValueError('Unverifiable candidate identity')
                        matches.add(operation['name'])
                token = raw.get('nextPageToken')
                if not token:
                    break
                if not isinstance(token, str) or token in tokens:
                    raise ValueError('Invalid/repeated page token')
                tokens.add(token)
            else:
                raise ValueError('List incomplete at configured page bound')
            if len(matches) != 1:
                raise ValueError('No unique exact job match; do not resubmit')
            job = matches.pop()
            _bind(state, journal, None, attempt, job)
            return job
        except Exception as exc:
            item['last_error'] = type(exc).__name__
            _save(state, journal)
            raise RuntimeError('Job identity unresolved; no fallback or resubmission') from None


def cancel_once(data, state, attempt, provider):
    """At most one cancel POST per attempt, including timeout/restart cases.

    A cancel acknowledgement is NOT terminality, a refund, or permission to retry.
    Continue explicit GET recovery to archive late results. Unimplemented cancel
    leaves the job unresolved and subsequent submissions halted.
    """
    state = _state_dir(state)
    with directory_lock(state / 'orchestration-lock'):
        journal, _ = _load(state, data)
        item = journal['attempts'][attempt]
        journal['halted'] = True
        if not item['job']:
            _save(state, journal)
            raise ValueError('Cannot cancel without a verified job ID')
        if item['cancel_requested'] or item.get('terminal_state'):
            _save(state, journal)
            return {'cancel_requested': item['cancel_requested'], 'terminal_verified': bool(item.get('terminal_state'))}
        item.update(cancel_requested=True, recovery_pending=True)
        _save(state, journal)
        try:
            raw = provider(item['job'] + ':cancel', {})
            item['cancel'] = _archive(state, 'cancel', raw)
            _save(state, journal)
            return {'cancel_requested': True, 'terminal_verified': False}
        except Exception as exc:
            item['last_error'] = type(exc).__name__
            _save(state, journal)
            raise RuntimeError('Cancellation uncertain/unsupported; poll explicitly; never resend') from None
