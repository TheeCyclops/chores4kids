# Chores4Kids issues and verification gaps

Updated 2026-09-13. No new backend-specific reproduced defect was established by these handoffs. Missing validation is not proof of failure.

| ID | Status / evidence | Verification and acceptance |
| --- | --- | --- |
| C4K-V01 | Current installed version/resource provenance unverified; older tracker reported `0.1.12` | Record actual HACS fork/version and one active `/local/` card resource without exposing credentials |
| C4K-V02 | Timing/repeat/rollover coverage incomplete despite historical working controls | Create/update defaults and overrides, generated assignments, scheduled-day rollover, timezone boundaries and restart persistence match source contract |
| C4K-V03 | Completion/points/rewards working per user handoff; complete regression coverage absent | Exercise configured approval/skip-approval, rejection, purchase, insufficient balance, duplicate requests and persisted accounting with authorized test records |
| C4K-V04 | Current Home Assistant backup and tested recovery unknown | Establish secure complete backup and restoration test before server upgrade or storage migration |

Historical duplicate/manual-copy and uncertain card-source problems were reportedly resolved through HACS adoption. Do not remove active components to replay the old cleanup. Reproduce any new instance first.

Hub flashing/date drift are MagicMirror issues, not established backend faults. Longer parent sessions and shared reward points are enhancements, recorded in [backlog](backlog.md).

For a new bug add expected/actual behavior, reproduction, environment/date, references, safe workaround, and acceptance. Label open, pending live confirmation, mitigated, or resolved based on evidence.
