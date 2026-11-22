"""Verify the private-backup gate and HA administrator boundary with HA stubs."""
from copy import deepcopy
import importlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

from test_rollover import storage


class MemoryStore:
    def __init__(self):
        self.data = None

    async def async_save(self, data):
        self.data = deepcopy(data)

    async def async_load(self):
        return deepcopy(self.data)


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = storage.KidsChoresStore(None)
        self.store._store = MemoryStore()
        self.store.children = [storage.Child('x', 'Xander', points=83)]
        self.store.items = [storage.ShopItem('r', 'Reward', 5)]
        self.store.purchases = [storage.Purchase('p', 'x', 'r', 'Reward', 5)]
        self.store._earned_backfill_done = True
        self.backup = MemoryStore()
        core = sys.modules['homeassistant.core']
        core.SupportsResponse = types.SimpleNamespace(ONLY='only', OPTIONAL='optional')
        exceptions = types.ModuleType('homeassistant.exceptions')
        exceptions.HomeAssistantError = RuntimeError
        dispatcher = types.ModuleType('homeassistant.helpers.dispatcher')
        dispatcher.async_dispatcher_send = lambda *args: None
        vol = types.ModuleType('voluptuous')
        vol.Schema = lambda value: value
        vol.Required = lambda value: value
        vol.In = lambda value: value
        modules = patch.dict(sys.modules, {'homeassistant.exceptions': exceptions,
            'homeassistant.helpers.dispatcher': dispatcher, 'voluptuous': vol})
        modules.start()
        self.addCleanup(modules.stop)
        sys.modules.pop('rollover_subject.workflow_services', None)
        self.services = importlib.import_module('rollover_subject.workflow_services')
        self.services.Store = lambda *args: self.backup
        self.handlers = {}
        def register(domain, name, handler, **kwargs):
            self.handlers[name] = handler
        self.hass = types.SimpleNamespace(auth=types.SimpleNamespace(async_get_user=AsyncMock(return_value=types.SimpleNamespace(is_admin=True))),
            services=types.SimpleNamespace(async_register=register))
        self.services.register_workflow_services(self.hass, self.store)

    def call(self, data=None, user='admin'):
        return types.SimpleNamespace(data=data or {}, context=types.SimpleNamespace(user_id=user))

    async def activate(self, receipt):
        return await self.handlers['workflow_action'](self.call(dict(action='activate', payload={
            'request_id': 'activation', 'backup_id': receipt['id'], 'protected_digest': receipt['protected_digest']})))

    async def test_complete_backup_readback_and_activation_preserve_records(self):
        before = self.store.workflow.protected()
        receipt = await self.handlers['prepare_workflow'](self.call())
        self.assertEqual(self.backup.data['balances']['x']['points'], 83)
        self.assertEqual(self.backup.data['data']['purchases'][0]['id'], 'p')
        self.assertNotIn('balances', receipt)
        await self.activate(receipt)
        self.assertEqual(self.store.workflow.protected(), before)
        await self.activate(receipt)

    async def test_changed_balance_invalidates_backup(self):
        receipt = await self.handlers['prepare_workflow'](self.call())
        self.store.children[0].points += 1
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            await self.activate(receipt)
        self.assertFalse(self.store.workflow.data['active'])

    async def test_corrupt_backup_rejected(self):
        receipt = await self.handlers['prepare_workflow'](self.call())
        self.backup.data['data']['children'][0]['points'] = 0
        with self.assertRaisesRegex(RuntimeError, 'checksum'):
            await self.activate(receipt)

    async def test_non_admin_cannot_activate_or_review(self):
        self.hass.auth.async_get_user.return_value.is_admin = False
        with self.assertRaisesRegex(RuntimeError, 'admin_required'):
            await self.handlers['prepare_workflow'](self.call())
        with self.assertRaisesRegex(RuntimeError, 'admin_required'):
            await self.handlers['workflow_action'](self.call(dict(action='review_chore', payload={})))

    async def test_unverified_caller_flag_cannot_activate(self):
        with self.assertRaisesRegex(RuntimeError, 'backup_required'):
            await self.handlers['workflow_action'](self.call(dict(action='activate', payload={
                'request_id': 'bad', 'backup_verified': True, 'protected_digest': self.store.workflow.digest()})))

    async def test_persisted_reload_preserves_balances_and_awards(self):
        receipt = await self.handlers['prepare_workflow'](self.call())
        await self.activate(receipt)
        await self.store.workflow.execute('adjust_points', dict(request_id='correction', child_id='x', amount=2, reason='Test'))
        fresh = storage.KidsChoresStore(None)
        fresh._store = self.store._store
        await fresh.async_load()
        self.assertEqual(fresh.children[0].points, 85)
        self.assertIn('adjust:correction', fresh.workflow.data['ledger'])
        self.assertEqual(fresh.items, self.store.items)
        self.assertEqual(fresh.purchases, self.store.purchases)

    async def test_unknown_schema_refuses_load_without_saving(self):
        self.store._store.data = {'workflow': {'schema_version': 99}}
        fresh = storage.KidsChoresStore(None)
        fresh._store = self.store._store
        with self.assertRaisesRegex(ValueError, 'unsupported_workflow_schema'):
            await fresh.async_load()
        self.assertEqual(self.store._store.data, {'workflow': {'schema_version': 99}})

    async def test_changed_chore_invalidates_full_backup(self):
        receipt = await self.handlers['prepare_workflow'](self.call())
        self.store.tasks.append(storage.Task('later', 'New old chore', 1))
        with self.assertRaisesRegex(RuntimeError, 'storage_changed'):
            await self.activate(receipt)
