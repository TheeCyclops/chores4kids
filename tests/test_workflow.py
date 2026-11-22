"""Backend regression tests; isolated from live household storage."""
import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import unittest
from unittest.mock import AsyncMock

from test_rollover import storage


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = storage.KidsChoresStore(None)
        self.store.children = [storage.Child('x', 'Xander', points=70), storage.Child('d', 'Dad', points=25)]
        self.store.items = [storage.ShopItem('reward', 'Movie', 10)]
        self.store.purchases = [storage.Purchase('purchase', 'x', 'reward', 'Movie', 10)]
        self.store.tasks = [storage.Task('legacy', 'Old chore', 5, assigned_to='x')]
        self.store.async_save = AsyncMock()
        self.w = self.store.workflow
        self.now = datetime(2026, 11, 23, 8, tzinfo=timezone.utc)
        self.w.now = lambda: self.now
        self.serial = 0

    async def act(self, action, **payload):
        self.serial += 1
        return await self.w.execute(action, dict(request_id=str(self.serial), **payload))

    async def activate(self):
        await self.act('activate', protected_digest=self.w.digest(), backup_verified=True, backup_id='private-backup')

    def schedule(self, **values):
        return dict(anchor='2026-11-23', due_time='07:30', unit='days', every=1, **values)

    async def chore(self, **values):
        return await self.act('save_chore', title='Feed dogs', points=3, assignee='x',
                              schedule=values.pop('schedule', self.schedule()), **values)

    async def routine(self, **values):
        return await self.act('save_routine', title='Morning', people=['x'], weekdays=[0, 1, 2, 3, 4],
                              start_time='06:00', finish_time='08:30', bonus=5,
                              steps=[dict(id='a', title='Dress', points=1), dict(id='b', title='Bag', points=1)], **values)

    def occurrence(self):
        return next(iter(self.w.data['occurrences'].values()))

    def routine_run(self):
        return next(iter(self.w.data['runs'].values()))

    async def test_activation_preserves_all_protected_records_and_legacy(self):
        before = self.w.protected()
        tasks = deepcopy(self.store.tasks)
        await self.activate()
        self.assertEqual(before, self.w.protected())
        self.assertEqual(tasks, self.store.tasks)
        self.assertEqual(self.w.data['activation']['protected'], before)
        await self.store.daily_rollover()
        self.assertEqual(tasks, self.store.tasks)

    async def test_activation_requires_matching_snapshot(self):
        with self.assertRaises(ValueError):
            await self.act('activate', protected_digest='wrong', backup_verified=True, backup_id='backup')
        self.assertFalse(self.w.data['active'])

    async def test_inactive_workflow_rejects_writes(self):
        with self.assertRaisesRegex(ValueError, 'not_active'):
            await self.chore()

    async def test_overdue_takeover_awards_only_after_approval(self):
        await self.activate()
        await self.chore()
        o = self.occurrence()
        await self.act('submit_chore', id=o['id'], child_id='d')
        self.assertEqual(self.store.children[1].points, 25)
        self.assertEqual(o['original_assignee'], 'x')
        await self.act('review_chore', id=o['id'], decision='approve')
        self.assertEqual([c.points for c in self.store.children], [70, 28])

    async def test_reserved_before_due(self):
        await self.activate()
        self.now = self.now.replace(hour=7)
        await self.chore()
        with self.assertRaisesRegex(ValueError, 'reserved'):
            await self.act('submit_chore', id=self.occurrence()['id'], child_id='d')

    async def test_pending_cannot_be_taken_and_rejection_reopens(self):
        await self.activate()
        await self.chore()
        oid = self.occurrence()['id']
        await self.act('submit_chore', id=oid, child_id='d')
        with self.assertRaisesRegex(ValueError, 'not_open'):
            await self.act('submit_chore', id=oid, child_id='x')
        await self.act('review_chore', id=oid, decision='reject')
        o = self.w.data['occurrences'][oid]
        self.assertEqual(o['assignee'], 'x')
        self.assertIsNone(o['completed_by'])
        self.assertEqual([c.points for c in self.store.children], [70, 25])

    async def test_one_outstanding_across_many_missed_dates(self):
        await self.activate()
        await self.chore()
        self.now = self.now.replace(month=12, day=23)
        await self.act('tick')
        self.assertEqual(len(self.w.data['occurrences']), 1)

    async def test_concurrent_submissions_only_one_wins(self):
        await self.activate()
        await self.chore()
        oid = self.occurrence()['id']
        results = await asyncio.gather(self.act('submit_chore', id=oid, child_id='d'),
                                       self.act('submit_chore', id=oid, child_id='x'), return_exceptions=True)
        self.assertEqual(sum(isinstance(r, ValueError) for r in results), 1)

    async def test_approval_retry_and_restart_do_not_double_award(self):
        await self.activate()
        await self.chore()
        oid = self.occurrence()['id']
        await self.act('submit_chore', id=oid, child_id='d')
        payload = dict(request_id='approval', id=oid, decision='approve')
        await asyncio.gather(self.w.execute('review_chore', payload), self.w.execute('review_chore', payload))
        saved = deepcopy(self.w.data)
        self.w.data = saved
        await self.w.execute('review_chore', payload)
        self.assertEqual(self.store.children[1].points, 28)

    async def test_failed_save_rolls_back_points_and_ledger(self):
        await self.activate()
        await self.routine()
        before = deepcopy(self.w.data)
        self.store.async_save.side_effect = OSError('disk full')
        with self.assertRaises(OSError):
            await self.act('check_step', run_id=self.routine_run()['id'], step_id='a')
        self.assertEqual(self.w.data, before)
        self.assertEqual(self.store.children[0].points, 70)

    async def test_step_immediate_bonus_only_parent_approved(self):
        await self.activate()
        await self.routine()
        rid = self.routine_run()['id']
        await self.act('check_step', run_id=rid, step_id='a')
        await self.act('check_step', run_id=rid, step_id='a')
        self.assertEqual(self.store.children[0].points, 71)
        await self.act('check_step', run_id=rid, step_id='b')
        self.assertEqual(self.store.children[0].points, 72)
        await self.act('review_routine', run_id=rid, decision='approve')
        self.assertEqual(self.store.children[0].points, 77)

    async def test_late_steps_keep_partial_points_without_bonus(self):
        await self.activate()
        await self.routine()
        rid = self.routine_run()['id']
        await self.act('check_step', run_id=rid, step_id='a')
        self.now = self.now.replace(hour=9)
        await self.act('check_step', run_id=rid, step_id='b')
        self.assertEqual(self.routine_run()['bonus_status'], 'late')
        self.assertEqual(self.store.children[0].points, 72)
        with self.assertRaises(ValueError):
            await self.act('review_routine', run_id=rid, decision='approve')

    async def test_reset_closes_partial_without_deducting_points(self):
        await self.activate()
        await self.routine()
        rid = self.routine_run()['id']
        await self.act('check_step', run_id=rid, step_id='a')
        self.now = self.now.replace(day=24)
        await self.act('tick')
        self.assertTrue(self.w.data['runs'][rid]['closed'])
        self.assertEqual(self.store.children[0].points, 71)
        self.assertEqual(len(self.w.data['runs']), 2)
        with self.assertRaises(ValueError):
            await self.act('check_step', run_id=rid, step_id='b')

    async def test_bonus_can_be_approved_after_next_run(self):
        await self.activate()
        await self.routine()
        rid = self.routine_run()['id']
        for step in ('a', 'b'):
            await self.act('check_step', run_id=rid, step_id=step)
        self.now = self.now.replace(day=24)
        await self.act('tick')
        await self.act('review_routine', run_id=rid, decision='approve')
        self.assertEqual(self.store.children[0].points, 77)

    async def test_rejected_bonus_does_not_remove_step_points(self):
        await self.activate()
        await self.routine()
        rid = self.routine_run()['id']
        for step in ('a', 'b'):
            await self.act('check_step', run_id=rid, step_id=step)
        await self.act('review_routine', run_id=rid, decision='reject')
        self.assertEqual(self.store.children[0].points, 72)

    async def test_edit_definition_does_not_change_current_occurrence(self):
        await self.activate()
        definition = await self.chore()
        original = deepcopy(self.occurrence())
        await self.act('save_chore', **{**definition, 'title': 'Updated', 'points': 10})
        self.assertEqual(self.occurrence(), original)

    async def test_completion_interval_uses_submission_not_approval(self):
        await self.activate()
        await self.chore(schedule={**self.schedule(), 'basis': 'completion', 'unit': 'months'})
        oid = self.occurrence()['id']
        await self.act('submit_chore', id=oid, child_id='x')
        self.now = self.now.replace(day=30)
        await self.act('review_chore', id=oid, decision='approve')
        self.assertEqual(next(iter(self.w.data['definitions'].values()))['next_due'], '2026-12-23')

    async def test_month_end_and_quarterly(self):
        schedule = self.w.schedule({**self.schedule(), 'anchor': '2026-01-31', 'unit': 'months', 'every': 3})
        from datetime import date
        self.assertEqual(self.w.next_day(schedule, date(2026, 2, 1)).isoformat(), '2026-04-30')
        self.assertEqual(self.w.next_day(schedule, date(2026, 5, 1)).isoformat(), '2026-07-31')

    async def test_opening_window_and_no_premature_occurrence(self):
        await self.activate()
        await self.chore(schedule={**self.schedule(), 'anchor': '2026-12-01', 'lead_days': 2})
        self.assertFalse(self.w.snapshot()['eligible'])
        self.now = self.now.replace(day=29)
        await self.act('tick')
        self.assertEqual(len(self.w.snapshot()['eligible']), 1)

    async def test_legacy_mutations_rejected_rewards_retained(self):
        await self.activate()
        for action in (self.store.reset_points(), self.store.approve_task('legacy'), self.store.assign_task('legacy', 'd')):
            with self.assertRaisesRegex(ValueError, 'legacy'):
                await action
        await self.store.buy_shop_item('x', 'reward')
        self.assertEqual(self.store.children[0].points, 60)
        self.assertEqual(len(self.store.purchases), 2)

    async def test_audited_parent_correction_records_previous_balance(self):
        await self.activate()
        await self.act('adjust_points', child_id='x', amount=-1, reason='Duplicate real-world check')
        entry = next(iter(self.w.data['ledger'].values()))
        self.assertEqual((entry['before'], entry['after']), (70, 69))

    async def test_snapshot_excludes_balance_backup_and_receipts(self):
        await self.activate()
        snapshot = self.w.snapshot()
        self.assertNotIn('activation', snapshot)
        self.assertNotIn('ledger', snapshot)
        self.assertNotIn('requests', snapshot)

    async def test_stale_edit_rejected(self):
        await self.activate()
        definition = await self.chore()
        with self.assertRaisesRegex(ValueError, 'revision_conflict'):
            await self.act('save_chore', **{**definition, 'revision': 0})

    async def test_request_id_cannot_be_reused_for_other_action(self):
        await self.activate()
        await self.w.execute('adjust_points', dict(request_id='unique', child_id='x', amount=1, reason='Test'))
        with self.assertRaisesRegex(ValueError, 'request_id_conflict'):
            await self.w.execute('adjust_points', dict(request_id='unique', child_id='x', amount=100, reason='Test'))

    async def test_edit_after_approval_does_not_recreate_old_occurrence(self):
        await self.activate()
        definition = await self.chore()
        oid = self.occurrence()['id']
        await self.act('submit_chore', id=oid, child_id='x')
        await self.act('review_chore', id=oid, decision='approve')
        definition = self.w.data['definitions'][definition['id']]
        await self.act('save_chore', **{**definition, 'title': 'Renamed'})
        self.assertEqual(len(self.w.data['occurrences']), 1)

    async def test_approval_delay_does_not_generate_backlog(self):
        await self.activate()
        await self.chore()
        oid = self.occurrence()['id']
        await self.act('submit_chore', id=oid, child_id='x')
        self.now = self.now.replace(month=12, day=23)
        await self.act('tick')
        self.assertEqual(len(self.w.data['occurrences']), 1)
        await self.act('review_chore', id=oid, decision='approve')
        await self.act('tick')
        self.assertEqual(len(self.w.data['occurrences']), 1)

    async def test_routine_step_order_and_run_snapshot_survive_edits(self):
        await self.activate()
        routine = await self.routine()
        await self.act('save_routine', **{**routine, 'steps': list(reversed(routine['steps']))})
        self.assertEqual([s['id'] for s in self.routine_run()['steps']], ['a', 'b'])
        self.assertEqual([s['id'] for s in self.w.data['routines'][routine['id']]['steps']], ['b', 'a'])

    async def test_two_people_have_independent_routine_awards(self):
        await self.activate()
        routine = await self.routine()
        await self.act('save_routine', **{**routine, 'people': ['x', 'd']})
        runs = list(self.w.data['runs'].values())
        self.assertEqual(len(runs), 2)
        for run in runs:
            await self.act('check_step', run_id=run['id'], step_id='a')
        self.assertEqual([c.points for c in self.store.children], [71, 26])

    async def test_failed_reward_save_restores_balance_and_purchases(self):
        await self.activate()
        self.store.async_save.side_effect = OSError('disk full')
        with self.assertRaises(OSError):
            await self.store.buy_shop_item('x', 'reward')
        self.assertEqual(self.store.children[0].points, 70)
        self.assertEqual(len(self.store.purchases), 1)

    async def test_timezone_deadlines_follow_wall_clock(self):
        from datetime import date
        from zoneinfo import ZoneInfo
        from test_rollover import dt
        old = getattr(dt, 'DEFAULT_TIME_ZONE', None)
        dt.DEFAULT_TIME_ZONE = ZoneInfo('America/Chicago')
        try:
            self.assertEqual(self.w.local(date(2026, 3, 8), '02:30').hour, 3)
            self.assertEqual(self.w.local(date(2026, 11, 1), '01:30').fold, 0)
            self.assertNotEqual(self.w.local(date(2026, 3, 7), '07:30').utcoffset(), self.w.local(date(2026, 3, 8), '07:30').utcoffset())
        finally:
            if old is None:
                del dt.DEFAULT_TIME_ZONE
            else:
                dt.DEFAULT_TIME_ZONE = old

    async def test_routine_award_and_reward_purchase_share_write_lock(self):
        await self.activate()
        await self.routine()
        async def delayed_save():
            await asyncio.sleep(0.001)
        self.store.async_save.side_effect = delayed_save
        await asyncio.gather(self.act('check_step', run_id=self.routine_run()['id'], step_id='a'),
                             self.store.buy_shop_item('x', 'reward'))
        self.assertEqual(self.store.children[0].points, 61)
        self.assertEqual(len(self.store.purchases), 2)

    async def test_bad_step_is_rejected_without_award(self):
        await self.activate()
        await self.routine()
        with self.assertRaisesRegex(ValueError, 'step_not_found'):
            await self.act('check_step', run_id=self.routine_run()['id'], step_id='missing')
        self.assertEqual(self.store.children[0].points, 70)

    async def test_weekday_selection_and_once_completion(self):
        from datetime import date
        schedule = self.w.schedule({**self.schedule(), 'unit': 'weeks', 'weekdays': [1, 3]})
        self.assertEqual(self.w.next_day(schedule), date(2026, 11, 24))
        self.assertEqual(self.w.next_day(schedule, date(2026, 11, 24)), date(2026, 11, 26))
        await self.activate()
        await self.chore(schedule={**self.schedule(), 'once': True})
        oid = self.occurrence()['id']
        await self.act('submit_chore', id=oid, child_id='x')
        await self.act('review_chore', id=oid, decision='approve')
        self.assertIsNone(next(iter(self.w.data['definitions'].values()))['next_due'])


if __name__ == '__main__':
    unittest.main()
