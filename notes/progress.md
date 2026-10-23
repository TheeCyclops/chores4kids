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
