# Releasing the household fork

Authoritative source: `C:\Users\alxwh\Documents\chores4kids`, `TheeCyclops/chores4kids`, branch `main`. Do not publish from the retired MagicMirror vendor tree.

## Ordinary task checkpoint

Complete relevant checks, update context, stage explicit task files, review `git diff --cached`, commit, and `git push origin main`. A routine checkpoint does not bump the manifest, tag, publish a release, install via HACS, or restart Home Assistant.

## Explicit release task

1. Read [progress](notes/progress.md), [validation](notes/context/development.md), and [recovery](notes/context/recovery.md). Inspect clean/task-specific status and actual remote release inventory. Source manifest was `0.1.12` at context creation; do not treat that as a perpetual latest version.
2. Choose the next unused household version from the current manifest and actual fork releases. Ignore unrelated inherited higher upstream tags when choosing the household sequence; never reuse or move a tag.
3. Verify backend and deployed bundled card are aligned. Review any storage changes and compatibility. Run relevant checks and record remaining live acceptance.
4. Update `custom_components/chores4kids/manifest.json` for the release. Manifest `X.Y.Z` must match tag `vX.Y.Z`. Stage explicit release files, review, commit and push `main`.
5. Create an annotated `vX.Y.Z` tag on the reviewed commit and push that exact tag. Publish a GitHub release with changes, validation and compatibility notes. Do not use `git push --tags` to publish inherited tags accidentally.
6. Check applicable release automation/results. A published release is still not proof Home Assistant has installed it.

## Explicit Home Assistant deployment task

1. Establish a suitable current backup before risky/storage changes; record existing installed version and compatibility requirements.
2. In HACS select the household fork release and install/update it. Confirm the repository is `TheeCyclops/chores4kids`.
3. Restart Home Assistant as authorized and reload the dashboard. `frontend.py` installs the bundled card at `/local/chores4kids-card.js?v=<cache-token>`; verify one intended resource rather than adding `/hacsfiles/` duplicates.
4. Confirm integration availability, existing data, task timing, approval/points, rewards and card behavior using [acceptance scenarios](notes/context/development.md). Record installed version and results.

If HACS does not show a release, verify the actual published fork release, tag and manifest alignment before troubleshooting runtime or copying files manually. Routine manual file copying is retired. Document failed checks; do not declare release acceptance from successful download alone.
