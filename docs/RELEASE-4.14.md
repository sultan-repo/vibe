# Vibe v4.14.0 release candidate

Merging to `main` is a production delivery and formal Vibe plugin release. Complete required evidence before merge and treat skipped checks as pending, not a pass.

Routine feature deployment, including an auto-deploying merge, uses focused feature-specific unit/integration/component and UI/API acceptance checks covering delivered behavior and relevant local error/recovery handling. It does not automatically run full user-journey E2E. Run full journey E2E when the owner explicitly requests it or at formal production release/promotion. Critical security/data invariants and explicit project integration gates remain mandatory; unbounded impact expands scope.

Existing project hook/CI requirements remain active until an owner-authorized, validated replacement is implemented. Upgrading Vibe only updates policy, not a project's executable gates. The coordinator must confirm the actual deployment/promotion boundary, not guess from branch names.

## Before merge
Run full Vibe repository checks, strict Claude plugin validation, Codex first-prompt tests, installer smoke, policy regressions, and independent review of the exact final head because delivery controls changed. Preserve existing trusted-main SHA and tag guards. Report skipped/unavailable runtime E2E honestly, without claiming model adherence or speedups from static tests.

The independent review must cover the exact final HEAD and use at most one targeted recheck for fixes. Static regression tests cannot certify live model behavior or unobserved user journeys.
