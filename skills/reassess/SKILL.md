---
name: reassess
description: Product alignment review and definition-of-done check. Use at a milestone, before a release, after a material requirements change, or when the user asks "are we done", "review the product", "what's missing", "does this still match the goal". Compares the objective, approved requirements, actual behavior, user journeys, and evidence; classifies gaps; updates docs/REQUIREMENTS.md and docs/STATUS.md; gives a done / not-done verdict with what remains.
---

# Reassess: does the software serve its purpose?

A finished task list, a green test suite, or a clean architecture does not prove the product is done. This skill checks alignment between the intended outcome, the approved requirements, the delivered behavior, and the evidence. It ends with a verdict and updated continuity files. Reassess owns independent review decisions, but **an ordinary milestone does not automatically trigger Codex**.

## 1. Gather inputs
- The objective and non-goals (project CLAUDE.md, STATUS.md).
- `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`.
- The code as it is now: `git log` and `git diff` since the last reassessment or milestone.
- Evidence: test runs, CI results, review findings, any user or operator feedback. Separate what was observed from what was claimed. Inspect the previous independent review's full HEAD SHA, covered scope, findings and evidence when present.

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
- Are reliability and security proportionate to the risk? For stateful high-risk rules, were invariants exercised against a model/sequence suite or justified deterministic equivalent? If independent review is required now, does approval cover the final HEAD and affected scope?
- Is anything more complicated than the product needs?

## 4. Exercise the real software
Where the app can run here, walk the main user journeys and at least one failure path, and report what you saw. End-to-end tests count; unit tests alone do not for user-facing behavior. Never invent user feedback. If a real environment or real users are unavailable, use representative scenarios and say that this is the limitation.

## 5. Operational readiness (production-relevant systems only)
Check what applies: deployment and rollback, configuration and secrets handling, logging and monitoring, backup and recovery, data reconciliation, support and maintenance needs. Prefer existing infrastructure. Propose new operational tooling only against a concrete need.

## 6. Independent review gate (conditional)

Decide *after* evaluating requirements and evidence. Modes:

| Reassess occasion | Review decision |
| --- | --- |
| Ordinary milestone / progress alignment | No automatic external review. Verify requirements, tests and user journeys and record deferred review if appropriate. |
| High-risk change before merge | Mandatory independent review of the **final HEAD** and affected rules/requirements before declaring merge-ready. If merge is not imminent, record review pending rather than re-reviewing each increment. |
| Release candidate / publish-readiness check | Mandatory independent review covering material changes since the last approval on the final HEAD, even for otherwise normal work. |
| Explicit user request for independent review | Run it, even on unchanged code, unless the user explicitly asks to reuse an earlier review. |
| Newly discovered material architecture/integration risk | Recommend review now. Make it mandatory only if the action is high-risk or needed for a release gate. |

Before starting Codex, check for a reusable independent approval: same exact full HEAD SHA, unchanged requirements/rules and review scope, no open required findings, and test/CI evidence still applicable. If all hold, reuse it and record the reviewed SHA and scope in STATUS.md. Otherwise review the cumulative diff since the relevant previous approval or agreed base **once at the gate**, not once per prior increment. A new code commit invalidates the old approval for that gate.

When review is needed, load `../build/references/review-loop.md` and `../build/references/reviewer-brief.md`. Use the selected Codex CLI or fresh-context Claude reviewer, auto-selecting reasoning effort based on review risk. Ask the onboarding preference once if absent; never silently switch reviewer. Run tests in a writable environment or CI *before* a read-only review; record commands, outcomes and trusted evidence with the commit SHA. A reviewer may assess auditable test/CI evidence without personally rerunning write-requiring tests. Lack of trustworthy proof remains blocking. A reviewer's inability to rerun verified tests in a read-only sandbox is a *reviewer limitation*, not by itself a failed acceptance criterion; report it separately from actual `unverified_requirements`. Keep genuine acceptance gaps separate from execution limitations.

Triage findings as bugs, spec questions or out-of-scope improvements with stable IDs. Codex gets **one consolidated full review plus at most one targeted recheck per gate**. After that, stop automatic Codex cycles and escalate unresolved blockers to design or the owner. Do not weaken the gate or pretend the unresolved change is merge-ready. Avoid reviewing intermediate minor changes that Claude and tests can handle. Approval alone never replaces passing checks or CI, and this skill does not authorize a merge or deployment.

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
- **Done**: all approved material requirements implemented and verified; intended journeys work including recovery paths; required checks pass; if an independent review gate applies, it passed or was validly reused for the exact HEAD and scope; no unresolved required finding, safety invariant or material spec question; status files reflect reality; authorized external actions completed.
- **Done with disclosed gaps**: as above except for named gaps the user has accepted or must now accept.
- **Not done**: list exactly what is delivered, what is unverified, and what remains.

An ordinary milestone may be **Done for that milestone** without independent review when no gate applies; this does not mean release-ready or high-risk merge approved. Never manufacture done through documentation, status edits, or unrelated passing tests. An unresolved acceptance failure blocks a clean verdict regardless of severity.

## 9. Update files and report
Update REQUIREMENTS.md statuses and evidence, STATUS.md (milestone, limitations, deferred, next actions, review needed/skipped/reused/executed with SHA and scope), DECISIONS.md for any decision made. Commit if work is on a branch. Do not commit new code after an independent approval without reassessing that gate.

Report in about 20 lines: Verdict, Delivered, Requirements (met and open with IDs), Verified (commands and results), Findings by class, Decisions needed, Next actions.
