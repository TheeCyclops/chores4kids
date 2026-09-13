# Chores4Kids progress

Updated 2026-09-13. Source baseline: `12e1233` on `main`, matching remote at documentation-task start. Manifest: `0.1.12`. Local custom tags `v0.1.0` through `v0.1.12` exist alongside inherited upstream tags. Remote release inventory and current HACS installation were not audited.

## Current state

- Standalone editable/release source and `/local/` bundled-card guidance are reconciled. The pre-existing staged README correction was retained in this documentation work.
- Backend implements native timing, repeat/rollover, statuses, points, shop/rewards and storage; inspect the [architecture](context/architecture.md) for source routing.
- Historical user reports confirm HACS fork updates, data survival, and time controls. Newer MagicMirror handoff reports working completion, approval/points, reward purchase and parent actions. Dates of those latter observations were not retained.
- Full regression coverage, repeat/rollover acceptance, installed-version confirmation, and backup/restore readiness remain open [verification gaps](known-bugs.md).
- Shared reward points requires design; no accounting changes made. Longer parent unlock belongs primarily to the MagicMirror backlog.

## Documentation checkpoint

Agent context, roadmap, issues, recovery, and release boundaries are documented. No code, versions, HA state, releases, or installations changed. Documentation commits are source checkpoints only; find them with `git log --oneline -- AGENTS.md notes README.md RELEASING.md`.

Next backend work should start from a concrete issue/feature prompt and update this file with checks, commit references, pushed status, and remaining live acceptance.
