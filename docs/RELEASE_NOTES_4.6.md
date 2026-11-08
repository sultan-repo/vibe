# Vibe v4.6.0

Describe what you want in normal conversation. Vibe selects the appropriate workflow and delegates independent work automatically.

## What changed

- **Automatic workflows:** ordinary requests select Discover, Build or Reassess internally. Approval of a pending decision continues already-requested implementation without another command. Slash commands remain optional shortcuts.
- **Parallel subagents:** substantial independent work can use up to three native Claude workers initially. Each assignment has defined inputs, file ownership and acceptance checks. Dependent work, conflicting edits and shared-resource mutations stay sequential.
- **Combined verification:** the coordinator owns shared progress, integration and final checks. Existing permission boundaries and the single consolidated final review remain in place; there is no extra review cycle per worker.
- **Respect for request scope:** discovery-only and review-only requests do not make unrequested project edits.
- **Progress fixes:** native TaskList updates no longer reference an undefined variable. Empty native task lists clear stale progress, failed updates preserve valid state, and the board shows reported tasks still in progress after the coordinator's turn ends. The board opens automatically from tracked work on supported surfaces.

## Verification and limits

- The implementation passed 11 Python policy/metadata tests, 15 Node tests and all 28 force-push safety cases, plus startup-hook and installation checks.
- Publication is gated by GitHub Actions checks on the exact main commit, including native plugin validation and Mod render tests with pinned Claude Code 2.1.314. The publishing workflow adds the tested commit and CI link below.
- **Live Claude execution is unverified:** natural-language routing and actual parallel delegation have not been observed in an authenticated Claude session for this release.
- **Interactive UI is unverified:** automated Mod rendering does not establish that the pane works in a real terminal or Desktop session.
- **Performance is unmeasured:** no numeric speed improvement is claimed. Parallel workers may consume more Claude usage.

## Using this version

Existing installations need to load the updated plugin once. After that, ask for a feature, fix, continuation or review normally. The progress pane requires the plugin installation method; the standalone installer still loads the automatic workflow rules without the pane.

The owner authorized merge and publication after the live-runtime and UI limitations were disclosed. See [verification details](https://github.com/sultan-repo/vibe/blob/v4.6.0/docs/RELEASE-4.6.md).
