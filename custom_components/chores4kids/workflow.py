"""Versioned chore library and routines; activation never rewrites legacy records."""
from __future__ import annotations

import asyncio
import calendar
from contextlib import asynccontextmanager
from copy import deepcopy
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from functools import wraps
import hashlib
import json
from uuid import uuid4


class WriteLock:
    """One reentrant lock for nested legacy methods and new accounting writes."""

    def __init__(self):
        self.lock = asyncio.Lock()
        self.owner = None

    @asynccontextmanager
    async def held(self):
        owner = asyncio.current_task()
        if self.owner is owner:
            yield
            return
        async with self.lock:
            self.owner = owner
            try:
                yield
            finally:
                self.owner = None


def locked_store_method(method):
    @wraps(method)
    async def guarded(store, *args, **kwargs):
        async with store.workflow_lock.held():
            if store.workflow.data['active'] and method.__name__ in LEGACY_WRITES:
                raise ValueError('legacy_chores_archived_use_workflow')
            before = deepcopy((store.children, store.tasks, store.items, store.purchases, store.categories))
            try:
                return await method(store, *args, **kwargs)
            except BaseException:
                store.children, store.tasks, store.items, store.purchases, store.categories = before
                raise
    return guarded


LEGACY_WRITES = {
    'add_task', 'assign_task', 'set_task_status', 'approve_task', 'delete_task',
    'set_task_repeat', 'set_task_icon', 'update_task', 'set_task_bonus_completed',
    'approve_bonus_task', 'reset_points', 'add_points', 'remove_child', 'clear_shop_history',
}


def integer(value, minimum=0, maximum=100000):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError('invalid_integer')
    return value


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 1000:
        raise ValueError('invalid_text')
    return value.strip()


def clock(value):
    if not isinstance(value, str) or len(value) != 5:
        raise ValueError('invalid_time')
    return time.fromisoformat(value)


def instant(value):
    return value.astimezone(timezone.utc)


def advance(day, schedule):
    """Advance from an anchor, preserving month-end intent without date drift."""
    every = schedule['every']
    if schedule['unit'] == 'months':
        month = day.year * 12 + day.month - 1 + every
        anchor = date.fromisoformat(schedule['anchor']).day
        year, month = divmod(month, 12)
        return date(year, month + 1, min(anchor, calendar.monthrange(year, month + 1)[1]))
    return day + timedelta(days=every * (7 if schedule['unit'] == 'weeks' else 1))


