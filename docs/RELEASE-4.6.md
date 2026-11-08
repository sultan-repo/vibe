# Vibe v4.6.0 verification

## Scope and authorization

This release includes [PR #11](https://github.com/sultan-repo/vibe/pull/11): automatic workflow selection, parallel implementation guidance and progress-board corrections. The owner authorized merge and publication on 2026-11-08 after disclosure that live Claude execution and the native UI remained unverified. Rejected PR #6 remains excluded.

## Automated evidence

The PR #11 source at `37f56c216f10e1f150393933f681c79e71748cd9` passed:

- `python3 -m unittest discover -s tests -v`: 11 tests.
- `node --test tests/mod-board.test.mjs tests/benchmark-runner.test.mjs`: 15 tests, including six new board regressions.
- `python3 hooks/test-force-push-hook.py`: all 28 cases.
- Shell/Node syntax, JSON/YAML metadata, exact startup-hook injection and isolated install/reinstall/uninstall checks preserving user settings.

For publication, the Vibe checks workflow also runs `claude plugin validate --strict .` and `claude plugin test .` with Claude Code 2.1.314 on the release branch and main. The publisher uses only a successful trusted main-push run and checks out its exact SHA. The GitHub release records the final tested commit and CI URL. A passing PR run alone does not trigger publication.

## Disclosed limits

Live natural-language routing, actual concurrent Claude workers and the interactive terminal/Desktop board have not been observed in an authenticated Claude session for this release. Automated packaging and Mod rendering are not substitutes for those observations.

The benchmark harness has passed its dry-run self-tests, but authenticated plain-Claude-versus-Vibe timing and usage comparisons have not been run. No speedup is claimed.

## Follow-up runtime checks

In a supported Claude Code session with v4.6.0 loaded, request a bounded fix and then a feature with independent parts using normal language. Observe routing, file ownership, any parallel assignments, final integration checks and automatic board behavior. Confirm dependent work stays sequential, dismissed panes stay closed, and task completion is not reported as acceptance evidence. Record the CLI version, observations and any measured timing before claiming these behaviors verified in practice.
