# Chores4Kids progress

Updated 2026-11-22. Published baseline is `cd9aa2d` (`v0.1.14`), including opt-in workflow-v2. HACS Validation, hassfest and release ZIP packaging pass. The last user-reported installed custom-fork version remains `0.1.13`; installation/activation of the new release is not claimed.

## Current state

- 2026-11-22 release published: [v0.1.14](https://github.com/TheeCyclops/chores4kids/releases/tag/v0.1.14) at `cd9aa2d`, with `chores4kids.zip` attached. Downloaded ZIP inspected in memory: manifest 0.1.14, workflow modules and bundled card match tested source after JSON-format/newline normalization. HACS Validation, hassfest, ZIP packaging and release automation all passed. See [release notes](releases/v0.1.14.md). No installation, live balance capture, activation or restart performed.

- 2026-11-22 implementation: opt-in chore library/occurrences, calendar and completion recurrence, overdue takeover with parent approval, ordered personal routines with immediate step points and parent-approved on-time bonus. Protected activation creates/read-verifies a private complete-store backup and balance snapshot; legacy chores become read-only without deleting records. Root/bundled card provide editors and retain rewards. See [workflow API and activation](WORKFLOW_V2.md). No live balance capture, activation, release, deployment or restart performed. Local tests and delivery results are recorded in the task completion; installed HA and MagicMirror-v2 acceptance remain pending.

- Standalone editable/release source and `/local/` bundled-card guidance are reconciled. The pre-existing staged README correction was retained in this documentation work.
- Backend implements native timing, repeat/rollover, statuses, points, shop/rewards and storage; inspect the [architecture](context/architecture.md) for source routing.
- Historical user reports confirm HACS fork updates, data survival, and time controls. The user confirms the household installation is custom-fork `v0.1.13` and that all chores returned after the update; the active runtime card resource was not independently inspected. Newer MagicMirror handoff reports working completion, approval/points, reward purchase and parent actions. Dates of those latter observations were not retained.
- Full regression coverage, repeat/rollover acceptance, card-resource inspection, and backup/restore readiness remain open [verification gaps](known-bugs.md).
- Shared reward points and longer parent unlock are planned for the next Chores page pass; no accounting or authorization changes made.

## Documentation checkpoint

Workflow-v2 local validation (2026-11-22): 46 in-memory backend tests pass,
including backup integrity, admin boundary, restart, failed-save rollback,
concurrent awards/purchases, overdue takeover and routine bonus accounting.
Actual bundled-card Chrome checks at 1080x1500 and 390x844 pass for quarterly
save/retry, routine ordering/save, step transport without fabricated balance
updates, rewards, archive and parent-only controls, with no page/console errors.
Browser plugin unavailable; existing Playwright/Chrome used. Python/JS syntax,
YAML, identical root/bundled card copies, changed Markdown and whitespace pass.
These are synthetic local checks; no installed HA/NUC acceptance is claimed.

Agent context, roadmap, issues, recovery, and release boundaries are documented. The 2026-10-30 rollover fix was released as `v0.1.13`, and the user reported that version installed with chores restored. Workflow-v2 source changes are recorded above; no newer HA installation or activation is claimed. Documentation commits are source checkpoints only; find them with `git log --oneline -- AGENTS.md notes README.md RELEASING.md`.

Next Chores page work should connect MagicMirror to the workflow-v2 sensor/services and parent authorization before any installed activation. Shared reward points remain a separate undecided feature. Update this file with checks, delivery and live acceptance; a complete off-host backup destination remains unresolved.

## 2026-10-30 rollover recovery

User reports missing assigned chores returned after an HA host reboot. Exact live cause remains unknown. Backend now retries missed/failed daily rollover every five minutes, serializes overlapping runs, marks a day complete only after saving, and logs start/failure/finish plus debug cleanup/skip reasons. Startup uses the same callback and refreshes sensors. Timers and startup work are cancelled on unload. Same-day template/child instances (including approved tasks) prevent retry duplicates; pending approvals, carry rules and points are preserved. No mirror layout or storage format changes.

Validation: five in-memory rollover regression tests and Python AST parsing; these isolate the HA storage/clock boundary and do not replace an installed HA integration test. Implementation committed as `c7e0539` on main and pushed to `TheeCyclops/chores4kids` after explicit user approval on 2026-10-30. No version bump, release, installation or restart. Live acceptance remains: deploy through a separately authorized release, observe midnight recovery and sensor refresh, verify no duplicate assignments or point changes, and inspect debug logs if recurrence continues.

## 2026-10-30 release v0.1.13

Prepared household release `v0.1.13` for rollover recovery. Manifest/tag sequence checked against actual fork releases; `v0.1.12` was latest. Root and bundled card hashes match and card code is unchanged. No storage schema migration. Five rollover regressions, Python syntax, and documentation checks passed; GitHub HACS Validation and hassfest passed for `ebf240b`. Published [v0.1.13](https://github.com/TheeCyclops/chores4kids/releases/tag/v0.1.13) at release commit `6f83f32`. HACS Validation, hassfest, ZIP packaging and release automation succeeded. Downloaded ZIP inspected in memory: manifest is 0.1.13, storage has the rollover guard, integration has the five-minute watchdog, and the bundled card is present. Home Assistant installation was later confirmed by the user; restart completion and midnight acceptance remain pending independent verification.

## 2026-10-30 user-reported installation acceptance

User confirms the installed version displays 0.1.13 and all chores are showing after the update. This is user-reported live recovery; points, restart completion, and an overnight rollover were not independently verified. User will observe the next rollover and return to this chat if changes are needed.
