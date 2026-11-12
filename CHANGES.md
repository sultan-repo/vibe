# Changes

**v4.12.1 (release candidate):** repairs Codex core truncation with a bounded handler allowance and explicit incomplete-preview guidance. Preserves native configured owner-instruction selection and later owner edits instead of shadowing fallback files with a new AGENTS.md. Repairs only owner-free legacy fallback reminders/bridges; uncertain routing or ambiguous owner content is left untouched for reconciliation. Corrects fenced-import detection and adds rollback plus private recovery copies for interrupted multi-file adoption writes. Adds deterministic transport/recovery tests and strengthens native Codex prompt tests to assert actual owner-rule content after adoption. Verification cadence, reuse-first decisions, review requirements, permissions, hook trust and publication guards remain unchanged. No new slash commands, agents, testing gates or checkpoint features. Abrupt termination is not claimed filesystem-atomic; live model adherence and time/token savings are not inferred from tests.

**v4.12.0 (release candidate)** adds Codex installation with first-session routing, keeps Claude Code's native installation, and shares project rules through AGENTS.md. Both hosts use the same Discover, Build and Reassess workflows.

**v4.11.0 (release candidate):** adds reuse-before-rebuilding guidance for substantial standard frontend and backend work. Prefer existing project code, installed dependencies and platform capabilities; evaluate maintained libraries from current authoritative sources when those are insufficient. Choose by total delivery and maintenance effort, requirement fit, security, compatibility and license constraints. Keep trivial low-risk work direct and product-specific rules explicit; do not replace working code merely because a library exists. Add a short core rule, an existing Build step, one on-demand reference and static policy regressions. No new slash command, runtime dependency, startup scan, mandatory research agent, dependency register or per-feature benchmark. Existing approval, verification and trusted-main publication protections remain unchanged. No measured speedup or unchanged defect-detection rate is claimed.

**v4.10.0 (release candidate):** adopts a small managed project policy automatically during authorized edits, including projects that did not go through Discover. Discover, Build and Reassess remain model-invocable but are no longer user commands. Adds bounded, change-aware startup gate advisories without executing project scripts or changing project protections. Adds optional evidence-only `check` and `pre-push --require-evidence` actions, preserving the shared evidence contract and existing run-on-miss behavior. Documents conditional background isolation and separate gate migration. Removes the progress board module, command/tool registration, board tests and active instructions while retaining native task tracking and continuity. Preserves required-check job IDs, strict plugin validation, release verification and independent review. This candidate is not a published release; no measured speedup or unchanged defect-detection rate is claimed.

**v4.9.0 (release candidate):** separates feature acceptance from production readiness with affected, expanded and release test scopes. Selects checks from cumulative changes and dependencies; shared/high-risk behavior, unknown impact and missing coverage expand verification. Completing a feature no longer implies a full E2E run. Full production verification, required CI, critical invariants and bounded independent review remain intact. Tightens the optional cache adapter's selection-scope contract without changing its executable modes or implementation. Updates both project templates and adds policy regression checks plus a bounded runtime-adoption plan. Existing projects are not migrated automatically; narrower project gates require authorized validation. No measured speedup or zero-quality-impact claim is made. Merging to main delivers this version to plugin users, so native plugin checks now run on every PR before merge as well as on main. Adds release notes, matching version/publisher metadata and regression checks for the release boundary. The core explicitly requires acceptance evidence for uncovered requirements; a larger green suite is not a substitute.

**2026-11-09, v4.8.0:** makes continuity checkpoints concrete: before substantial work starts, before ending a turn with a work-state transition, after merges/releases/deployments and immediately on an owner handoff signal. Only the coordinator writes status. Handoffs and unfinished work must be saved remotely under existing permissions and discoverable from the project's canonical record or authoritative tracker. Adds a compact Now summary and a local-only startup check in plugin and manual installations. Status-only commits do not make their own baseline stale; cached branch information is advisory. Unchanged turns add no checkpoint work, extra agent or verification gate. Includes hook, installation and fresh-checkout regressions. Abrupt termination before saving and unavailable remote persistence remain explicit limits.

