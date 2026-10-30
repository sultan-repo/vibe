# Vibe v4.5.0 release readiness

**Status: release candidate, not published.**

## Included
- PR #7: Fast/Standard/Critical routing, continuous implementation, concise user updates.
- PR #8: optional native graphical progress board.
- PR #9: readable GitHub commit titles and PR titles.
- Rejected PR #6: **excluded**, must not be merged as part of this release.

## Automated evidence
- CI checks Python skills and policy tests, Node mod tests, hook safety, installer/uninstaller, JSON/skill metadata and release version.
- `claude plugin validate --strict .` and `claude plugin test .` should also run with the intended Claude Code version. Mod tests in Node are not proof a native pane is usable.
- Copy the successful GitHub Actions URL, checked SHA and Claude Code version into the eventual release description.

## Real graphical UI smoke test (required, still awaiting a live Claude Code session)
Requires authenticated Claude Code CLI 2.1.287+ in an **interactive terminal** at least 144 columns wide (or supported Desktop Code tab). Headless `claude -p` does not display Mods.

1. Check out this release candidate, run `claude plugin validate --strict .`, then launch `claude --plugin-dir .`. This uses the local checkout rather than a previously installed marketplace copy.
2. Run `/vibe-board`. **Pass:** the "Vibe · Progress" pane is visible; the empty-state message is legible and closing it does not interrupt Claude.
3. Ask Claude to implement a multi-step feature using its native task tracking. **Pass:** step labels and progress numbers appear and update after tool results. If it does not create a native plan, use the deferred Vibe progress tool explicitly to send a two-step plan and update one step.
4. While a command runs, inspect **Details**. **Pass:** activity indicates what Claude is doing and returns to idle at turn end. Toggle **Less**.
5. Close the pane and keep working. **Pass:** it stays dismissed until `/vibe-board` is invoked again.
6. Open a narrow terminal, repeat the command. **Pass:** graceful degradation, without blocking coding or altering permissions.
7. Verify an actual test failure is not presented as accepted/verified work; the percentage means task-status progress only.
8. Repeat in Claude Desktop Code tab if supported by your installation. Capture screenshot, terminal width, CLI version and observed steps as review evidence.

**Do not mark a live smoke test passed based on static rendering, Node mocks, CI, or a conceptual UI screenshot.** The release authoring environment does not have an authenticated Claude Code binary, so this remains unverified.

## Performance comparison
On the **same machine**, CLI version, model, and ideally a quiet network, run:
```bash
node scripts/compare-performance.mjs --dry-run
node scripts/compare-performance.mjs --model sonnet --rounds 3
```
The runner creates independent disposable projects, alternates baseline (plain Claude Code with user settings suppressed) and Vibe (local candidate plugin), runs the same bug-fix prompts, then executes the same `node --test` acceptance checks. It records per-run wall time, Claude turns, token usage where returned, errors, and test success. This consumes Claude usage.

Compare **successful test rate first**, then median end-to-end wall-clock latency and tokens. A positive latency delta means Vibe was slower. Three paired runs per task are a minimum useful exploratory comparison, not a statistical proof. Validate that plain sessions did not inherit global Vibe instructions.

**Results as of candidate creation: NOT MEASURED.** The release-prep environment cannot authenticate and run Claude Code. Never replace this with an estimated speedup.

## Approval gates
1. Latest candidate commit passes CI.
2. Real native UI smoke evidence recorded or the release remains blocked.
3. Real performance comparison recorded, or the release owner explicitly accepts "performance unmeasured" in release notes.
4. Merge candidate only after approval; do not create a release tag, publish GitHub Release, or auto-deploy without explicit authorization.