class Workflow:
    def __init__(self, store):
        self.store = store
        self.data = dict(schema_version=2, active=False, definitions={}, occurrences={},
                         routines={}, runs={}, ledger={}, requests={}, activation=None)

    def now(self):
        from homeassistant.util import dt as dt_util
        return dt_util.now()

    def local(self, day, hhmm):
        from homeassistant.util import dt as dt_util
        zone = getattr(dt_util, 'DEFAULT_TIME_ZONE', self.now().tzinfo)
        value = datetime.combine(day, clock(hhmm), tzinfo=zone)
        # Round trips advance nonexistent spring times; ambiguous times use fold=0.
        return value.astimezone(timezone.utc).astimezone(zone)

    def protected(self):
        return dict(children=[asdict(c) for c in self.store.children],
                    items=[asdict(i) for i in self.store.items],
                    purchases=[asdict(p) for p in self.store.purchases])

    def digest(self):
        return hashlib.sha256(json.dumps(self.protected(), sort_keys=True).encode()).hexdigest()

    def child(self, child_id):
        return self.store._get_child(text(child_id))

    def schedule(self, raw):
        if not isinstance(raw, dict):
            raise ValueError('invalid_schedule')
        result = dict(basis=raw.get('basis', 'calendar'), unit=raw.get('unit', 'days'),
                      every=integer(raw.get('every', 1), 1, 1200),
                      anchor=date.fromisoformat(raw['anchor']).isoformat(),
                      due_time=clock(raw['due_time']).strftime('%H:%M'),
                      lead_days=integer(raw.get('lead_days', 0), 0, 3650),
                      weekdays=raw.get('weekdays', []), once=raw.get('once', False))
        if result['basis'] not in ('calendar', 'completion') or result['unit'] not in ('days', 'weeks', 'months'):
            raise ValueError('invalid_schedule')
        if not isinstance(result['once'], bool) or not isinstance(result['weekdays'], list):
            raise ValueError('invalid_schedule')
        result['weekdays'] = sorted(set(integer(v, 0, 6) for v in result['weekdays']))
        if result['weekdays'] and (result['basis'] != 'calendar' or result['unit'] != 'weeks' or result['every'] != 1):
            raise ValueError('weekdays_require_weekly_calendar')
        return result

    def next_day(self, schedule, after=None, completion=None):
        day = date.fromisoformat(schedule['anchor'])
        if completion is not None and schedule['basis'] == 'completion':
            # Completion intervals anchor months to the actual completion day.
            interval = dict(schedule, anchor=completion.isoformat())
            return advance(completion, interval)
        if after is None:
            if schedule['weekdays']:
                while day.weekday() not in schedule['weekdays']:
                    day += timedelta(days=1)
            return day
        if schedule['once']:
            return day if day > after else None
        if schedule['weekdays']:
            day = max(day, after + timedelta(days=1))
            while day.weekday() not in schedule['weekdays']:
                day += timedelta(days=1)
            return day
        while day <= after:
            day = advance(day, schedule)
        return day

    def award(self, key, child_id, points, kind, actor=None):
        if key in self.data['ledger']:
            return
        child = self.child(child_id)
        before = child.points
        self.store._add_earned_points(child, points)
        self.data['ledger'][key] = dict(child_id=child_id, points=points, kind=kind,
                                        before=before, after=child.points, actor=actor, at=self.now().isoformat())

    async def execute(self, action, payload):
        """Atomic in memory and persisted in one save; failed saves restore state."""
        async with self.store.workflow_lock.held():
            request = text(payload.get('request_id'))
            fingerprint = hashlib.sha256(json.dumps([action, payload], sort_keys=True).encode()).hexdigest()
            old = self.data['requests'].get(request)
            if old:
                if old['fingerprint'] != fingerprint:
                    raise ValueError('request_id_conflict')
                return deepcopy(old['result'])
            if not self.data['active'] and action != 'activate':
                raise ValueError('workflow_not_active')
            if action not in ACTIONS:
                raise ValueError('unknown_action')
            before = deepcopy(self.data)
            children = deepcopy(self.store.children)
            try:
                result = getattr(self, action)(payload)
                if action != 'tick':
                    self.data['requests'][request] = dict(fingerprint=fingerprint, result=deepcopy(result))
                await self.store.async_save()
                return deepcopy(result)
            except BaseException:
                self.data = before
                self.store.children = children
                raise

    def activate(self, payload):
        if self.data['active']:
            return {'active': True}
        # Digest is compared to the verified private backup by the activation handler.
        if payload.get('protected_digest') != self.digest() or not payload.get('backup_verified'):
            raise ValueError('verified_backup_required')
        self.data['activation'] = dict(at=self.now().isoformat(), protected=self.protected(),
                                       digest=self.digest(), backup_id=text(payload['backup_id']))
        self.data['active'] = True
        return {'active': True}

    def save_chore(self, payload):
        identifier = payload.get('id') or str(uuid4())
        old = self.data['definitions'].get(identifier)
        if payload.get('id') and not old:
            raise ValueError('chore_not_found')
        if old and payload.get('revision') != old['revision']:
            raise ValueError('revision_conflict')
        owner = payload.get('assignee') or None
        if owner:
            self.child(owner)
        if not isinstance(payload.get('categories', []), list):
            raise ValueError('invalid_categories')
        definition = dict(id=identifier, title=text(payload['title']),
                          description=str(payload.get('description', ''))[:4000],
                          points=integer(payload.get('points', 1)), assignee=owner,
                          categories=list(payload.get('categories', [])),
                          schedule=self.schedule(payload['schedule']),
                          enabled=payload.get('enabled', True), revision=(old or {}).get('revision', 0) + 1)
        if not isinstance(definition['enabled'], bool) or any(not isinstance(c, str) for c in definition['categories']):
            raise ValueError('invalid_chore')
        if old and definition['schedule'] == old['schedule']:
            definition['next_due'] = old['next_due']
        else:
            next_due = self.next_day(definition['schedule'], self.now().date() if old else None)
            definition['next_due'] = next_due.isoformat() if next_due else None
        self.data['definitions'][identifier] = definition
        self.tick({})
        return definition

    def edit_occurrence(self, payload):
        occurrence = self.data['occurrences'][payload['id']]
        if occurrence['status'] != 'open':
            raise ValueError('occurrence_not_open')
        if payload.get('revision') != occurrence['revision']:
            raise ValueError('revision_conflict')
        if 'assignee' in payload:
            owner = payload['assignee'] or None
            if owner:
                self.child(owner)
            occurrence['assignee'] = owner
        if 'due' in payload:
            due = datetime.fromisoformat(payload['due'])
            if due.tzinfo is None or due < datetime.fromisoformat(occurrence['opens_at']):
                raise ValueError('invalid_due')
            occurrence['due'] = due.isoformat()
        occurrence['revision'] += 1
        return occurrence

    def submit_chore(self, payload):
        occurrence = self.data['occurrences'][payload['id']]
        completer = self.child(payload['child_id']).id
        now = self.now()
        if occurrence['status'] != 'open':
            raise ValueError('occurrence_not_open')
        if instant(now) < instant(datetime.fromisoformat(occurrence['opens_at'])):
            raise ValueError('not_available')
        if occurrence['assignee'] not in (None, completer) and instant(now) <= instant(datetime.fromisoformat(occurrence['due'])):
            raise ValueError('reserved_for_assignee')
        occurrence.update(status='awaiting_approval', completed_by=completer,
                          submitted_at=now.isoformat(), revision=occurrence['revision'] + 1)
        return occurrence

    def review_chore(self, payload):
        occurrence = self.data['occurrences'][payload['id']]
        decision = payload['decision']
        if occurrence['status'] != 'awaiting_approval' or decision not in ('approve', 'reject'):
            raise ValueError('invalid_review')
        if decision == 'reject':
            occurrence.setdefault('rejections', []).append(dict(completed_by=occurrence['completed_by'],
                submitted_at=occurrence['submitted_at'], reviewed_by=payload.get('actor_id'), at=self.now().isoformat()))
            occurrence.update(status='open', completed_by=None, submitted_at=None)
        else:
            self.award('chore:' + occurrence['id'], occurrence['completed_by'], occurrence['points'], 'chore', payload.get('actor_id'))
            occurrence.update(status='approved', approved_at=self.now().isoformat(), approved_by=payload.get('actor_id'))
            definition = self.data['definitions'][occurrence['definition_id']]
            schedule = definition['schedule']
            if schedule['once']:
                day = None
            else:
                completed = datetime.fromisoformat(occurrence['submitted_at']).astimezone(self.now().tzinfo).date()
                day = self.next_day(schedule, self.now().date(), completed)
                interval = dict(schedule, anchor=completed.isoformat()) if schedule['basis'] == 'completion' else schedule
                # An old completion awaiting approval must not regenerate a backlog.
                while day is not None and day <= self.now().date():
                    day = advance(day, interval)
            definition['next_due'] = day.isoformat() if day else None
        occurrence['revision'] += 1
        return occurrence

    def save_routine(self, payload):
        identifier = payload.get('id') or str(uuid4())
        old = self.data['routines'].get(identifier)
        if payload.get('id') and not old:
            raise ValueError('routine_not_found')
        if old and payload.get('revision') != old['revision']:
            raise ValueError('revision_conflict')
        people = list(dict.fromkeys(payload['people']))
        if not people:
            raise ValueError('routine_requires_people')
        for person in people:
            self.child(person)
        steps = []
        for step in payload['steps']:
            chore_id = step.get('chore_id')
            if chore_id and chore_id not in self.data['definitions']:
                raise ValueError('routine_chore_not_found')
            steps.append(dict(id=text(step.get('id') or str(uuid4())), title=text(step['title']),
                              points=integer(step.get('points', 1)),
                              chore_id=chore_id,
                              duration_minutes=integer(step.get('duration_minutes', 0), 0, 1440)))
        if not steps or len(steps) > 100 or len({s['id'] for s in steps}) != len(steps):
            raise ValueError('invalid_steps')
        start, finish = clock(payload['start_time']), clock(payload['finish_time'])
        if start >= finish:
            raise ValueError('routine_must_finish_same_day_after_start')
        weekdays = sorted(set(integer(v, 0, 6) for v in payload['weekdays']))
        if not weekdays:
            raise ValueError('routine_requires_days')
        routine = dict(id=identifier, title=text(payload['title']), people=people, steps=steps,
                       weekdays=weekdays, start_time=start.strftime('%H:%M'), finish_time=finish.strftime('%H:%M'),
                       bonus=integer(payload.get('bonus', 1), 1), enabled=payload.get('enabled', True),
                       revision=(old or {}).get('revision', 0) + 1)
        if not isinstance(routine['enabled'], bool):
            raise ValueError('invalid_routine')
        self.data['routines'][identifier] = routine
        self.tick({})
        return routine

    def tick(self, payload):
        now = self.now()
        for definition in self.data['definitions'].values():
            if not definition['enabled'] or not definition['next_due']:
                continue
            if any(o['definition_id'] == definition['id'] and o['status'] != 'approved'
                   for o in self.data['occurrences'].values()):
                continue
            day = date.fromisoformat(definition['next_due'])
            due = self.local(day, definition['schedule']['due_time'])
            opens = self.local(day - timedelta(days=definition['schedule']['lead_days']), '00:00')
            if now >= opens:
                identifier = str(uuid4())
                self.data['occurrences'][identifier] = dict(id=identifier, definition_id=definition['id'],
                    title=definition['title'], points=definition['points'], assignee=definition['assignee'],
                    original_assignee=definition['assignee'], opens_at=opens.isoformat(), due=due.isoformat(),
                    status='open', completed_by=None, submitted_at=None, revision=1)
        for routine in self.data['routines'].values():
            for person in routine['people']:
                previous = [r for r in self.data['runs'].values() if r['routine_id'] == routine['id'] and r['child_id'] == person]
                if not routine['enabled'] or now.weekday() not in routine['weekdays'] or now < self.local(now.date(), routine['start_time']):
                    continue
                identifier = f"{routine['id']}:{person}:{now.date().isoformat()}"
                if identifier in self.data['runs']:
                    continue
                for run in previous:
                    run['closed'] = True
                    run['outcome'] = 'complete' if len(run['checked']) == len(run['steps']) else 'missed'
                self.data['runs'][identifier] = dict(id=identifier, routine_id=routine['id'], child_id=person,
                    title=routine['title'], steps=deepcopy(routine['steps']), checked={}, closed=False,
                    starts_at=self.local(now.date(), routine['start_time']).isoformat(),
                    finish_at=self.local(now.date(), routine['finish_time']).isoformat(),
                    bonus=routine['bonus'], bonus_status='not_eligible')
        return {'updated_at': now.isoformat()}

    def check_step(self, payload):
        self.tick({})
        run = self.data['runs'][payload['run_id']]
        if run['closed']:
            raise ValueError('routine_run_closed')
        step = next((s for s in run['steps'] if s['id'] == payload['step_id']), None)
        if step is None:
            raise ValueError('routine_step_not_found')
        if step['id'] not in run['checked']:
            self.award(f"step:{run['id']}:{step['id']}", run['child_id'], step['points'], 'routine_step', payload.get('actor_id'))
            run['checked'][step['id']] = self.now().isoformat()
        if len(run['checked']) == len(run['steps']) and run['bonus_status'] == 'not_eligible':
            run['bonus_status'] = ('awaiting_approval' if all(instant(datetime.fromisoformat(t)) <= instant(datetime.fromisoformat(run['finish_at']))
                                    for t in run['checked'].values()) else 'late')
        return run

    def review_routine(self, payload):
        run = self.data['runs'][payload['run_id']]
        if run['bonus_status'] != 'awaiting_approval' or payload['decision'] not in ('approve', 'reject'):
            raise ValueError('invalid_review')
        if payload['decision'] == 'approve':
            self.award('bonus:' + run['id'], run['child_id'], run['bonus'], 'routine_bonus', payload.get('actor_id'))
            run['bonus_status'] = 'approved'
        else:
            run['bonus_status'] = 'rejected'
        run['reviewed_by'] = payload.get('actor_id')
        run['reviewed_at'] = self.now().isoformat()
        return run

    def adjust_points(self, payload):
        child = self.child(payload['child_id'])
        delta = integer(payload['amount'], -100000)
        reason = text(payload['reason'])
        before = child.points
        child.points += delta
        self.data['ledger']['adjust:' + payload['request_id']] = dict(child_id=child.id, points=delta,
            kind='parent_adjustment', reason=reason, before=before, after=child.points,
            actor=payload.get('actor_id'), at=self.now().isoformat())
        return {'balance': child.points}

    def snapshot(self):
        now = self.now()
        result = deepcopy(self.data)
        result.pop('requests')
        result.pop('activation')
        result.pop('ledger')
        result['eligible'] = [dict(o, overdue=instant(now) > instant(datetime.fromisoformat(o['due'])),
                                   available_to_anyone=o['assignee'] is None or instant(now) > instant(datetime.fromisoformat(o['due'])))
                              for o in result['occurrences'].values() if o['status'] == 'open' and instant(now) >= instant(datetime.fromisoformat(o['opens_at']))]
        result['archived_task_count'] = len(self.store.tasks) if result['active'] else 0
        return result


ACTIONS = {'activate', 'save_chore', 'edit_occurrence', 'submit_chore', 'review_chore',
           'save_routine', 'check_step', 'review_routine', 'adjust_points', 'tick'}
