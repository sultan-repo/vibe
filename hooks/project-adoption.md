# Automatic project adoption

Use once on first authorized project editing, including a Fast task, or when the managed policy is outdated. Vibe already applies its core principles in the active session. Do not ask the user to run Discover, Build, Reassess or an initialization command.

1. Read applicable project rules, existing status and Git state. Resolve the active project root, not an unrelated parent or another worktree. Respect plan mode and permissions.
2. If the managed `vibe:project` block is absent or outdated, the coordinator runs `python3 <Vibe root>/hooks/project_setup.py adopt --project-dir <project root>`. The manual installer provides `~/.claude/vibe-tools/project_setup.py`. Quote actual paths. This is an internal operation, not user setup.
3. Inspect the small diff and continue the requested work. Reuse the block when current. Do not copy all Vibe skills/references into each project or add a mandatory registry. Native installed skills remain the workflow implementation; load their detailed content only when needed.

The helper keeps the shared policy in root `AGENTS.md`. It imports that file from the existing root or nested Claude instructions, creating a root `CLAUDE.md` bridge when needed. An old Claude policy block becomes an import. Existing owner rules, permissions, line endings and a Claude symlink to the shared file are preserved. Ambiguous markers, unrelated symlinks, non-UTF-8 and oversized rules require reconciliation. Repeated adoption is a no-op.

Read-only discovery, assessment, explanation, status questions and plan mode apply the principles without writing a policy file. Adoption never grants permission to commit, push, merge, release, deploy, change review requirements or replace existing hooks/CI.

## Policy adoption is not gate migration

Inspect relevant gate instructions and actual `core.hooksPath` when first adopting or when a startup advisory reports changed configuration. Follow Build's testing-policy reference. The local startup inspector reads a bounded set of rules, active executable commit/push hooks, root package scripts, literal script references and workflow files. It never executes project commands. Its fingerprint cache is Git-private and suppresses unchanged notices; it does not certify coverage or runtime branch conditions.

The inspector reads at most 24 paths, 64 KiB per file, 256 KiB in total, eight workflow-directory entries and three script-reference levels, with a 0.5-second best-effort filesystem budget inside the startup Git time budget. Special files and symlinks are not followed for file contents. Dynamic shell behavior, custom runners and unavailable or bounded inputs require coordinator inspection. Filesystem calls on stalled storage cannot be given a hard wall-clock guarantee. A targeted browser smoke check or an intentional delivery gate is not automatically a conflict.

Never disable a gate from an advisory. Ordinary development should avoid expensive blocking full gates by default, while cheap checks, targeted browser acceptance, critical invariants, explicit integration requirements and full production verification remain. Validate an authorized replacement with a bounded targeted/full comparison before relaxing coverage.
