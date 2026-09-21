"""Explicit offline budget review of completed external controls; never submits."""
import copy
from decimal import Decimal
from pathlib import Path
import orchestration as o


def reconcile_controls_budget(data, state, authorization):
    if authorization != 'USER_APPROVED_COMPLETED_CONTROLS_BUDGET_RECONCILIATION':
        raise ValueError('Explicit economic reconciliation authorization required')
    state = o._state_dir(state)
    data = Path(data).resolve()
    with o.directory_lock(state / 'orchestration-lock'):
        o.verify(data)
        journal = o.read(state / 'operations.json')
        marker = o.read(state / 'external-job.json')
        budget = o.read(state / 'budget.json')
        if (journal.get('mode') != 'EXTERNAL_REVIEW' or journal.get('halted') is not False
                or journal.get('manifest') != o.digest(o.read(data / 'manifest.json'))
                or len(journal.get('attempts', {})) != 1 or budget.get('cap') != '30'
                or marker.get('main_authorized') is not False):
            raise ValueError('Expected blocked, adopted controls-only runtime')
        attempt, item = next(iter(journal['attempts'].items()))
        if set(budget.get('attempts', {})) != {attempt}:
            raise ValueError('Other or orphan reservations must be reconciled separately')
        report = o._archived(state, item['report'], 'report')
        entry = budget['attempts'][attempt]
        keys = o._keys(data, 'controls')
        if (item.get('shard') != 'controls' or item.get('phase') != 'RECONCILED'
                or item.get('recovery_pending') is not False
                or item.get('terminal_state') != 'SUCCEEDED'
                or item.get('job') != marker.get('job')
                or report.get('provider_job') != item.get('job')
                or report.get('provider_state') != 'SUCCEEDED'
                or report.get('operational_approval') is not True
                or entry.get('keys') != keys or entry.get('provider_job') != item.get('job')
                or not o.report_allows(report, keys, journal.get('version'), True)):
            raise ValueError('Complete controls reconciliation required')
        inputs = sum(r['usage']['promptTokenCount'] for r in report['records'].values())
        outputs = sum(r['usage']['candidatesTokenCount'] + r['usage'].get('thoughtsTokenCount', 0)
                      for r in report['records'].values())
        estimated = (Decimal(inputs)*Decimal('.125') + Decimal(outputs)*Decimal('.75'))/1000000
        allowance = Decimal('.03')
        if estimated > allowance:
            raise ValueError('Usage exceeds reviewed controls allowance')
        decision = {'authorization': authorization, 'journal_sha256': o.digest(journal),
                    'report': item['report'], 'usage_estimate_usd': str(estimated),
                    'retained_allowance_usd': str(allowance), 'invoice_verified': False,
                    'basis': 'Completed controls; conservative local allowance, not a refund',
                    'launch_authorized': False}
        if 'economic_reconciliation' in budget:
            if (budget['economic_reconciliation'] != decision or entry.get('reserved_usd') != '0.03'
                    or entry.get('state') != 'COMPLETED_ACCOUNTED'
                    or entry.get('budget_reconciled') is not True
                    or entry.get('billing_reconciled') is not False
                    or entry.get('estimated_usage_cost_usd') != str(estimated)):
                raise ValueError('Economic review conflicts with current evidence')
            return decision
        adoption = o._archived(state, journal['external_adoption'], 'external-adoption')
        if (entry.get('reserved_usd') != '30' or adoption['budget_sha256'] != o.digest(budget)
                or adoption['marker_sha256'] != o.digest(marker)):
            raise ValueError('Original adoption ledger/marker changed')
        # Archive the old ledger before the one atomic mutation. A crash either
        # leaves the original ledger, or the complete decision; repeating is safe.
        o._archive(state, 'budget-before-economic-review', budget)
        updated = copy.deepcopy(budget)
        updated['economic_reconciliation'] = decision
        updated['attempts'][attempt].update(reserved_usd=str(allowance),
            state='COMPLETED_ACCOUNTED', estimated_usage_cost_usd=str(estimated),
            billing_reconciled=False, budget_reconciled=True)
        o.save_json(state / 'budget.json', updated)
        return decision
