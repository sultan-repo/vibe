# Vibe v4.11.0 release candidate

Scope: reuse-before-rebuilding guidance, one on-demand Build reference, static policy regressions and matching release metadata. No new package, runtime scanner, research agent, skill command or executable verification behavior is introduced. Existing automatic project adoption, internal workflows and board removal remain intact.

Merging to `main` is a production delivery to plugin users. The owner explicitly requested this PR, merge and publication. Complete the applicable checks before merge; authorization is not a test result.

## Verification and publication

- Identify the exact final PR head, current base and integrated candidate. Run both existing CI jobs, including the full repository tests and strict plugin validation with the existing pinned Claude Code version. A failed, cancelled, unavailable or skipped required check is not a pass.
- Check that the reference is reachable from core and Build, that trivial work needs no mandatory browsing, and that current-source verification, project-specific requirements, integration acceptance and permission boundaries remain explicit. The installer already copies Build references; no new installation path is required.
- Release workflow changes are version/notes/tag substitutions only. Preserve job IDs, permissions, trusted-main checks, tested-SHA matching and existing-tag protection. Publish only after checks pass for the merged commit; confirm the release and tag resolve to that commit.
- This scope does not change executable gates, permissions or product security behavior. Existing policy does not require an independent review merely for a low-risk instruction release. If consequential behavior is added or a required finding emerges, obtain the applicable independent review on the exact final head and a targeted recheck for fixes before delivery. No independent approval is claimed by static tests.

## Evidence limits

Static contracts and native package validation cannot certify live model decisions, dependency fitness in a user's application, reduced token use or faster delivery. Live representative-task comparisons are unverified, not a release result implied by passing static tests. Evaluate them once when useful rather than adding a benchmark to every feature. No measured speedup or unchanged defect-detection rate is claimed.

The evidence for this candidate belongs in the PR and CI run records, not pre-marked passes in this document. Existing project hooks/CI and all full-production verification requirements remain unchanged.
