# Automatic project adoption

Use once on first authorized project editing, including a Fast task, or when the managed policy is outdated. Vibe applies its core principles in the active session even when persistent adoption must be deferred. Do not ask the user to run Discover, Build, Reassess or an initialization command.

1. Read applicable project rules, existing status and Git state. Resolve the active project root, not an unrelated parent or another worktree. Respect plan mode and permissions.
2. Before introducing `AGENTS.md` or repairing the v4.12 fallback reminder, establish the effective Codex `project_doc_fallback_filenames` order from the active host configuration, including applicable overrides. The coordinator supplies that order as a JSON array with `--codex-fallbacks-json`; use `[]` only when verified empty. Do not infer it merely from files present or assume an unavailable host has default settings. Existing native `AGENTS.md` or `AGENTS.override.md` ordinarily needs no fallback discovery.
3. The coordinator runs `python3 <Vibe root>/hooks/project_setup.py adopt --project-dir <project root> [--codex-fallbacks-json <JSON array>]`. The manual installer provides `~/.claude/vibe-tools/project_setup.py`. Quote actual paths and JSON. This is an internal operation, not a user command or another approval checkpoint.
4. Inspect the small diff and continue authorized work. Reuse a current block. Do not copy all Vibe skills/references into each project or add a mandatory registry. If effective routing is unknown or reconciliation is unsafe, leave files unchanged, apply the principles in-session, disclose the limitation once and continue independent work. Do not guess to make adoption succeed.

## Preserve native instruction selection

Where a configured fallback is currently selected, keep that file selected and update the small managed policy there. Do not introduce a higher-priority `AGENTS.md`, copy owner instructions into a stale snapshot, or rely on the model to rediscover instructions that were previously loaded automatically. The first existing configured fallback retains precedence, including an empty file. Later owner edits remain in the native source.

For a fallback-based project, existing Claude instructions receive the same small Vibe policy without copying Codex-only owner rules. If Claude has no file, use `.claude/CLAUDE.md` rather than creating a root `CLAUDE.md` that could shadow another configured fallback. For existing native shared/override instructions, or when no fallback is selected under verified settings, use root `AGENTS.md` and an import from the existing root or nested Claude instructions. An existing `AGENTS.override.md`, even empty, receives its managed block without exposing its owner rules to the other host. Preserve existing prose imports and symlinks to the shared file; fenced/indented examples are not imports. New bridges go before an unclosed example, not inside it.

During repair of v4.12, remove only an owner-free shared file carrying Vibe's old fallback reminder and, when applicable, its still owner-free generated root bridge. A bridge that gained owner instructions is a real instruction source, never a file to ignore. Refuse ambiguous shared owner content or an owner-written import that would become dangling; reconcile explicitly instead of discarding it. Ambiguous markers, unrelated symlinks, non-UTF-8 and oversized rules remain protected. Repeated adoption is a no-op.

## Failed writes and recovery

Validate all planned edits before writing. Caught write failures roll back completed edits, preserving original contents, permissions and empty-file existence. Never overwrite concurrent owner edits during rollback. If rollback cannot safely complete, report the affected paths and retain owner-only recovery copies in the reported `vibe-adoption-*` temporary directory. Reconcile those copies manually within existing authority; do not replay them automatically over current files.

This is not a filesystem-wide atomic transaction. An abrupt process or machine termination can leave partial edits and a private recovery directory. Inspect the current files and recovery manifest before retrying, and keep the original owner's rules authoritative. No recovery process runs at startup or on every turn.

Read-only discovery, assessment, explanation, status questions and plan mode apply principles without writing policy files. Adoption never grants permission to commit, push, merge, release, deploy, change review requirements or replace existing hooks/CI.

## Owner-controlled governance
During the first authorized edit or when relevant project instruction/gate configuration changes, the coordinator loads `governance.md` and performs a bounded, read-only conflict assessment. This check is separate from project policy adoption and does not run at every session start. The same policy applies to Claude Code and Codex. Report only confirmed consequential contradictions and use existing decisions to suppress repeat questions for unchanged evidence. Project-specific product, security and delivery requirements are not automatically conflicts.

## Policy adoption is not gate migration

Inspect relevant gate instructions and actual `core.hooksPath` when first adopting or when a startup advisory reports changed configuration. Follow Build's testing-policy reference. The local startup inspector reads a bounded set of rules, active executable commit/push hooks, root package scripts, literal script references and workflow files. It never executes project commands. Its fingerprint cache is Git-private and suppresses unchanged notices; it does not certify coverage or runtime branch conditions.

The inspector reads at most 24 paths, 64 KiB per file, 256 KiB in total, eight workflow-directory entries and three script-reference levels, with a 0.5-second best-effort filesystem budget inside the startup Git time budget. Special files and symlinks are not followed for file contents. Dynamic shell behavior, custom runners and unavailable or bounded inputs require coordinator inspection. Filesystem calls on stalled storage cannot be given a hard wall-clock guarantee. A targeted browser smoke check or an intentional delivery gate is not automatically a conflict.

Never disable a gate from an advisory. Ordinary development should avoid expensive blocking full gates by default, while cheap checks, targeted browser acceptance, critical invariants, explicit integration requirements and full production verification remain. Validate an authorized replacement with a bounded targeted/full comparison before relaxing coverage.
