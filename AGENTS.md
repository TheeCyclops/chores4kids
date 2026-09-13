# Chores4Kids household agent instructions

## Start here

Authoritative editable and publishing checkout: `C:\Users\alxwh\Documents\chores4kids`.
Remote: `TheeCyclops/chores4kids`; delivery branch: `main`.
Read [context index](notes/context/README.md), [progress](notes/progress.md), and the task-specific documents before editing.

This custom fork supplies the Home Assistant backend and bundled Lovelace card. Home Assistant runs in the Lenovo server VM; MagicMirror runs on a separate NUC. MagicMirror source is `C:\Users\alxwh\Documents\Projects\MagicMirror`; read its `AGENTS.md` for dashboard changes.

This repository is not an export destination for a MagicMirror vendor copy. Do not synchronize retired copies or merge these repositories' histories. Preserve stored chores, balances, rewards, settings, and history across code updates.

## Working rules

- Read the context index and current progress before editing; follow the task-specific links. The user's current task defines scope. If a requested behavior is undecided, ask about that decision before implementing it.
- Verify the repository root, branch, remote destination, and staged/unstaged changes. Do not create a mirrored working copy or silently switch repositories.
- Preserve unrelated changes. Stage explicit task paths, never `git add .`. Review the staged diff before committing; do not sweep another task's staged changes into your commit.
- Complete appropriately scoped checks, update affected context/status/bugs, then commit and push normally to the repository's household branch. Report commits, checks, and remaining live verification. If pushing fails, retain the commit and report the actual failure; never force-push.
- Releases, version bumps, deployment tags, NUC updates, HACS installation, and restarts require a release/deployment task. A routine code or documentation task does not include them.
- Never rewrite history, force-push, reset away changes, or automatically restore deleted files. Use reviewed revert commits for ordinary code rollback.
- Keep credentials, passcodes/hashes, private URLs, generated configuration, and mutable family data out of Git and tool output. Inspect safe source and sanitized diagnostics instead of printing private configuration.
- Separate code implementation, local checks, user-reported live results, and unverified runtime state. A passing test, HTTP 200, or successful push does not prove the deployed display or Home Assistant behavior works.
- Keep documentation concise and linked. Update the authoritative record instead of adding a conflicting summary elsewhere. Record observation dates separately from dates of imported handoffs.