**2026-11-09, v4.7.0:** makes focused checks the development default and runs full integrated checks/E2E at agreed major milestones or delivery boundaries. Removes automatic independent review from low-risk releases and discretionary review of ordinary increments. Reduces the core and Build/Reassess context, chooses agents and team size from the task and available capacity without preset numbers, budgets build/browser resources and performance measurements, and keeps shared records under the coordinator. Adds native effort selection: medium workflows/scoped workers, low mechanical work and high difficult reasoning/consequential review, with internal controls and explicit host limitations. Makes chat updates and progress labels natural for a nontechnical owner; the board uses factual finished-step counts, keeps technical activity in Details and separates finished work from checked or published work. Adds an optional verification-cache helper and pre-push template for projects with duplicate gates, without another always-on hook. Project rules, required CI, high-risk invariant checks and exact-HEAD review approval remain in force. Runtime speed, model usage and effective effort in the owner's host have not been benchmarked.

**2026-11-08, v4.6.0:** selects Discover, Build and Reassess from normal conversation, with slash commands retained as optional shortcuts. Automatically delegates substantial independent work to a small pool of native Claude subagents, with explicit ownership, dependency handling, worktree bases and combined verification. Keeps existing permissions and bounded final review. Fixes native TaskList progress updates and removes the board's command-only empty-state guidance. Runtime delegation performance and interactive UI behavior remain unverified; see the release notes for the disclosed limits.

**2026-10-31, v4.5.0 (release candidate):** consolidates PR #7 (continuous Fast/Standard/Critical execution and concise reporting), PR #8 (native optional progress board), and PR #9 (human-readable GitHub titles). Adds release-readiness checks and a matched Claude/Vibe benchmark harness. Rejected PR #6 (learning and security extras) is deliberately **excluded**. Real interactive UI and model timing evidence are release gates, not claimed as passed.

**2026-10-18, v4.4:** removed the external CLI reviewer, model configuration and its tests. Fresh-context Claude is Vibe's sole reviewer. Build handles small edits with normal checks and uses a focused Claude review only when useful. Reassess performs one consolidated final review for high-risk pre-merge, release readiness or explicit requests, with a maximum of one targeted recheck before escalating unresolved findings. Older installer artifacts are cleaned up during upgrade.

**2026-10-18, v4.3 (superseded):** introduced risk-aware business rules, model-based state tests, review triage and an optional external CLI reviewer. The external integration and related setup were removed in v4.4.


**2026-10-08, v4.2:** split discovery from building. `discover` now stops at the checkpoint and writes no code; it revises the checkpoint on each reply and hands off to the new `build` skill when the user approves. `build` applies decisions to the register, implements one approved increment, verifies, records evidence, commits, and stops. Every later session starts with `build` instead of "continue".

**2026-10-08, v4.1:** renamed the plugin, marketplace, and repo from `delivery-standard` to `vibe`. Skills are now `/vibe:discover` and `/vibe:reassess` when installed as a plugin. No change to the rules themselves.

---

## What changed from v3.0 to v4.0, and why

## Assessment of v3.0

The objective is sound and worth keeping: an agent that discovers what the product really needs, challenges weak decisions, enriches requirements with approval, builds complete journeys, verifies with evidence, and reassesses against the original purpose, while staying proportional. The lifecycle, the Required/Recommended/Optional classification, the requirements register, the evidence rules, and the "continue until done or blocked" directive are the strong parts and survive intact.

The problems are in form, not intent:

| Measure | v3.0 | Effect |
|---|---|---|
| Words / tokens on every turn | 4,201 / ~5,700 | Attention dilution; instructions near the middle get ignored; less room for code |
| Sections | 46 | Same rule restated in up to five places |
| Bullets | 271 | Reads as a checklist to execute, not rules to follow |
| "Do not / Never / Avoid" sentences | 44 | Prohibition-heavy prompts make the model timid and over-ask |
| "substantial / material" | 35 uses, never defined |
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
