# Session continuity at startup

The plugin's existing SessionStart hook adds the core and the project's `docs/STATUS.md` **Now** summary to one `additionalContext` JSON response. It reads at most ten summary lines, never history. If no status file exists, core injection is unchanged. The manual installer registers the same hook with `--status-only`, since its core is already imported. Its startup scripts live in Vibe's own `~/.claude/vibe-tools/` directory, preserving personal scripts and registrations in the shared hooks folder.

Use `## Now` followed by `Updated`, `Position`, `In progress`, `Next task` and `Waiting on owner` fields. `Updated` ends with `| <full default-branch baseline SHA>`. The baseline describes integrated work, not the commit containing the status update. Descendant commits changing only `docs/STATUS.md` do not make the record stale; changes to other documents do.

The project comes from hook input `cwd`, falling back to `CLAUDE_PROJECT_DIR` and the current directory. Local Git finds the checkout root, including linked worktrees. The known default is `origin/HEAD`, or the only other remote HEAD. A missing default or unavailable baseline produces an advisory instead of guessing `main`.

Warnings describe **locally known** refs. Unmerged branches absent from Now are listed as potentially relevant, not proven forgotten work. Merged branches and history-only mentions do not suppress that check. There is no fetch, remote query, lazy object fetch, file write, model call or per-turn hook. Git inspection has a two-second total budget. The hook can detect a stale record but cannot create a handoff or recover unsaved work.

For an existing authoritative issue tracker, declare that source in project instructions and have the coordinator read it on resume. This local hook does not query a tracker or create a competing status file. Installations without Python retain plain core injection; continuity inspection needs Python 3.
