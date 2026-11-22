# Chore library and personal routines

Implemented 2026-11-22 in the authoritative Desktop checkout. This is an opt-in
backend and bundled-card capability, not a claim of release, installation,
activation, live balance capture, or MagicMirror integration.

## Protected activation

Existing installations continue using the legacy workflow until explicitly
activated. People, IDs, balances, earned counters, rewards, purchases, categories,
settings and old tasks remain in the existing HA storage. The new `workflow`
extension has its own `schema_version: 2`; the existing HA Store container remains
version 1. Unknown extension versions refuse to load rather than overwrite data.

An authenticated HA administrator calls `chores4kids.prepare_workflow` with service
response enabled. The server writes the complete current store to a separate
private HA Store named `chores4kids_workflow_backup`, including a dated balance
snapshot for every person. It reads the copy back and returns only its `id`,
`checksum`, `protected_digest` and `created_at`. This is a migration recovery copy,
not a complete off-host Home Assistant/VM backup; see [recovery](context/recovery.md).

Before activation, independently retain the recovery copy and verify it can be
read with each child's exact balance, catalog, purchases, and task history intact.
Do not paste this private data into Git or public logs. Call `workflow_action`
with action `activate` and payload containing a unique `request_id`, `backup_id`
(the returned `id`) and returned `protected_digest`. The server verifies the
backup checksum and unchanged complete current storage. Changes since preparation
require preparing again. Callers cannot bypass verification with a boolean flag.
After activation preparation cannot overwrite the baseline backup.

Activation archives old chores logically; it does not delete or convert them.
Legacy task writes, resets, direct point adjustments, child deletion and purchase
history clearing are blocked. Existing reward interfaces remain. Read-only legacy
history is exposed through `archived_tasks` on the existing task sensor and Archive
in the bundled parent card. The task sensor's active `tasks` and child task arrays
are empty once archived; old consumers must upgrade before activation.

Do not downgrade activated storage to old code: an older save could discard the
extension. Recovery requires a matching tested storage backup or a compatible
forward fix. There is intentionally no destructive reset/automatic rollback API.

## Dashboard API

The new workflow sensor has unique ID `chores4kids_workflow_v2`. Discover its
actual entity ID; do not assume an HA-generated slug. Its attributes include
`schema_version`, `active`, `definitions`, `occurrences`, `routines`, `runs`,
`eligible`, and `archived_task_count`. Private activation snapshots, request
receipts and award ledger are excluded. Point and shop sensor IDs stay unchanged.

Use `chores4kids.workflow_action` with `action` and `payload`. Every payload needs
a unique `request_id`; reuse it for a retry of the identical operation. Responses
are optional and contain `result`. Changed content with the same request ID is a
conflict. State and award-key checks also stop duplicate awards with new IDs.

| Action | Required payload beyond request_id |
| --- | --- |
| `save_chore` | `title`, `schedule`; optional `id` + current `revision` for edits, `description`, `points`, `assignee` (person ID or null), `categories` (ID list), `enabled` |
| `edit_occurrence` | `id`, current `revision`; optional `assignee`, offset-aware ISO `due` |
| `submit_chore` | `id` (occurrence), `child_id` (actual completer) |
| `review_chore` | `id`, `decision`: `approve` or `reject` |
| `save_routine` | `title`, `people` (IDs), `weekdays` (0=Monday), `start_time`, `finish_time`, ordered `steps`, `bonus`; optional `id` + `revision`, `enabled` |
| `check_step` | `run_id`, `step_id`; no uncheck operation |
| `review_routine` | `run_id`, `decision`: `approve` or `reject` |
| `adjust_points` | `child_id`, signed integer `amount`, mandatory `reason` |
| `tick` | No extra fields; scheduler reconciliation |

All actions except `submit_chore` and `check_step` require an authenticated HA
administrator at the service boundary. Completing users select a household
person; this is not per-person authentication. MagicMirror must continue enforcing
its parent gate before issuing admin actions through its trusted HA connection.
No token or PIN enters the sensor payload.

