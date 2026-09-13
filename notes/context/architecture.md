# Chores4Kids architecture and contract

Source inspected 2026-09-12 at `12e1233`, manifest `0.1.12`; this is not a fresh live installed-version check.

## Source and delivery

This standalone checkout is both editable source and release source for `TheeCyclops/chores4kids`, branch `main`. The old MagicMirror vendor copy is retired. Backend and bundled card belong to the same release. HACS installation is a separate deployment action after an explicitly requested release.

`custom_components/chores4kids/__init__.py` registers services and initializes storage/sensors/frontend. `services.yaml` describes action inputs; handler code is the actual implementation. `sensor.py` exposes state. Inspect all three when changing a contract.

## State and services

`storage.py` owns `KidsChoresStore`, using Home Assistant `Store` with the key/version in `const.py` (currently `chores4kids`, storage version 1). Models include children/points, categories, task timing/status/repeat fields, shop items/history, and UI settings. This state lives in Home Assistant storage, not this Git repository. Never modify persistence shape without compatibility and recovery planning.

Task statuses in source include `assigned`, `in_progress`, `awaiting_approval`, `approved`, and `rejected`. Task fields include default/override start/end times, repeat-child associations, rollover, quick completion, and skip-approval flags. Preserve existing configured behavior rather than imposing a blanket approval policy.

Registered action families include `add_task`, `update_task`, `assign_task`, `set_task_status`, `approve_task`, `add_points`, and `buy_shop_item`. These names do not establish exact runtime entity IDs or complete payloads. Before new writes, compare handler schemas, `services.yaml`, sensor attributes, MagicMirror bridge mappings, and sanitized live samples. Never guess service payloads or hard-code IDs from old notes.

## Card and assets

`frontend.py` deploys `custom_components/chores4kids/www/chores4kids-card.js` into Home Assistant's `www` directory and registers `/local/chores4kids-card.js?v=<cache-token>` as a module resource. Do not add a duplicate `/hacsfiles/` resource. A root `chores4kids-card.js` also exists; identify whether a change needs both copies and explicitly compare them rather than assuming the root is deployed. The bundled copy is the runtime input.

Uploaded images/sounds and other assets under Home Assistant `www` require separate backup. Inspect path-building code before defining their exact inventory; don't treat a source release as backing up uploads.

## MagicMirror boundary

The separate MagicMirror bridge owns dashboard polling/action transport and local parent authentication. ChoreBoard renders chores/rewards; DailySchedule renders tasks in the Hub. Home Assistant remains authoritative for accounting and status. Cross-repository changes require compatible payloads and separate commits; do not merge histories or assume a dashboard push installs an HA release.
