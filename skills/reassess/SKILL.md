---
name: reassess
description: Product alignment review and definition-of-done check. Use at an ordinary milestone, before a high-risk merge or release, after a material requirements change, or when the user asks "are we done", "review the product", "what's missing", "does this still match the goal". Compares the objective, approved requirements, actual behavior, user journeys, and evidence; classifies gaps; updates docs/REQUIREMENTS.md and docs/STATUS.md; gives a done / not-done verdict with what remains.
---

# Reassess: does the software serve its purpose?

A finished task list, a green test suite, or a clean architecture does not prove the product is done. This skill checks alignment between the intended outcome, the approved requirements, the delivered behavior, and the evidence. It ends with a verdict and updated continuity files. Ordinary milestone reassessments do **not** automatically trigger a code-review round.

## 1. Gather inputs
- The objective and non-goals (project CLAUDE.md, STATUS.md).
- `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`.
- The code as it is now: `git log` and `git diff` since the last reassessment or milestone.
- Evidence: test runs, CI results, review findings, any user or operator feedback. Separate what was observed from what was claimed. Inspect any prior reviewer approval's full SHA, scope, required findings and evidence. For recurring defects, consult verified project lessons only when relevant; do not run continuous-learning hooks.

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
- Are reliability and security proportionate to the risk? For stateful high-risk rules, were invariants exercised against a model/sequence suite or justified deterministic equivalent? If a final gate is due, did the fresh-context Claude review cover the final HEAD?
- Is anything more complicated than the product needs?

## 4. Exercise the real software
Where the app can run here, walk the main user journeys and at least one failure path, and report what you saw. End-to-end tests count; unit tests alone do not for user-facing behavior. Never invent user feedback. If a real environment or real users are unavailable, use representative scenarios and say that this is the limitation.

## 5. Operational readiness (production-relevant systems only)
Check what applies: deployment and rollback, configuration and secrets handling, logging and monitoring, backup and recovery, data reconciliation, support and maintenance needs. Prefer existing infrastructure. Propose new operational tooling only against a concrete need.

## 6. Conditional final review gate

Reassess always checks requirements, real behavior and test evidence. When a high-risk or release gate affects security-sensitive surfaces, read `references/security-preflight.md` and assess only relevant changed paths using existing checks; skip when not applicable. Use the fresh-context Claude `reviewer` subagent only when:
- A high-risk change is about to merge (mandatory approval on the final HEAD);
- A release candidate is being declared ready (mandatory approval for relevant changed code);
- The user explicitly asks for an independent review;
- A newly discovered consequential risk requires earlier review before irreversible action.

At ordinary milestones and progress checks, do not run a reviewer automatically. Claude can still perform focused, lightweight reviews during Build for substantial changes when valuable.

First check whether a prior clean approval has the **same full HEAD SHA, scope and requirements**, with no unresolved required findings and valid current test/CI evidence. Reuse it unless the user explicitly requests a fresh review. Otherwise gather actual runnable test/CI evidence *before* reviewing and review the cumulative relevant diff once at the gate. A reviewer may inspect trustworthy recorded test results without rerunning every write-requiring command; a genuine absence of acceptance evidence remains blocking.

When required, load `../build/references/review-loop.md` and `../build/references/reviewer-brief.md`, then spawn the fresh-context `reviewer` subagent. Use at most **one full review plus one targeted follow-up** per gate. If blockers remain after that, stop and escalate for a design or scope decision, rather than endlessly patching. Record the reviewed final HEAD/scope and disposition in STATUS.md. A new code commit invalidates an approval for the previous HEAD. Never merge, release or mark a high-risk gate passed while required findings remain.

## 7. Classify each finding
- Missing approved requirement.
- Required defect correction.
- Approved requirement change.
- Proposed product enhancement.
- Architectural or operational improvement.
- Deferred capability.
- Accepted limitation.

Prioritize by impact, risk, and effort. Required corrections within authorized scope go to the `build` skill now. Proposed changes go back through the `discover` checkpoint for a decision. Do not restart the whole lifecycle.

## 8. Verdict (definition of done)
Declare one of:
- **Done**: all approved material requirements implemented and verified; intended journeys work including recovery paths; required checks passed, and a fresh-context Claude review passed (or was validly reused) on the exact HEAD and scope **when a final gate applies**; no unresolved required finding, safety invariant or material specification question; status files reflect reality; authorized external actions completed.
- **Done with disclosed gaps**: as above except for named gaps the user has accepted or must now accept.
- **Not done**: list exactly what is delivered, what is unverified, and what remains.

An ordinary milestone may be Done for that milestone without a final code review when no gate is due; that does not mean release-ready or high-risk merge-approved. Never manufacture done through documentation, status edits, or unrelated passing tests. An unresolved acceptance failure blocks a clean verdict regardless of severity.

## 9. Update files and report
Update REQUIREMENTS.md statuses and evidence, STATUS.md (milestone, limitations, deferred, next actions and final review status/SHA/scope when relevant), DECISIONS.md for any decision made. If the same verified fix recurs, apply the optional learning criteria in `../build/references/lessons-and-handoff.md`, but never add a lesson for each review finding. Commit if work is on a branch; any new code commit requires reconsidering final approval.

Report in about 20 lines: Verdict, Delivered, Requirements (met and open with IDs), Verified (commands and results), Findings by class, Decisions needed, Next actions.
