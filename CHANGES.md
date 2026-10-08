# What changed from v3.0 to v4.0, and why

## Assessment of v3.0

The objective is sound and worth keeping: an agent that discovers what the product really needs, challenges weak decisions, enriches requirements with approval, builds complete journeys, verifies with evidence, and reassesses against the original purpose, while staying proportional. The lifecycle, the Required/Recommended/Optional classification, the requirements register, the evidence rules, and the "continue until done or blocked" directive are the strong parts and survive intact.

The problems are in form, not intent:

| Measure | v3.0 | Effect |
|---|---|---|
| Words / tokens on every turn | 4,201 / ~5,700 | Attention dilution; instructions near the middle get ignored; less room for code |
| Sections | 46 | Same rule restated in up to five places |
| Bullets | 271 | Reads as a checklist to execute, not rules to follow |
| "Do not / Never / Avoid" sentences | 44 | Prohibition-heavy prompts make the model timid and over-ask |
| "substantial / material" | 35 uses, never defined | The whole proportionality model depends on an undefined word |
| "significant / consequential / meaningful / important" | 36 uses | Same problem |
| "but not for small tasks" disclaimers | 11 | Symptom of the missing definition |

Net effect: the prompt is more likely to produce long checkpoints and process narration than to raise the quality of the code. The biggest single fix is defining "substantial" with concrete anchors and routing the heavy procedures behind that definition.

## Removed

- **Section 19 (Final Operating Rules)** and the **Governing Principle** trailer: pure restatement of sections 1 and 18.
- **Section 15 (Prevent Drift)**: duplicate of 5.2 and 6. Its one new idea, "always maintain a clear next step", moved to the STATUS.md format.
- **Section 16 (Momentum)**: duplicate of section 1's closing rule. Its one new idea, "when blocked, name the precise missing decision", moved to the approval rules.
- **Section 14 (Operational readiness)**: four generic sentences. Folded into `/reassess` step 5 where it has a trigger (production-relevant systems at a milestone).
- **The role title stack** in the mission. Modern models do not perform better with six titles; one sentence states the role.
- **Duplicated "do not fake completion" rules** in 5.3, 11.5, 13.4, 17: stated once in the core, enforced once in `/reassess` step 7.
- **11.2 CI sub-bullets** ("configure checks on PRs, make checks visible, protected branch policies"): reads as a platform-admin checklist and invites the agent to add CI unprompted. Kept: run existing checks, never weaken a failing check, CI changes need authorization.
- **Rules Claude Code already enforces** in its own system prompt: faithful reporting of test results, finishing the whole task, confirming before destructive actions, reading before asking. Harmless but they were the first candidates for cuts.
- **Most of the 44 prohibitions**: rewritten as positive rules where the positive form is actionable ("Verify with executable evidence and report the command and result" instead of "Do not invent test outcomes").

## Added

1. **A definition of Small / Substantial / High-risk** with concrete anchors (files touched, new dependency, schema or contract change, auth, payments, personal data, migrations). Every proportionality rule now hangs off it. "Small is not low-risk" kept as an explicit line.
2. **A precedence rule**: current-conversation instruction > project CLAUDE.md > the standard. v3.0 never said what happens when the user wants a quick hack; now the agent does it and lists what was skipped.
3. **Fixed file names and locations** for continuity: `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`, `docs/STATUS.md`, with templates. v3.0 said "create a lightweight register" but not where, which produces a different file per session, exactly the drift it warned about.
4. **An end-of-turn protocol** to mirror the session-start protocol: update statuses and evidence, update next actions, commit.
5. **Decision-request format**: batch the questions, attach a recommendation and a default to each, continue with non-dependent work. v3.0 said "ask only for material decisions" but not how, and open-ended questions block autonomous runs.
6. **Git discipline**: feature branch for substantial work, commit per coherent increment naming requirement IDs, never force-push or rewrite shared history, never commit secrets. Absent in v3.0 apart from "push only when authorized".
7. **Concrete triggers for independent review** (the High-risk list and large diffs) instead of "when likely to materially improve the result". Review is expensive; it needs a trigger, not a judgment call.
8. **A size budget and template for the checkpoint** (one screen, fixed sections) and for milestone reports (about 15 lines). v3.0 listed contents but no bound.
9. **Running-software verification rule**: for user-visible changes, exercise the journey when the app can run; unit tests alone do not count for UI behavior.
10. **Mapping onto Claude Code mechanisms**: skills for the two procedures, a subagent for the reviewer, hooks for the one rule that must never be broken, plan mode as an optional way to run `/discover` without edits.

## Modified

- "Mandatory Delivery Lifecycle" → "Lifecycle". The section itself said it was not mandatory ceremony.
- The 3.1 dimension list (eight categories, about fifty bullets) and 3.2 scenarios became a reference file loaded only by `/discover`. Same content, loaded once per feature instead of on every turn.
- The register (5.1) keeps all eight fields but gains a status vocabulary with transitions, a rule for what deserves a row (material requirements, not every criterion), and "write `unverified` rather than leaving evidence blank".
- Independent review (12) moved into the reviewer agent's own prompt. The agent has a fresh context by construction, which is the only way the "not inherited the implementer's conclusions" requirement is actually met. The three-cycle limit is kept; escalation now means "present the unresolved finding with options".
- Product alignment review (13) and Definition of Done (17) merged into `/reassess` with a three-way verdict: Done, Done with disclosed gaps, Not done.
- Communication (18): the milestone summary is now the only mandated report format, with a length bound.
- Tone: bold and emphasis removed except in the checkpoint template. Rules are stated once, plainly.

## What stayed the same on purpose

- The seven-stage lifecycle and its names.
- Required / Recommended / Optional / Not applicable classification.
- "Challenge findings must cite evidence or be marked as a hypothesis."
- "A requirement is verified only when acceptance was observed to pass on the current code."
- "Continue through authorized work until the outcome is delivered or a genuine blocker requires my decision."
- No mocks or placeholders for required behavior without approval and a visible label.
