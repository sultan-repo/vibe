# Automatic parallel work

Use native Claude subagents for substantial independent tasks. Keep one coordinator responsible for the outcome. Do not add a scheduler, mandatory agent team, approval step or separate task register.

## Dispatch ready work

- Start with at most three concurrent workers, or fewer if the runtime permits fewer. The coordinator controls the total; workers do not recursively delegate without an allocated slot and an explicit assignment from the coordinator.
- Dispatch tasks whose inputs are ready and whose outputs can be combined without conflicting ownership. Research, separate modules and independent test commands can overlap. Establish shared API/schema decisions before dependent implementation. Different filenames alone do not prove independence.
- Give each worker the objective, relevant user/project constraints, agreed interfaces, owned files, starting commit and acceptance checks. Pass the same scope and permission boundaries as the coordinator. Workers do not expand scope, publish, merge or deploy on their own.
- Keep the coordinator working on an independent task while workers run. Release dependent work as its prerequisites become available; do not wait for unrelated workers or impose artificial rounds.
- If delegation is unsupported, the task is too small, or safe ownership cannot be established, work sequentially without asking the user to run commands or change settings.

## Isolate changes and shared resources

- Prefer separate Git worktrees for substantial parallel editing, each based on the same intended committed version. Verify each worker's starting SHA. Native worktrees can start from the default branch; use a supported current-HEAD base or create them explicitly from the chosen commit.
- A worktree does not include uncommitted parent changes. Preserve user edits. Finish and commit only authorized prerequisite changes, deliberately supply the required patch, or keep dependent work in the coordinator until its inputs can be shared safely.
- A shared workspace is acceptable for narrowly scoped, disjoint edits with explicit file ownership. Neither the coordinator nor another worker edits owned files until the assignment is returned or stopped. Serialize overlapping changes even across separate worktrees.
- Worktrees isolate files, not databases, ports or external services. Isolate test resources or serialize commands that mutate the same resource. The coordinator owns shared lockfile changes, shared branch operations and integration; workers may commit only their assigned work in their own worktree.
- Keep shared progress and continuity files under the coordinator's ownership. Workers report progress and blockers to it rather than replacing the board's full plan.

## Integrate and verify

Workers return the patch or branch/commit, changed files, exact checks and results, and unresolved dependencies or blockers. A completion notification is not acceptance evidence.

The coordinator inspects and integrates the results, resolves conflicts, and runs the affected checks on the combined code. Reassign or finish failed work within the approved scope; stop the previous worker before transferring file ownership. Preserve useful partial work and report genuine blockers instead of repeatedly respawning workers.

Before a required final review, finish integration and tests, stop outstanding writes to the reviewed code, and commit the final state. Use the existing single consolidated Claude review and bounded targeted recheck on that exact HEAD. Do not review every worker separately or reuse approval after a new code commit. External actions still require the existing authorization.
