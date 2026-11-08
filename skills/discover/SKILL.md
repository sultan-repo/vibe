---
name: discover
effort: medium
description: Automatically explore product intent and resolve material uncertainty from normal conversation. Use for brainstorming, discovery or planning requests, or an unresolved product or architecture decision. No slash command is required. Clear approved implementation proceeds through Build without a mandatory checkpoint; discovery-only requests do not authorize project edits.
---

# Discover → Challenge → Enrich → Approve

Goal: improve the product direction without blocking clear implementation. Explicit Discover requests produce analysis and a concise decision checkpoint, not application code. Ordinary Build requests with an understood objective and approved decisions skip this skill entirely.

After loading this workflow, apply the core's effort selection if this work needs a level other than medium.

Input: `$ARGUMENTS` is the idea or feature. If empty, use the request already in the conversation.

Select this workflow internally from intent; never ask the user to run a command to start it or continue to Build. For discovery-only requests, report proposed file changes in the answer. Instructions below to create or update project files apply only to authorized implementation or explicitly requested document work.

## 1. Discover (facts before questions)

Establish from evidence:
- The problem, intended users, desired outcome, and how success will be measured.
- Current state. Read relevant code/tests, config and recent changes; search existing records for the decisions that affect this work. Reuse context rather than rereading whole logs. Trust code over docs.
- Constraints, non-goals, operating environment, dependencies, integrations.
- Risks and unknowns. Classify high-risk by impact, including consent, auth, deletion, payments, permissions, concurrency and data integrity; do not equate a small diff with low risk.

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

For high-risk changes, read `../build/references/review-loop.md` (or the installed build skill). Reuse or draft concise invariants and recovery rules; ask only about unresolved material choices. Use sequence/property tests where they add evidence, otherwise use adequate focused examples.

Five strong recommendations beat twenty weak ones. Include only findings that would change the outcome if omitted.

## 4. Approve (the checkpoint)

Present one checkpoint, ideally 5–10 short lines, only when a material decision is needed. Use this shape selectively:

- **Objective**: one sentence. **Size**: substantial or high-risk, and why.
- **Confirmed requirements**: describe the important observable behavior in plain language; keep any R-IDs in internal records.
- **Gaps found (Required)**: what, why it matters, evidence.
- **Recommended**: at most three consequential choices, each with its tradeoff and recommended default. Avoid a wide table unless it improves clarity.
- **Assumptions I will proceed on** unless corrected.
- **Decisions needed now**: numbered, each with a recommendation. No reviewer setup question is needed; Vibe uses its existing fresh-context Claude reviewer when a review is genuinely required.
- **Plan**: the next useful outcome; internal milestone codes stay out of user-facing text.

If the repository has no `CLAUDE.md`, create one from `references/project-claude-template.md` with the objective, non-goals, and constraints agreed in the checkpoint; fill the Commands section once the stack is decided.

Record material approved rules, focused checks, the major milestone where full E2E is due, and any high-risk review requirement. No external reviewer configuration or authentication is required.

Use existing project tracking. For long-running projects that need it, create or update relevant continuity files using `references/register-template.md`; do not require all three files or update them when no material state changed.

When material decisions remain, stop for the owner's answer. If the user already gave approval or clear defaults, record them and proceed to `build` in the same conversation when implementation was requested. An explicit request for discovery alone ends with the checkpoint and does not change application code.

- If the user replies with changes or questions: address them concisely; only stop again if an important decision remains. Do not default to multiple rounds.
- If the user approves (a clear yes, "go", "go with your recommendations", or answers to the decisions) and implementation was requested: record material decisions in existing tracking, then invoke the installed `build` skill internally and continue the approved outcome in the same conversation. Approval of a design during discovery-only work does not itself request implementation.

Proposed items stay proposed until the user says yes. In plan mode, present the checkpoint; create project files only after leaving plan mode and when the requested work authorizes those edits.

## Proportionality

If the implementation request is clear, proceed directly to Build regardless of file count. If the user requested discovery only, return the analysis without code. A requested quick hack uses the Fast path with disclosed limitations; applicable safety rules still hold.
