# Approved behavior

Current context reconciled 2026-09-13. These preservation requirements do not imply complete live regression coverage.

- Preserve existing chores, assignments, point balances, rewards, approval history, and settings during updates. Code rollback alone is not data rollback.
- Native default/override task times and the bundled admin card are part of the customized fork. Time controls appeared and data persisted after HACS updates according to historical user reports.
- Preserve repeat templates, generated assignments, child associations, and local-time scheduling. Do not rebuild retired fixed-slot/YAML helpers.
- Honor configured backend approval behavior, including explicit skip-approval options. Dashboard completion must not independently invent points or status transitions.
- Keep frontend and integration version-aligned. Preserve the `/local/` resource flow.
- MagicMirror's completion, approval/rejection, rewards purchase, and gated parent controls have user-reported working results; parent session behavior lives primarily in MagicMirror.
- Shared points for rewards is a new request, not an existing agreed accounting contract. Clarify pooled purchase versus transfer, consent, approvals, refunds, and transaction safety before coding.
- Never silently reset storage, balances, task history, or integration entries to solve a display issue.

Read [validation](development.md) before changes and [issues](../known-bugs.md) for evidence gaps.
