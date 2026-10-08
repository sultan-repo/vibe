---
name: discover
description: Requirements discovery, challenge, and enrichment before building substantial work (a new project, feature, user journey, integration, schema or contract change). Produces a one-screen checkpoint of confirmed requirements, gaps, recommendations, and decisions, then seeds docs/REQUIREMENTS.md, docs/DECISIONS.md, and docs/STATUS.md. Use at the start of any substantial task, or when the user says "discover", "plan this feature", "what am I missing", "challenge this design".
---

# Discover → Challenge → Enrich → Approve

Goal: help the user end up with a better product than the one they described, without uncontrolled scope growth. The output is a short checkpoint and an updated requirements register, not a document.

Input: `$ARGUMENTS` is the idea or feature. If empty, use the request already in the conversation.

## 1. Discover (facts before questions)

Establish from evidence:
- The problem, intended users, desired outcome, and how success will be measured.
- Current state. For an existing repo, read the code, tests, config, CI, recent git log, and any `docs/REQUIREMENTS.md`, `docs/STATUS.md`, `docs/DECISIONS.md`. Trust code over docs.
- Constraints, non-goals, operating environment, dependencies, integrations.
- Risks and unknowns.

Label each item as **confirmed fact**, **assumption**, **existing decision**, or **proposed change**. Ask the user only what the repo cannot answer, and ask inside the checkpoint, not one question at a time.

## 2. Challenge

Test the proposed approach against the objective. Look for incorrect assumptions, incomplete workflows, fragile architecture, unnecessary dependencies or infrastructure, missing security boundaries, unrealistic expectations, and a simpler alternative.

Every challenge cites evidence (a file, an observed behavior, a constraint) or is marked as a hypothesis. For a significant architecture choice, compare two or three credible options on functionality, complexity, risk, maintainability, and operating cost, then recommend one. Skip the comparison when the approach is conventional and the repo already follows it.

## 3. Enrich

Read `references/checklist.md` once and select only the dimensions that apply to this product. For each affected user or operational journey, model it end to end: start, actors and permissions, state transitions, valid alternatives, errors, concurrency, interruption, retry, cancellation, admin intervention, final visible outcome. Look hardest for failures that appear successful but leave data inconsistent.

Classify every meaningful finding:
- **Required**: needed for the approved objective, an existing constraint, or basic correctness. Enters the register as approved.
- **Recommended**: materially improves value, experience, or reliability. Needs a scope decision.
- **Optional**: future enhancement. Goes to the deferred list in STATUS.md only if worth remembering.
- **Not applicable**: dropped without mention.

Five strong recommendations beat twenty weak ones. Include only findings that would change the outcome if omitted.

## 4. Approve (the checkpoint)

Present one checkpoint, one screen at most, in this shape:

- **Objective**: one sentence. **Size**: substantial or high-risk, and why.
- **Confirmed requirements**: R-01, R-02 ... one line each.
- **Gaps found (Required)**: what, why it matters, evidence.
- **Recommended (your decision)**: a table with item, benefit, cost, impact if omitted, my recommendation, and the default if you do not answer.
- **Assumptions I will proceed on** unless corrected.
- **Decisions needed now**: numbered, each with a recommendation.
- **Plan**: milestones in order, first increment named.

If the repository has no `CLAUDE.md`, create one from `references/project-claude-template.md` with the objective, non-goals, and constraints agreed in the checkpoint; fill the Commands section once the stack is decided.

Then create or update the three continuity files using `references/register-template.md`: confirmed and required items as `approved`, recommended items as `proposed`, architecture choices in DECISIONS.md with the reason, and a one-screen STATUS.md.

Start the first increment immediately if it is authorized and independent of the open decisions. Build only approved scope. Proposed items stay proposed until the user says yes.

## Proportionality

If step 1 shows the work is actually small, say so in one line and go straight to implementation. If the user asked for a quick hack, do the hack and list what was skipped under deferred.
