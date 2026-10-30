"""Rollover regression tests with an in-memory HA storage/clock boundary."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parents[1]
for name in ('homeassistant', 'homeassistant.core', 'homeassistant.helpers',
             'homeassistant.helpers.storage', 'homeassistant.util', 'homeassistant.util.dt'):
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules['homeassistant.core'].HomeAssistant = object
sys.modules['homeassistant.helpers.storage'].Store = lambda *a: types.SimpleNamespace(async_save=AsyncMock())
dt = sys.modules['homeassistant.util.dt']
dt.now = lambda: datetime(2026, 10, 30, 0, 5, tzinfo=timezone.utc)
dt.parse_datetime = datetime.fromisoformat
dt.as_local = lambda value: value.astimezone(timezone.utc)
sys.modules['homeassistant.util'].dt = dt
package = types.ModuleType('rollover_subject')
package.__path__ = [str(ROOT / 'custom_components/chores4kids')]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location('rollover_subject.storage', Path(package.__path__[0]) / 'storage.py')
storage = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = storage
spec.loader.exec_module(storage)


class RolloverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = storage.KidsChoresStore(types.SimpleNamespace())
        self.store.async_save = AsyncMock()
        self.store.children = [storage.Child('kid', 'Test', points=25)]
        self.template = storage.Task('tpl', 'Chore', 5, repeat_days=[4], repeat_child_ids=['kid'])
        self.store.tasks = [self.template]
        async def add(**kwargs):
            task = storage.Task(str(len(self.store.tasks)), created=dt.now().isoformat(), **kwargs)
            self.store.tasks.append(task)
            await self.store.async_save()
            return task
        self.store.add_task = add

    async def test_concurrent_and_same_day_calls(self):
        await asyncio.gather(self.store.daily_rollover(), self.store.daily_rollover())
        self.assertEqual(len(self.store.tasks), 2)
        self.assertFalse(await self.store.daily_rollover())

    async def test_failure_after_creation_then_completion_is_not_duplicated(self):
        self.store.async_save.side_effect = [RuntimeError('disk'), None, None]
        with self.assertRaises(RuntimeError):
            await self.store.daily_rollover()
        self.assertIsNone(self.store._last_rollover_date)
        self.store.tasks[-1].status = storage.STATUS_APPROVED
        await self.store.daily_rollover()
        self.assertEqual(len(self.store.tasks), 2)
        self.assertEqual(self.store.children[0].points, 25)

    async def test_old_approval_and_persistent_assignments_survive(self):
        yesterday = (dt.now() - timedelta(days=1)).isoformat()
        pending = storage.Task('pending', 'Chore', 5, assigned_to='kid', created=yesterday,
                               status=storage.STATUS_AWAITING, repeat_template_id='tpl')
        carry = storage.Task('carry', 'Other', 5, assigned_to='kid', created=yesterday,
                             persist_until_completed=True)
        expired = storage.Task('expired', 'Old', 5, assigned_to='kid', created=yesterday)
        self.store.tasks.extend([pending, carry, expired])
        await self.store.daily_rollover()
        self.assertEqual({t.id for t in self.store.tasks}, {'tpl', 'pending', 'carry'})
        self.assertTrue(carry.carried_over)
        self.assertEqual(self.store.children[0].points, 25)

    async def test_next_local_day_runs_again(self):
        await self.store.daily_rollover()
        original_now = dt.now
        dt.now = lambda: datetime(2026, 10, 31, 0, 5, tzinfo=timezone.utc)
        try:
            self.assertTrue(await self.store.daily_rollover())
            self.assertEqual(self.store.tasks, [self.template])
        finally:
            dt.now = original_now

    async def test_completed_today_survives_restart(self):
        self.store.tasks.append(storage.Task('done', 'Renamed', 5, assigned_to='kid',
                                created=dt.now().isoformat(), status=storage.STATUS_APPROVED,
                                repeat_template_id='tpl'))
        await self.store.daily_rollover()
        self.assertEqual(len(self.store.tasks), 2)


if __name__ == '__main__':
    unittest.main()
