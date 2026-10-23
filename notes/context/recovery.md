# Chores4Kids backup and recovery

Guidance only: no live backup or restore was performed or validated here.

## What source control preserves

Pushed commits preserve integration/card source. Tags/releases name published code. They do not preserve Home Assistant state, family balances, tasks, uploaded media, or VM configuration. Local inherited upstream tags are not household known-good checkpoints.

For an identified bad source commit, inspect dependencies and compatibility, use `git revert <full-bad-commit>`, run relevant checks, and push normally to `main`. Release a new compatible version only in an explicitly requested release task. Never retag a published version or force-push.

## Backup inventory and readiness

Home Assistant's storage key is `chores4kids` in the source's `Store` usage. Verify actual HA storage layout during an authorized inventory; do not edit `.storage` live or export raw family state to Git.

Secure backup coverage must include Home Assistant configuration/storage, integration entries, registries, chores/points/rewards/history/settings, HACS metadata, bundled-card registration, uploaded images/sounds under `www`, and secrets. Also account for the Lenovo VM/host configuration needed to restore the service. A source checkout or a copy of `custom_components` is insufficient.

Current backup freshness, destination, encryption/recovery keys, retention/off-host copy, and restore test are unknown. As of 2026-10-22, no backup destination is available; the user is searching for a server/RAID array that can host backups and other services. Use a separately authorized task to inventory and create a complete backup, secure recovery material, and test restoration in an isolated compatible environment before Lenovo upgrade or destructive migration. Do not post backups or keys in chat/Git.

## Rollback compatibility

Preferred source recovery is a new revert-based release. Downgrading to a previous HACS release is an alternative only after checking its compatibility with current stored data and HA version; exact downgrade/restore flow has not been tested here. Do not assume old code can read a migrated store.

Before any authorized install/rollback: record current installed version/resource and backup reference, review storage changes, and establish a compatible restore point. Follow [release/deployment guidance](../../RELEASING.md), restart only as authorized, then verify tasks, balances, rewards/history, timing, card resource, and MagicMirror interactions.

If data restoration is necessary, restore the matching complete backup through the chosen HA/VM procedure, not selective guessed JSON edits. Record actual version and acceptance. Keep backup and source histories intact.
