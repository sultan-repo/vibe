# Vibe v4.9.0 verification

## Delivery boundary

Merging to `main` is a production delivery: the marketplace source is `./`, so new installations receive the default branch without waiting for a tag or GitHub release. Treat PR #15 as a release candidate, not as an inert documentation merge. Keep it unmerged until the checks and independent recheck below are complete and the owner authorizes delivery.

The plugin version, marketplace description, core heading, validation workflow and publisher identify v4.9.0. Historical v4.8 files and tags are unchanged. The publisher retains its existing filename, `publish-v4.5.yml`, but targets v4.9.0 and its matching notes.

## Required before merge

1. Complete all tracked changes and identify the exact final PR head, current integration base and integrated test candidate. If the base or candidate changes, reconcile the impact and obtain applicable current evidence; an older approval does not approve a new commit.
2. Require successful `validate` and `native-mod-render` jobs on that final integrated candidate. The existing full repository checks remain: shell/JSON syntax, board and benchmark tests, force-push safeguards, all Python policy/cache/continuity/installation tests, and install/uninstall smoke checks. Native validation uses pinned Claude Code 2.1.314 for `claude plugin validate --strict .` and `claude plugin test .`.
3. Native checks run for every PR, including draft and non-`release/` branches, as well as main. A skipped, unavailable, cancelled or failed required job is not a pass. Do not rely on a post-merge run to validate code already available through the marketplace.
4. Obtain a focused independent targeted recheck of the exact final candidate against the review findings: release/version consistency, native validation before delivery, uncovered-requirement acceptance evidence and unchanged quality protections. Preserve required high-risk review; this is not another open-ended review cycle. Remaining required findings block delivery.
5. Record the candidate, CI run/job links, actual outcomes and recheck verdict in the PR. Evidence from the earlier reviewed commit `7032f4fe6636094a31d8f2821617b8b89df53e58` cannot certify this revised candidate. This file is a verification plan, not a claim that these checks have passed.

## Publication after authorized merge

The PR workflow keeps read-only repository permissions and no publish credential. Native validation does not require running an agent or an application E2E suite. The publisher still accepts only successful trusted main-push Vibe checks, checks out their exact tested SHA, verifies the expected version and release files, rejects conflicting tags, and skips a stale main candidate. A PR check run cannot publish. The resulting GitHub release records the tested commit and CI URL.

No tag, release, main-branch update or other project's gate is authorized merely by preparing this candidate. Branch protection is not reconfigured by these changes; maintainers must confirm the required successful jobs and recheck before authorizing merge.

## Adoption and limits

Existing project gates stay active until an authorized replacement has passed the bounded targeted/full comparison in [TESTING-VALIDATION.md](TESTING-VALIDATION.md). Empty test selections and selection-scoped cache keys still require correct project adapters. Broad passing checks cannot prove an uncovered requirement: add and observe its acceptance evidence.

Static policy/configuration tests and native package/Mod validation do not prove live Claude instruction adherence, representative project defect detection or timing improvements. Those need observed runtime evidence. No automatic project migration, measured speedup or zero-quality-impact guarantee is claimed.
