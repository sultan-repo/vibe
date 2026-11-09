# Change-aware testing: validation and adoption

Status: v4.9.0 release candidate. This document defines acceptance scenarios, not recorded runtime passes. Check the associated PR/CI evidence for executed checks and the exact candidate. Merging to `main` is a production delivery because the marketplace installs from this repository; a draft PR or a missing tag is not a deployment hold. The version, release notes and publisher must agree before merge. See [release verification](RELEASE-4.9.md).

## Scope

Replace automatic full testing at feature milestones with affected/expanded/release coverage. Full production verification, critical invariants, project gates and bounded independent review remain mandatory where applicable. This change updates Vibe's instructions and project templates; it does not rewrite existing projects' scripts, install a selector, change the cache executable or bypass CI.

## Acceptance scenarios

| Scenario | Expected behavior |
| --- | --- |
| Documentation wording, no executable or operational effect | Document checks; no application E2E. Workflow policies and executable examples are not automatically exempt. |
| Isolated search behavior on a non-deploying branch | Affected unit/integration and targeted browser journeys, including empty/error states. No unrelated full suite solely because the feature is finished. |
| Shared UI, routing, API contract or global CSS | Expand to affected consumers and devices; do not classify by the edited filename alone. |
| Authentication, consent, privacy, payments or migration | Test critical invariants before merge and retain required independent review. Expand fully if impact cannot be bounded. |
| Unknown/stale base or dependency map | Expand; full relevant checks when bounded impact cannot be established. |
| Selected runner executes zero tests or misses new acceptance | No acceptance pass. Add coverage or broaden; a full green suite cannot establish an uncovered requirement. |
| Unexpected failure | Diagnose, retain the failure and add regression evidence. No blind full-suite retry loop or disabled assertion. |
| Integration brings in new target-branch changes | Re-evaluate cumulative impact and invalidate affected prior evidence. Worker-local passes are insufficient. |
| Small production release or auto-deploying merge | Full integrated delivery gate, just as for a major release. |
| Non-deploying feature PR or status question | Use applicable focused evidence; report full release E2E pending without automatically running it. |
| Existing project mandates full pre-push checks | Preserve it until an authorized replacement is validated; do not silently bypass it. |
| Same tree, different selection base/filter/device | Do not reuse narrower evidence for a broader or different claim. |
| Full pass followed by successful quick run | Retain full evidence separately; quick must not overwrite it. |
| Failed/interrupted rerun after an earlier pass | Invalidate prior evidence for those inputs; do not fall back to stale green. |
| Same candidate and sufficient unchanged full evidence at release | Reuse it instead of repeating the same gate; required CI and exact-HEAD review still apply. |

## Repository checks

Run the existing policy, YAML, installation, session-start, force-push and verification-cache tests through the Vibe checks workflow. Both `validate` and `native-mod-render` must pass on the final integrated candidate before merge. Native checks now run on every PR, regardless of branch name, and on main with pinned Claude Code 2.1.314. A skipped, unavailable, cancelled or failed required check is not a pass; post-merge validation alone is too late for marketplace delivery. The new `tests/test_testing_policy.py` guards instruction consistency, escalation rules and evidence contracts. These are static policy regression tests, not proof of an agent's runtime decisions or a project's test coverage. Existing executable cache tests remain responsible for the helper's behavior. `tests/test_release_candidate.py` guards version/release consistency, pre-merge native validation and the trusted-main publication boundary. These configuration checks do not themselves execute a release or prove native runtime behavior.

## Before reducing a project's existing gate

During authorized adoption, identify its true deployment boundary and map existing commands to coverage scopes. Keep old gates active while performing a bounded shadow comparison: targeted and full checks on the same representative candidate/environment, plus known-regression replay where available. Include isolated, shared and high-risk changes, and intentionally incomplete selections. Investigate any relevant failure missed by selection before enabling the narrower development gate. Do not repeat this dual-run adoption exercise for every feature.

Record the candidate, integration base, selected journeys, omitted checks with reasons, outcomes, elapsed time and duplicate-run count in existing CI/PR evidence. Verify cache invalidation for changed inputs, failed reruns and selection-scope changes. Keep release coverage unchanged and make fallback to expanded/full explicit.

## Limits and release prerequisites

Live Claude instruction adherence, real-project targeted/full comparisons and comparative timing require a suitable runtime and representative project. Do not infer them from static tests or report them passed without evidence. A bounded sample cannot prove zero quality impact. Because this changes delivery-control policy, retain the required independent review of the final candidate before merge/release. No automatic project migration or measured speedup is claimed.
