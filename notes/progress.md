# Chores4Kids progress

Updated 2026-10-22. Source implementation baseline: `12e1233` on `main`; current documentation checkpoint: `57b7c678`. Manifest and user-reported installed custom-fork version: `0.1.12`. Local custom tags `v0.1.0` through `v0.1.12` exist alongside inherited upstream tags. The active card resource was not independently inspected.

## Current state

- Standalone editable/release source and `/local/` bundled-card guidance are reconciled. The pre-existing staged README correction was retained in this documentation work.
- Backend implements native timing, repeat/rollover, statuses, points, shop/rewards and storage; inspect the [architecture](context/architecture.md) for source routing.
- Historical user reports confirm HACS fork updates, data survival, and time controls. The user now confirms the household installation is custom-fork `v0.1.12`; the active card resource was not independently inspected. Newer MagicMirror handoff reports working completion, approval/points, reward purchase and parent actions. Dates of those latter observations were not retained.
- Full regression coverage, repeat/rollover acceptance, card-resource inspection, and backup/restore readiness remain open [verification gaps](known-bugs.md).
- Shared reward points and longer parent unlock are planned for the next Chores page pass; no accounting or authorization changes made.

## Documentation checkpoint

Agent context, roadmap, issues, recovery, and release boundaries are documented. No code, versions, HA state, releases, or installations changed. Documentation commits are source checkpoints only; find them with `git log --oneline -- AGENTS.md notes README.md RELEASING.md`.

Next Chores page work should start from a concrete feature prompt covering shared points and parent unlock. Update this file with checks, commit references, pushed status, and remaining live acceptance. Backup work remains blocked until a server/RAID destination is available.

## 2026-10-30 rollover recovery

User reports missing assigned chores returned after an HA host reboot. Exact live cause remains unknown. Backend now retries missed/failed daily rollover every five minutes, serializes overlapping runs, marks a day complete only after saving, and logs start/failure/finish plus debug cleanup/skip reasons. Startup uses the same callback and refreshes sensors. Timers and startup work are cancelled on unload. Same-day template/child instances (including approved tasks) prevent retry duplicates; pending approvals, carry rules and points are preserved. No mirror layout or storage format changes.

Validation: five in-memory rollover regression tests and Python AST parsing; these isolate the HA storage/clock boundary and do not replace an installed HA integration test. Implementation committed as `c7e0539` on main and pushed to `TheeCyclops/chores4kids` after explicit user approval on 2026-10-30. No version bump, release, installation or restart. Live acceptance remains: deploy through a separately authorized release, observe midnight recovery and sensor refresh, verify no duplicate assignments or point changes, and inspect debug logs if recurrence continues.

## 2026-10-30 release v0.1.13

Prepared household release `v0.1.13` for rollover recovery. Manifest/tag sequence checked against actual fork releases; `v0.1.12` was latest. Root and bundled card hashes match and card code is unchanged. No storage schema migration. Five rollover regressions, Python syntax, and documentation checks passed; GitHub HACS Validation and hassfest passed for `ebf240b`. Published [v0.1.13](https://github.com/TheeCyclops/chores4kids/releases/tag/v0.1.13) at release commit `6f83f32`. HACS Validation, hassfest, ZIP packaging and release automation succeeded. Downloaded ZIP inspected in memory: manifest is 0.1.13, storage has the rollover guard, integration has the five-minute watchdog, and the bundled card is present. Home Assistant installation, restart, and midnight acceptance remain pending user action.

## 2026-10-30 user-reported installation acceptance

User confirms the installed version displays 0.1.13 and all chores are showing after the update. This is user-reported live recovery; points, restart completion, and an overnight rollover were not independently verified. User will observe the next rollover and return to this chat if changes are needed.
