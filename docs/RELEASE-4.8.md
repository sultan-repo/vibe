# Vibe v4.8.0 verification

## Scope

This release adds explicit continuity checkpoints, a compact status template, startup context and local Git diagnostics, with the same behavior available through the plugin and manual installer. It changes Vibe only, not Family Network or its project-specific delivery rules.

## Evidence

Local checks passed:

- `python3 -m unittest discover -s tests -v`: 52 tests, including 16 startup-hook regressions and four isolated installer tests.
- `node --test tests/*.mjs`: 17 board and benchmark-harness tests, without model calls.
- `python3 hooks/test-force-push-hook.py`: all 28 safeguards.
- Shell syntax for every script, JSON/YAML parsing, matching project templates and `git diff --check`.

Hook tests use real local Git repositories for current, stale, missing and malformed status; status-only descendants; other-document changes; mentioned/unmentioned and merged branches; missing default references; nested paths and worktrees. A fresh clone finds the active branch, next task and remotely preserved partial work without earlier conversation or scratch files. A Git shim restricts the executed commands to local reads and verifies that transport protocols and lazy fetching are disabled.

Installer tests exercise install, reinstall and repeated uninstall, preserving personal instructions/settings and unrelated hooks, including pre-existing generic `session-start.sh` and `session-start.py` scripts. Vibe's startup scripts are isolated in its own tools directory. Tests execute the installed startup command from a path containing spaces, an apostrophe and `$`, confirming that status is added once and the already imported core is not duplicated.

A fresh-context worker also continued a small synthetic Python task from a fresh clone and its committed status alone. It found the saved feature branch, completed the pending duplicate-removal behavior, passed three focused tests and pushed both the feature and canonical handoff to a local bare origin without merging. The exercise exposed an ambiguity about Updated's baseline; the core and Build guidance now explicitly preserve the default-branch baseline. One bounded follow-up corrected that field and confirmed warning-free startup without rerunning product tests. This is a controlled continuation exercise, not an observation of the owner's live Claude session.

Native `claude plugin validate --strict .` and Mod render tests run on the release PR and trusted main commit with pinned Claude Code 2.1.314. The local executor has no Claude CLI; CI records those outcomes instead of claiming a local native run.

The new core checkpoint paragraph is 109 whitespace-delimited words; the net core addition is 97 words. Detailed persistence and startup semantics live in the template, Build guidance and hook documentation. These are source-size counts, not billing-token or runtime measurements.

## Limits and publication

The startup hook is read-only and has no network or model calls. Local remote references may be stale; missing Git information cannot prove freshness. The hook surfaces saved state but does not force a model to save it, and abrupt termination before a checkpoint can still lose unsaved work.

Automated hook/install checks and a fresh-checkout exercise do not establish that the owner's live Claude session loaded the new version or always follows its policy. No comparative runtime or token saving is claimed. Existing project CI may still run on status pushes and is not bypassed.

The publisher accepts only a successful trusted main-push check run, verifies the exact source SHA and creates or verifies its matching release tag. The GitHub release records that tested commit and CI URL. A passing release PR alone does not publish.
