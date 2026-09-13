# Development and validation

## Workflow

Verify checkout/root, `main`, intended remote, and both staged/unstaged diffs. Preserve unrelated changes. Review source contracts and current status before editing. Update affected documentation, stage explicit paths, inspect the staged diff, commit, and `git push origin main` after checks. Do not bump versions or create releases for ordinary documentation/code checkpoints.

For backend/card changes inspect `__init__.py`, `services.yaml`, `sensor.py`, `storage.py`, and the bundled card as relevant. Do not casually replace a bundled card with a potentially older root copy. Compare both copies and identify the intended edit source in the task report.

## Local checks

No dedicated repository test suite was found in the current file inventory. Do not claim full validation from syntax checks. For Python changes, parse changed source with Python's `ast.parse` (does not import HA or mutate storage); use a compatible HA test environment for behavioral tests. Validate changed JSON/YAML and inspect registered service/schema consistency. Card changes need a browser/Lovelace test for the actual interaction; passing JavaScript syntax alone is insufficient.

Existing `.github/workflows/hassfest.yml` and `hacs-validation.yml` provide repository validation on push. These do not exercise household workflows. Report CI separately from local checks and live acceptance.

Documentation-only changes need changed-file Markdown/link checks and a diff review, not a Home Assistant restart. Keep validation tools outside the product dependencies unless the task explicitly needs them.

## Live acceptance for an authorized deployment

Use test records approved for the task and preserve a current backup before migration/destructive tests. Record installed version, resource version, date, and environment without credentials.

- Create/update task times: defaults, overrides, unset values, start/end boundaries, and sensor output.
- Test assignment, start/complete, approval/rejection and point changes under the task's configured flags.
- Verify repeated assignment and rollover across an actual or controlled scheduled boundary, including relevant timezone/daylight-saving transitions.
- Verify reward listing, purchase/request behavior, insufficient points, repeated clicks/retries, status visibility, and accounting.
- Restart and confirm persistence; for an upgrade, verify both integration and bundled card changed together and records remained.
- For cross-repository changes, verify MagicMirror polling/actions against the installed backend, not just mocked payloads.

Record observed results and untested cases in progress/issues. A historical successful update does not prove all current time or reward edge cases.

For Markdown checks on this development machine, use MagicMirror's installed `markdownlint-cli2.cmd` with its `.markdownlint.json` via `--config` and explicit changed filenames; this applies the shared long-line policy without adding product dependencies. If that checkout/tool is absent, use an available Markdown checker with equivalent rules and report the difference.
