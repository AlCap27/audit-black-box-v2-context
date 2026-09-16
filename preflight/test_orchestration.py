"""Synthetic only: real frozen inputs, temporary ledgers, injected fake provider."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import orchestration as o
import transport as t
from batch_state import reconcile


class OrchestrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=t.BASE/'data'
        cls.receipt=o.read(t.ROOT/'token-receipt.json')
        cls.design=o.read(cls.data/'design.json')
        cls.traces={r['key']:r for r in map(json.loads,(cls.data/'traces.jsonl').read_text(encoding='utf-8').splitlines())}
        cls.version='SYNTHETIC-v1'

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state=Path(self.temp.name)/'state'
        self.gates={k:True for k in ('repository_handoff_complete','protocol_frozen','launch_authorized','model_project_verified','batch_quota_verified','token_count_verified','output_cap_verified','price_current','billing_decision_recorded','retention_plan_confirmed')}
        self.gates.update(model=t.MODEL,expected_model_version=self.version,input_price=.125,output_price=.75,available_batch_tokens=1000000)
        self.calls=[]

    def submit(self,shard='controls',attempt='control-attempt',provider=None):
        def fake(path,body):
            self.calls.append((path,body))
            self.assertEqual(o.read(self.state/'budget.json')['attempts'][attempt]['state'],'PREPARED_UNCERTAIN')
            return {'name':'batches/'+attempt}
        return t.send_once(self.data,self.state,shard,attempt,self.receipt,self.gates,provider or fake)

    def rows(self,shard='controls',version=None):
        names={v['vendor_id']:v['name'] for v in self.design['identities']}
        result=[]
        for key in o._keys(self.data,shard):
            tr=self.traces[key]
            answer={'decision':tr.get('expected_decision','abstain'),'recommendations':[],'explanation':'SYNTHETIC OFFLINE ONLY'}
            if tr.get('expected_vendor'):
                answer['recommendations']=[{'name':names[tr['expected_vendor']],'source':1}]
            result.append({'metadata':{'key':key},'response':{'modelVersion':version or self.version,
                'usageMetadata':{'promptTokenCount':self.receipt['requests'][key]['tokens'],'candidatesTokenCount':30,'thoughtsTokenCount':0},
                'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(answer)}]}}]}})
        return result

    def operation(self,shard='controls',attempt='control-attempt',status='SUCCEEDED',rows=None):
        raw={'name':'batches/'+attempt,'done':status in o.TERMINAL,'metadata':{'state':'BATCH_STATE_'+status}}
        if rows is not None or status=='SUCCEEDED':
            raw['response']={'inlinedResponses':{'inlinedResponses':rows if rows is not None else self.rows(shard)}}
        if status in {'FAILED','CANCELLED','EXPIRED'}:raw['error']={'code':13,'message':'SYNTHETIC'}
        return raw

    def recover(self,raw,attempt='control-attempt'):
        return o.recover_once(self.data,self.state,attempt,lambda path:copy.deepcopy(raw))

    def assert_main_blocked(self):
        self.gates['controls_pass']=True
        with self.assertRaises((ValueError,RuntimeError)):
            self.submit('main-00','main-attempt',lambda *a:self.fail('Main must not reach network'))

    def test_valid_controls_and_all_twelve_main_shards(self):
        self.submit()
        self.recover(self.operation())
        for index in range(12):
            shard=f'main-{index:02}'
            self.submit(shard,shard)
            self.recover(self.operation(shard,shard),shard)
        ledger=o.read(self.state/'budget.json')
        self.assertEqual(len(self.calls),13)
        self.assertEqual(len(ledger['attempts']),13)
        from decimal import Decimal
        self.assertEqual(sum(Decimal(x['reserved_usd']) for x in ledger['attempts'].values()),Decimal('10.406235'))
        self.assertEqual(sum(len(x['keys']) for x in ledger['attempts'].values()),8832)
        self.assertFalse(o.read(self.state/'operations.json')['halted'])

    def test_canonical_predicate_legacy_contradiction(self):
        keys=o._keys(self.data,'controls')
        for version in [self.version,'SYNTHETIC-wrong']:
            report=reconcile(keys,t.normalize_inline(self.operation(rows=self.rows(version=version))),self.traces,self.design['identities'],True,self.version)
            self.assertTrue(report['controls_pass'])
            self.assertEqual(o.report_allows(report,keys,self.version,True),version==self.version)
        report['stop_future_submissions']=False
        self.assertFalse(o.report_allows(report,keys,self.version,True))

    def test_version_mismatch_controls_stop_and_no_main(self):
        self.submit()
        report=self.recover(self.operation(rows=self.rows(version='SYNTHETIC-wrong')))
        self.assertFalse(report['controls_pass'])
        self.assertTrue(report['stop_future_submissions'])
        self.assert_main_blocked()

    def test_failed_control(self):
        self.submit();rows=self.rows()
        rows[0]['response']['candidates'][0]['finishReason']='MAX_TOKENS'
        report=self.recover(self.operation(rows=rows))
        self.assertFalse(report['controls_pass']);self.assert_main_blocked()

    def test_semantically_wrong_control(self):
        self.submit();rows=self.rows()
        positive=next(r for r in rows if self.traces[r['metadata']['key']]['expected_vendor'])
        positive['response']['candidates'][0]['content']['parts'][0]['text']=json.dumps({'decision':'abstain','recommendations':[],'explanation':'SYNTHETIC'})
        self.recover(self.operation(rows=rows));self.assert_main_blocked()

    def test_pending_then_success(self):
        self.submit()
        report=self.recover(self.operation(status='RUNNING'))
        self.assertFalse(report['terminal']);self.assert_main_blocked()
        self.recover(self.operation());self.submit('main-00','main-attempt')

    def test_ambiguous_terminal_flag(self):
        self.submit();raw=self.operation();raw['done']=False
        with self.assertRaises(RuntimeError):self.recover(raw)
        self.assert_main_blocked()

    def test_incomplete_canonical_reports(self):
        for report in [{},{'controls_pass':True},{'controls_pass':True,'stop_future_submissions':False}]:
            self.assertFalse(o.report_allows(report,o._keys(self.data,'controls'),self.version,True))

    def test_caller_boolean_cannot_skip_controls(self):
        self.assert_main_blocked()
        self.assertFalse((self.state/'budget.json').exists())

    def test_unknown_version_and_launch_gate_refused(self):
        for key in ['expected_model_version','launch_authorized']:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as folder:
                self.state=Path(folder)/'state';gates=dict(self.gates);gates.pop(key)
                with self.assertRaises(ValueError):t.send_once(self.data,self.state,'controls','a',self.receipt,gates,lambda *a:self.fail('Network forbidden'))

    def test_duplicate_attempt_and_same_shard_new_attempt(self):
        self.submit();self.recover(self.operation())
        for attempt in ['control-attempt','new-name']:
            with self.assertRaises(ValueError):self.submit(attempt=attempt)
        self.assertEqual(len(self.calls),1)

    def test_timeout_restart_no_resubmission(self):
        calls=[]
        def fail(*args):calls.append(args);raise TimeoutError()
        with self.assertRaises(RuntimeError):self.submit(provider=fail)
        for attempt in ['control-attempt','new-attempt']:
            with self.assertRaises(ValueError):self.submit(attempt=attempt)
        self.assertEqual(len(calls),1)
        self.assertEqual(len(o.read(self.state/'budget.json')['attempts']),1)

    def test_pending_main_blocks_next_main(self):
        self.submit();self.recover(self.operation());self.submit('main-00','main0')
        with self.assertRaises(ValueError):self.submit('main-01','main1')

    def test_out_of_order_main_blocked(self):
        self.submit();self.recover(self.operation())
        with self.assertRaises(ValueError):self.submit('main-01','main1')

    def test_recovery_idempotent_duplicate_results_not_accounted_twice(self):
        self.submit();rows=self.rows();rows.append(copy.deepcopy(rows[0]))
        raw=self.operation(rows=rows)
        first=self.recover(raw);journal=(self.state/'operations.json').read_bytes();ledger=(self.state/'budget.json').read_bytes()
        second=self.recover(raw)
        self.assertEqual(first,second);self.assertEqual(len(second['records']),24)
        self.assertEqual(journal,(self.state/'operations.json').read_bytes())
        self.assertEqual(ledger,(self.state/'budget.json').read_bytes())

    def test_late_partial_results_preserved_without_lifting_stop(self):
        self.submit();rows=self.rows()
        first=self.recover(self.operation(rows=rows[:12]));self.assertTrue(first['stop_future_submissions'])
        second=self.recover(self.operation(rows=rows[12:]));self.assertEqual(sum(r['status']=='valid' for r in second['records'].values()),24)
        self.assertTrue(second['stop_future_submissions']);self.assert_main_blocked()

    def test_conflicting_late_response_blocks_future(self):
        self.submit();self.recover(self.operation());rows=self.rows()
        rows[0]['response']['usageMetadata']['candidatesTokenCount']=31
        report=self.recover(self.operation(rows=rows))
        self.assertIn('conflicting_duplicate',{r['status'] for r in report['records'].values()})
        self.assert_main_blocked()

    def test_quarantine_even_when_all_controls_semantically_pass(self):
        self.submit();rows=self.rows();rows.append({'metadata':{'key':'unknown'},'error':{'code':1}})
        report=self.recover(self.operation(rows=rows));self.assertFalse(report['controls_pass']);self.assert_main_blocked()

    def test_missing_usage_and_exceeded_output_cap(self):
        for kind in ['missing','exceeded']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                self.state=Path(folder)/'state';self.submit();rows=self.rows()
                if kind=='missing':rows[0]['response'].pop('usageMetadata')
                else:rows[0]['response']['usageMetadata']['thoughtsTokenCount']=1201
                self.recover(self.operation(rows=rows));self.assert_main_blocked()

    def test_job_failure_cancel_expiry_and_partial_errors(self):
        for status in ['FAILED','CANCELLED','EXPIRED']:
            with self.subTest(status=status),tempfile.TemporaryDirectory() as folder:
                self.state=Path(folder)/'state';self.submit()
                self.recover(self.operation(status=status));self.assert_main_blocked()

    def test_wrong_job_and_malformed_output(self):
        for kind in ['wrong_id','file_output','bad_state']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                self.state=Path(folder)/'state';self.submit();raw=self.operation()
                if kind=='wrong_id':raw['name']='batches/unrelated'
                elif kind=='file_output':raw['response']={'responsesFile':'files/synthetic'}
                else:raw['metadata']['state']='NEW_UNKNOWN_STATE'
                with self.assertRaises(RuntimeError):self.recover(raw)
                self.assert_main_blocked()

    def test_get_failure_retains_reservation_and_blocks(self):
        self.submit();ledger=(self.state/'budget.json').read_bytes()
        with self.assertRaises(RuntimeError):o.recover_once(self.data,self.state,'control-attempt',lambda *a:(_ for _ in ()).throw(TimeoutError()))
        self.assertEqual(ledger,(self.state/'budget.json').read_bytes());self.assert_main_blocked()

    def uncertain(self):
        with self.assertRaises(RuntimeError):self.submit(provider=lambda *a:(_ for _ in ()).throw(TimeoutError()))
        journal=o.read(self.state/'operations.json')
        return o._archived(self.state,journal['attempts']['control-attempt']['request'],'request')['batch']['displayName']

    def test_locate_paginated_exact_identity_then_get(self):
        display=self.uncertain();calls=[]
        def listing(path):
            calls.append(path)
            if len(calls)==1:return {'operations':[],'nextPageToken':'next/a+b'}
            return {'operations':[{'name':'batches/control-attempt','metadata':{'displayName':display,'model':'models/'+t.MODEL}}]}
        self.assertEqual(o.locate_once(self.data,self.state,'control-attempt',listing),'batches/control-attempt')
        self.assertIn('next%2Fa%2Bb',calls[1])
        self.assertEqual(o.locate_once(self.data,self.state,'control-attempt',lambda *a:self.fail('No second list')),'batches/control-attempt')
        self.recover(self.operation());self.submit('main-00','main-attempt')

    def test_list_zero_multiple_wrong_model_and_unreachable_stay_uncertain(self):
        for kind in ['zero','multiple','model','unreachable','unsupported','page_limit']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                self.state=Path(folder)/'state';display=self.uncertain()
                op={'name':'batches/a','metadata':{'displayName':display,'model':'models/'+t.MODEL}}
                raw={'operations':[op]}
                if kind=='zero':raw={'operations':[]}
                if kind=='multiple':raw['operations'].append(dict(op,name='batches/b'))
                if kind=='model':op['metadata']['model']='models/other'
                if kind=='unreachable':raw['unreachable']=['somewhere']
                if kind=='page_limit':raw['nextPageToken']='more'
                def listing(path):
                    if kind=='unsupported':raise NotImplementedError()
                    return raw
                with self.assertRaises(RuntimeError):o.locate_once(self.data,self.state,'control-attempt',listing,max_pages=1)
                self.assert_main_blocked()

    def test_cancel_once_timeout_and_late_success_remain_halted(self):
        self.submit();calls=[]
        def cancel(path,body):calls.append((path,body));raise TimeoutError()
        with self.assertRaises(RuntimeError):o.cancel_once(self.data,self.state,'control-attempt',cancel)
        o.cancel_once(self.data,self.state,'control-attempt',cancel)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0],('batches/control-attempt:cancel',{}))
        report=self.recover(self.operation());self.assertTrue(report['stop_future_submissions']);self.assert_main_blocked()

    def test_cancel_acknowledgement_is_not_terminal(self):
        self.submit();result=o.cancel_once(self.data,self.state,'control-attempt',lambda *a:{})
        self.assertFalse(result['terminal_verified']);self.assert_main_blocked()

    def test_crash_after_create_archive_recovers_without_post(self):
        with patch.object(o,'_bind',side_effect=OSError('SYNTHETIC crash')):
            with self.assertRaises(RuntimeError):self.submit()
        self.recover(self.operation())
        self.assertEqual(len(self.calls),1)
        self.assertEqual(o.read(self.state/'budget.json')['attempts']['control-attempt']['provider_job'],'batches/control-attempt')

    def test_orphan_budget_refuses_new_submission(self):
        self.state.mkdir();o.save_json(self.state/'budget.json',{'attempts':{'orphan':{}}})
        with self.assertRaises(ValueError):self.submit()
        self.assertEqual(self.calls,[])

    def test_stale_lock_requires_manual_review(self):
        lock=self.state/'orchestration-lock';lock.mkdir(parents=True);(lock/'runner.lock').write_text('SYNTHETIC')
        with self.assertRaises(FileExistsError):self.submit()
        self.assertEqual(self.calls,[])

    def test_archive_tampering_blocks_main(self):
        self.submit();self.recover(self.operation());j=o.read(self.state/'operations.json')
        ref=j['attempts']['control-attempt']['report'];(self.state/'archive'/f'{ref}.json').write_text('{}')
        self.assert_main_blocked()

    def test_runtime_cannot_write_into_sealed_package(self):
        with self.assertRaises(ValueError):t.send_once(self.data,t.BASE/'runtime','controls','a',self.receipt,self.gates,lambda *a:self.fail('Network forbidden'))

    def test_changed_expected_version_cannot_admit_main(self):
        self.submit();self.recover(self.operation());self.gates['expected_model_version']='different'
        self.assert_main_blocked()

    def test_all_authorization_gates_fail_before_post(self):
        for key,value in self.gates.items():
            if value is not True:continue
            with self.subTest(gate=key),tempfile.TemporaryDirectory() as folder:
                gates=dict(self.gates);gates[key]=False
                with self.assertRaises(ValueError):t.send_once(self.data,Path(folder)/'state','controls','a',self.receipt,gates,lambda *a:self.fail('Closed gate reached provider'))

    def test_local_gate_refusal_leaves_no_phantom_submission(self):
        self.gates['launch_authorized']=False
        with self.assertRaises(ValueError):self.submit()
        self.gates['launch_authorized']=True
        self.submit()
        self.assertEqual(len(self.calls),1)

    def test_concurrent_submission_blocked_while_post_is_inflight(self):
        import threading
        entered=threading.Event();release=threading.Event();errors=[]
        def provider(path,body):
            self.calls.append(path);entered.set()
            if not release.wait(5):raise TimeoutError('Test synchronization failed')
            return {'name':'batches/control-attempt'}
        def first():
            try:self.submit(provider=provider)
            except Exception as exc:errors.append(exc)
        worker=threading.Thread(target=first);worker.start()
        try:
            self.assertTrue(entered.wait(5))
            with self.assertRaises(FileExistsError):self.submit(attempt='concurrent')
        finally:release.set();worker.join(5)
        self.assertFalse(worker.is_alive());self.assertEqual(errors,[]);self.assertEqual(len(self.calls),1)

    def test_crash_after_reservation_before_post_never_retries(self):
        real_save=o._save
        def crash(state,journal):
            if any(i['phase']=='PREPARED_UNCERTAIN' for i in journal['attempts'].values()):raise OSError('SYNTHETIC disk failure')
            real_save(state,journal)
        with patch.object(o,'_save',side_effect=crash):
            with self.assertRaises(OSError):self.submit()
        with self.assertRaises(ValueError):self.submit()
        self.assertEqual(self.calls,[])
        self.assertEqual(len(o.read(self.state/'budget.json')['attempts']),1)

    def test_crash_between_journal_bind_and_budget_metadata_is_repaired(self):
        real_save=o.save_json
        def crash(path,value):
            if Path(path).name=='budget.json' and value['attempts']['control-attempt'].get('provider_job'):raise OSError('SYNTHETIC disk failure')
            real_save(path,value)
        with patch.object(o,'save_json',side_effect=crash):
            with self.assertRaises(RuntimeError):self.submit()
        self.recover(self.operation())
        self.assertEqual(o.read(self.state/'budget.json')['attempts']['control-attempt']['provider_job'],'batches/control-attempt')
        self.assertEqual(len(self.calls),1)

    def test_bad_snapshot_does_not_prevent_archiving_later_valid_results(self):
        self.submit();raw=self.operation();raw['metadata']['state']='UNKNOWN'
        with self.assertRaises(RuntimeError):self.recover(raw)
        report=self.recover(self.operation())
        self.assertEqual(sum(r['status']=='valid' for r in report['records'].values()),24)
        self.assertEqual(len(report['observation_errors']),1)
        self.assertTrue(report['stop_future_submissions']);self.assert_main_blocked()

    def test_contradictory_batch_stats_block_main(self):
        self.submit();raw=self.operation()
        raw['metadata']['batchStats']={'requestCount':'24','successfulRequestCount':'23','failedRequestCount':'1'}
        report=self.recover(raw)
        self.assertTrue(report['batch_stats_inconsistent']);self.assert_main_blocked()

    def test_budget_job_identity_conflict_is_not_overwritten(self):
        self.submit();ledger=o.read(self.state/'budget.json');ledger['attempts']['control-attempt']['provider_job']='batches/other'
        o.save_json(self.state/'budget.json',ledger)
        with self.assertRaises(ValueError):self.recover(self.operation())
        self.assertEqual(o.read(self.state/'budget.json'),ledger);self.assert_main_blocked()

    def test_in_progress_version_error_halts_even_if_later_successful(self):
        self.submit();rows=self.rows(version='SYNTHETIC-wrong')[:1]
        self.recover(self.operation(status='RUNNING',rows=rows))
        self.recover(self.operation());self.assert_main_blocked()


if __name__=='__main__':
    unittest.main(verbosity=2)
