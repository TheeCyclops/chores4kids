# Task handoff template

Copy the relevant fields into a task prompt or an explicitly needed task note. Do not create a new permanent file for every small change.

- Outcome: what the user should be able to do when finished.
- Repository and branch: verify the actual root, not a mirrored copy.
- Read first: `AGENTS.md`, context index, and relevant issue/behavior records.
- Issue/backlog ID and scope: included changes and approved boundaries.
- Evidence: reproduction, expected/actual behavior, observed environment and date, code/deployed revisions if known.
- Decisions: approved behavior, constraints, and unresolved choices requiring an answer.
- Acceptance: concrete local checks and live steps; who can perform live validation.
- Delivery: commit and push; release/deployment only if explicitly part of this task.
- Completion: changed files, tests/results, commit IDs, pushed status, pending live checks, and updated documentation.

Example outcome: investigate timing gap C4K-V02, preserving existing tasks and configured approval behavior. Read architecture and validation first; identify the exact failing case before changing storage or services.

For agents that do not automatically load `AGENTS.md`, explicitly request that they read it. Shared files supply context across clients; they do not synchronize chat history.
