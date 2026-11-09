# Vibe v4.9.0

## Change-aware testing

Vibe separates feature acceptance from production readiness. Isolated changes use relevant unit/integration checks and targeted browser journeys, including failure/recovery paths. Finishing a feature alone no longer triggers the entire application E2E suite.

Shared changes expand verification to affected consumers. High-risk behavior keeps its critical checks and required independent review before merge. Unknown impact falls back to full relevant verification. Every production delivery, including small releases and auto-deploying merges, still requires full integrated evidence.

Selection considers cumulative changes, dependencies and acceptance criteria, not filenames alone. Empty selections cannot pass. Uncovered requirements need their own observed acceptance evidence; a broader green suite does not prove them.

## Quality and adoption

Existing project rules, hooks and required CI remain active. Before reducing a project's development gate, validate the replacement with a bounded targeted/full comparison and known-regression replay where available. This is an adoption check, not a requirement to run both suites for every feature.

Valid results can be reused only for matching inputs and sufficient coverage. Quick results cannot replace full evidence, failed/interrupted reruns invalidate earlier passes, and test reuse does not replace exact-commit review. Project adapters must enforce empty-selection rejection and scope-aware cache keys; Vibe does not install a universal test selector or migrate project hooks automatically.

## Release safeguards

This update has its own version rather than shipping under v4.8.0. Because marketplace installations follow this repository, merging to `main` is delivery. Native plugin validation now runs before merge on every PR, regardless of branch name, and again on main. Publishing remains restricted to successful trusted main-push checks and their tested source commit.

## Verification and limits

See [release verification](RELEASE-4.9.md) and [testing adoption](TESTING-VALIDATION.md) for the acceptance plan and evidence requirements. Actual outcomes belong in the final candidate's PR and CI records; these notes do not claim pending checks passed.

Policy/configuration tests and native plugin checks do not prove live agent behavior or application coverage. No measured speedup or unchanged defect-detection rate is claimed. Existing projects retain their current gates until their replacement is validated.
