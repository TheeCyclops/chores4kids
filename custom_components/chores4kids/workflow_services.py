"""Home Assistant boundary for the version-two workflow."""
from copy import deepcopy
import hashlib
import json
from uuid import uuid4

import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import DOMAIN, SIGNAL_DATA_UPDATED
from .workflow import ACTIONS

PARENT_ACTIONS = ACTIONS - {'submit_chore', 'check_step', 'tick'}


def checksum(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def register_workflow_services(hass, store):
    backup_store = Store(hass, 1, 'chores4kids_workflow_backup')

    async def require_parent(call):
        user = await hass.auth.async_get_user(call.context.user_id) if call.context.user_id else None
        if user is None or not user.is_admin:
            raise HomeAssistantError('workflow_parent_admin_required')

    async def prepare(call):
        await require_parent(call)
        async with store.workflow_lock.held():
            if store.workflow.data['active']:
                raise HomeAssistantError('workflow_already_active')
            await store.async_save()
            original = deepcopy(await store._store.async_load())
            backup = dict(id=str(uuid4()), data=original, checksum=checksum(original),
                          protected_digest=store.workflow.digest(),
                          balances={c.id: {'name': c.name, 'points': c.points} for c in store.children},
                          created_at=store.workflow.now().isoformat())
            await backup_store.async_save(backup)
            if await backup_store.async_load() != backup:
                raise HomeAssistantError('backup_readback_failed')
            return {key: backup[key] for key in ('id', 'checksum', 'protected_digest', 'created_at')}

    async def action(call):
        command = call.data['action']
        if command in PARENT_ACTIONS or command == 'tick':
            await require_parent(call)
        payload = deepcopy(dict(call.data['payload']))
        # These are server assertions, never caller-controlled flags.
        payload.pop('backup_verified', None)
        payload['actor_id'] = call.context.user_id
        async with store.workflow_lock.held():
            if command == 'activate' and store.workflow.data['active']:
                payload['backup_verified'] = True
            if command == 'activate' and not store.workflow.data['active']:
                backup = await backup_store.async_load()
                if not backup or backup['id'] != payload.get('backup_id'):
                    raise HomeAssistantError('backup_required')
                if checksum(backup['data']) != backup['checksum']:
                    raise HomeAssistantError('backup_checksum_mismatch')
                if payload.get('protected_digest') != backup['protected_digest'] or store.workflow.digest() != backup['protected_digest']:
                    raise HomeAssistantError('balances_or_rewards_changed_prepare_again')
                # Also reject chores/settings changed since the snapshot.
                await store.async_save()
                if checksum(await store._store.async_load()) != backup['checksum']:
                    raise HomeAssistantError('storage_changed_prepare_again')
                payload['backup_verified'] = True
            try:
                result = await store.workflow.execute(command, payload)
            except (ValueError, KeyError, TypeError, StopIteration) as error:
                raise HomeAssistantError(str(error)) from error
        async_dispatcher_send(hass, SIGNAL_DATA_UPDATED)
        return {'result': result}

    hass.services.async_register(DOMAIN, 'prepare_workflow', prepare,
                                 schema=vol.Schema({}), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, 'workflow_action', action,
        schema=vol.Schema({vol.Required('action'): vol.In(sorted(ACTIONS)),
                           vol.Required('payload'): dict}), supports_response=SupportsResponse.OPTIONAL)
