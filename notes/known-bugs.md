# Chores4Kids issues and verification gaps

Updated 2026-10-22. No new backend-specific reproduced defect was established by these handoffs. Missing validation is not proof of failure.

| ID | Status / evidence | Verification and acceptance |
| --- | --- | --- |
| C4K-V01 | User confirms the household installation is custom-fork `v0.1.12`; active resource provenance is not independently inspected | Verify one active `/local/` card resource without exposing credentials if a live acceptance pass is needed |
| C4K-V02 | Timing/repeat/rollover coverage incomplete despite historical working controls; no current failure reported | Optional confidence pass: create/update defaults and overrides, generated assignments, scheduled-day rollover, timezone boundaries and restart persistence against the source contract |
| C4K-V03 | Completion/points/rewards working per user handoff; complete regression coverage absent; no current failure reported | Optional confidence pass: exercise configured approval/skip-approval, rejection, purchase, insufficient balance, duplicate requests and persisted accounting with authorized test records |
| C4K-V04 | Current Home Assistant backup and tested recovery unknown; no destination is available yet | Establish a destination first, then create a secure complete backup and restoration test before server upgrade or storage migration |

Historical duplicate/manual-copy and uncertain card-source problems were reportedly resolved through HACS adoption. Do not remove active components to replay the old cleanup. Reproduce any new instance first.

Hub flashing/date drift are MagicMirror issues, not established backend faults. Longer parent sessions and shared reward points are enhancements, recorded in [backlog](backlog.md).

For a new bug add expected/actual behavior, reproduction, environment/date, references, safe workaround, and acceptance. Label open, pending live confirmation, mitigated, or resolved based on evidence.