Schedule example:

```json
{
  "anchor": "2026-12-01",
  "due_time": "18:00",
  "basis": "calendar",
  "unit": "months",
  "every": 3,
  "lead_days": 7,
  "weekdays": [],
  "once": false
}
```

`basis` is `calendar` or `completion`; `unit` is `days`, `weeks`, or `months`.
Selected weekdays require calendar/every-one-week. `once` disables repetition.
`lead_days` defaults to zero; jobs open at local midnight that many days before
the deadline. A disabled definition is library-only/paused; it does not create
standalone occurrences. Existing open occurrences remain when a schedule pauses.
All times use HA's timezone, with spring-gap times advanced and ambiguous autumn
times using the first occurrence. Month-end intervals preserve the anchor day,
clamped when necessary; quarterly is three calendar months.

An overdue or awaiting-approval occurrence blocks all further copies of its
schedule. Approved jobs advance to the next future date, skipping backlog. A
completion-based interval uses the submission date, not the approval date; if
approval misses several intervals, those elapsed intervals are skipped. Editing
a definition changes future occurrences only. Occurrence edits preserve original
ownership and require the current revision; pending/approved jobs cannot be edited.
The existing startup/midnight/five-minute watchdog reconciles new openings and
routine starts. Sensors compute overdue eligibility from current server time.

Ordinary chores go `open -> awaiting_approval -> approved`, or rejection reopens
the same occurrence. An owner can submit an open job; another person must wait
until strictly past its deadline. Unassigned jobs are available from their opening
time. Original assignee and actual completer remain separate. Only approval awards
the snapshotted points to the completer. Pending jobs cannot be stolen.

## Routine rules

The full-routine bonus is a positive amount added to the combined step points.
Steps contain stable `id`, `title`, `points`, optional `duration_minutes` and optional
`chore_id` reference. The card can add a step from the library or create it directly,
then move it up/down. Library references copy content into the routine; they do
not mark a separate standalone household occurrence complete. Use disabled
definitions for library chores intended only as routine steps.

Each assigned person receives a separate scheduled run with a snapshot of ordered
steps, points and bonus. Checking a step immediately credits that person once.
The ledger retains previous/new balance, amount, award kind and timestamp. No
ordinary uncheck or automatic deduction exists. Parent corrections use
`adjust_points`, recording the reason and exact before/after balances.

All steps checked by the finish time make the extra bonus `awaiting_approval`.
Parent approval awards it once, even after a later run starts. Rejection retains
all step points. Late steps can earn their base points until reset, but cannot
qualify the run for its bonus. Partial/missed runs retain earned points and close
at the next scheduled run's start. Routine steps never become shared takeover jobs.
Routines finish on the same local day after their start; overnight routines are
not supported in this version. The next scheduled run starts fresh. Routine edits
affect future runs, leaving existing runs and pending bonus reviews intact.

## Compatibility and validation

Root and bundled card sources must remain identical. The active-workflow branch
provides Today, library/schedule forms, ordered routine editors, approvals, rewards,
and a read-only archive. Existing card behavior remains when inactive. Existing
reward creation/editing and purchase services are retained; new workflow writes
and legacy store writes share a reentrant lock. Failed saves restore in-memory
awards/balances and reward purchase state rather than acknowledging unsaved work.

Run `python -m unittest discover -s tests -v`. Tests use HA boundary stubs, not an
installed integration. `node tests/browser_workflow.cjs` exercises the actual
bundled card in Chrome with synthetic state. It uses the sibling MagicMirror's
existing Playwright installation (or `PLAYWRIGHT_MODULE`) and the card's existing
Lit CDN import. Screenshots are temporary. No household service calls occur.

Release, HACS installation, backup capture and explicit activation are separate
operations. Before activation update the MagicMirror bridge/UI to consume the new
sensor/services, verify parent gating, and confirm the backup/balance report.
Then test controlled chores/routines, purchases, retries, restart, midnight,
approval attribution and unchanged historical records in installed HA.
