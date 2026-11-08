---
name: reassess
effort: medium
description: 'Assess the delivered outcome at a major milestone, release readiness or an explicit review request. Reuse current evidence, check real user journeys and identify material gaps. Invoke independent review only for affected high-risk behavior or an explicit request. Ordinary progress questions do not require a full reassessment.'
---

# Reassess: confirm the outcome

Use this at the agreed major milestone or delivery boundary, not after every package or commit. An ordinary milestone needs outcome validation, not an automatic independent review. Select this skill internally; no user command is needed.

After loading this workflow, apply the core's effort selection if this work needs a level other than medium. Keep high effort for consequential reasoning, not routine evidence collection.

A standalone assessment authorizes inspection and a report. Edit code or records only when implementation or document maintenance is already authorized.

## 1. Compare scope, behavior and evidence
Read the objective, relevant requirements/decisions, cumulative diff and available check results. Reuse context and inspect changed sections; do not scan every record or recreate a register. Establish:
- Approved material behavior is implemented or has an authorized disposition.
- Main journeys, failure/recovery paths and affected invariants have relevant evidence.
- No unapproved scope appeared and no requirement disappeared.
- Only applicable operational concerns remain: deployment/rollback, configuration, data recovery and observability.

At major milestone completion, require the full relevant checks and applicable end-to-end journeys on the integrated candidate. Documentation-only work without executable or operational changes needs document checks, not app E2E. Reuse a valid completed run; run only missing evidence. A readiness question or new merge commit does not justify repeating unchanged checks. Test evidence may cover an identical tree with unchanged verification context; independent review has the separate scope below.

For a progress question or interim assessment, use available focused evidence and identify E2E as pending until its milestone. Do not launch a full browser matrix to answer a status question. Never present unobserved journeys, unavailable environments or simulated feedback as verified.

## 2. Review only when required
Use the fresh-context Claude `reviewer` for a **high-risk change** before merge/release, an explicit independent-review request, or a concrete newly discovered consequential risk before irreversible action. Classify the actual changed behavior using `../build/references/review-loop.md`; a performance/refactor label does not exempt security, personal data or migrations.

Low-risk milestones and releases do not require independent review. Do not add a reviewer just because the work was substantial or parallel.

When required:
1. Finish integration and checks, stop writes to the candidate and commit it. Gather existing evidence before review; the reviewer need not rerun trustworthy checks.
2. Reuse a clean approval only for the same **full HEAD SHA, scope, requirements and rules**, with valid evidence and no unresolved required finding.
3. Otherwise load `../build/references/reviewer-brief.md`. Use **one full review** for unreviewed cumulative changes and **one targeted follow-up** for required fixes or missing evidence. If only commit identity changed, obtain targeted confirmation of the final SHA and unchanged covered code, base integration, rules and scope instead of another full audit.
4. If blockers remain, report the issue and seek the necessary design/scope decision instead of cycling. New code commits invalidate prior approval; a test-cache hit does not restore it. Never approve high-risk delivery with required findings unresolved.

## 3. Resolve and report
Within authorized implementation, fix required defects through Build without restarting the lifecycle. Keep proposed scope additions separate and ask only about material decisions. Batch necessary tracking updates; keep gate output in Git-private storage, CI or PR records rather than creating a new tested-tree change.

Give one verdict with **2–5 concise user-facing lines**:
- **Done:** the requested scope is delivered, applicable acceptance and milestone checks passed, required review passed on the final HEAD, and authorized delivery actions are complete.
- **Done with disclosed gaps:** name the limits and their acceptance status.
- **Not done:** say what is delivered, what is unverified and the next necessary action.

An intermediate package may be implemented with focused checks while milestone E2E remains pending; do not call the milestone or release verified until its evidence exists. Never mark failed acceptance passed through documentation or a reviewer verdict.
