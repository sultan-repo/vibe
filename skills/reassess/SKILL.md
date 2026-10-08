---
name: reassess
description: Product alignment review and definition-of-done check. Use at a milestone, before a release, after a material requirements change, or when the user asks "are we done", "review the product", "what's missing", "does this still match the goal". Compares the objective, approved requirements, actual behavior, user journeys, and evidence; classifies gaps; updates docs/REQUIREMENTS.md and docs/STATUS.md; gives a done / not-done verdict with what remains.
---

# Reassess: does the software serve its purpose?

A finished task list, a green test suite, or a clean architecture does not prove the product is done. This skill checks alignment between the intended outcome, the approved requirements, the delivered behavior, and the evidence. It ends with a verdict and updated continuity files.

## 1. Gather inputs
- The objective and non-goals (project CLAUDE.md, STATUS.md).
- `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`.
- The code as it is now: `git log` and `git diff` since the last reassessment or milestone.
- Evidence: test runs, CI results, review findings, any user or operator feedback. Separate what was observed from what was claimed.

## 2. Coverage check (structural)
For the register, confirm:
- Every `approved` requirement has an implementation or an authorized disposition (deferred, superseded, blocked, with reason).
- Every `implemented` requirement has acceptance checks, and `verified` rows were actually observed to pass on the current code.
- No approved requirement disappeared. No unapproved feature was built.
- Non-functional and operational requirements are still accounted for.

Correct the register where it disagrees with reality. Downgrade any `verified` row whose evidence predates the code it covers.

## 3. Alignment check (behavioral)
Answer briefly, with evidence:
- Does the product solve the intended problem for the intended users?
- Which important workflows are incomplete, including failure and recovery paths?
- What meaningful requirements were overlooked?
- Has the implementation drifted from the objective, or has new evidence changed the best solution?
- Where will users hit friction?
- Are reliability and security proportionate to the risk?
- Is anything more complicated than the product needs?

## 4. Exercise the real software
Where the app can run here, walk the main user journeys and at least one failure path, and report what you saw. End-to-end tests count; unit tests alone do not for user-facing behavior. Never invent user feedback. If a real environment or real users are unavailable, use representative scenarios and say that this is the limitation.

## 5. Operational readiness (production-relevant systems only)
Check what applies: deployment and rollback, configuration and secrets handling, logging and monitoring, backup and recovery, data reconciliation, support and maintenance needs. Prefer existing infrastructure. Propose new operational tooling only against a concrete need.

## 6. Classify each finding
- Missing approved requirement.
- Required defect correction.
- Approved requirement change.
- Proposed product enhancement.
- Architectural or operational improvement.
- Deferred capability.
- Accepted limitation.

Prioritize by impact, risk, and effort. Required corrections return to build and verify now if within authorized scope. Proposed changes go back through `/discover` step 4 for approval. Do not restart the whole lifecycle.

## 7. Verdict (definition of done)
Declare one of:
- **Done**: all approved material requirements implemented and verified; intended journeys work including recovery paths; required checks and any required independent review passed on the current code; status files reflect reality; authorized external actions completed.
- **Done with disclosed gaps**: as above except for named gaps the user has accepted or must now accept.
- **Not done**: list exactly what is delivered, what is unverified, and what remains.

Never manufacture done through documentation, status edits, or unrelated passing tests. An unresolved acceptance failure blocks a clean verdict regardless of severity.

## 8. Update files and report
Update REQUIREMENTS.md statuses and evidence, STATUS.md (milestone, limitations, deferred, next actions), DECISIONS.md for any decision made. Commit if work is on a branch.

Report in about 20 lines: Verdict, Delivered, Requirements (met and open with IDs), Verified (commands and results), Findings by class, Decisions needed, Next actions.
