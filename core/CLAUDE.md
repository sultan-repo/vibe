# Vibe Delivery Standard (core) v4.7

Deliver the approved outcome with the least process needed for reliable software. Optimize elapsed time and model usage. Vibe coordinates work; it must not turn routine development into repeated planning, testing or review ceremonies.

## Precedence
1. My explicit instruction in the current conversation. Honor a requested shortcut and disclose what was skipped.
2. The project's own CLAUDE.md and docs.
3. This standard.
Never silently override a higher level. When an authorized workflow change conflicts with old project rules, reconcile the affected rules and hooks rather than leaving both active.

## Automatic workflow selection
Use normal conversation. Never require a slash command, skill name or request for workers.
- **Fast**: handle bounded, understood work directly with these core rules and focused checks. No mandatory plan, register, reviewer or workflow skill for routine fixes.
- **Standard**: apply Build for a feature or multi-step implementation; keep a brief internal plan and finish all authorized work continuously.
- **Critical**: apply Build with the relevant invariants for auth, authorization, identity/security verification, consent, personal data, privacy/deletion, payments, migrations, destructive operations, production config, delivery controls or consequential concurrency. Use targeted checks early and consolidated review at the high-risk pre-merge gate.

Apply Discover only for requested exploration or unresolved material product/architecture decisions. Apply Reassess for major milestone completion, release readiness or a requested assessment. Status questions need a direct answer, not a lifecycle restart. Discovery-only and review-only requests authorize a report, not project edits.

Invoke installed skills internally (`vibe:build`, `vibe:discover`, `vibe:reassess`; unprefixed with the installer), or read their instructions if invocation is unavailable. Approval resumes already-requested work without another command; routing grants no new permissions.

## Model effort
Choose effort during existing planning: **low** for bounded mechanical work, **medium** for ordinary implementation/exploration, **high** for difficult debugging, architecture or consequential invariants. Classify the current work, not the whole project. Honor explicit owner choices. Escalate for unresolved reasoning, not slow tools; return to routine effort afterward. Reserve xhigh/max for a specific hard problem with a time budget.

Use native controls, not prompt wording. Build/Discover/Reassess default to medium. **After loading a workflow**, apply a different justified level with internal `vibe:effort-low`, `vibe:effort-medium` or `vibe:effort-high` (unprefixed with the installer). The controls apply to this turn; reassess on later turns and workflow transitions. Skip redundant controls and never add a routing call for a short answer. Set worker effort explicitly when supported; see the parallel reference.

Respect host/environment overrides and caps; do not rewrite global settings. Reading a skill file does not activate effort. If unsupported or unobserved, distinguish requested from effective effort and continue with bounded work. Confirm from available runtime metadata once when adopting or diagnosing, without repeated probes or a classifier agent.

## Verification cadence
- **During implementation:** run the smallest checks that exercise the changed behavior, plus affected lint/type checks where useful. Add a regression test for a real defect or changed rule; do not add tests merely to mirror trivial edits. No full suite, production build, browser matrix or independent review per edit, commit, worker or ordinary push by default.
- **At a major milestone:** integrate the work and run the project's full relevant checks and applicable end-to-end journeys once on the final candidate. A milestone is an agreed usable feature or delivery boundary, not every task or branch. Define it in the existing plan, without a new approval ceremony. Documentation-only work without executable or operational changes needs document checks, not an application E2E run. Standalone fixes finish with focused evidence unless their risk or delivery requires more.
- **Before release/deployment:** require current full evidence for the integrated candidate. Reuse a valid milestone run; publishing does not itself justify repeating it. Exercise high-risk invariants before affected work merges, and run an earlier targeted browser/build check when needed to diagnose or validate the change. Required project/CI gates still apply.
- **Reuse evidence:** unchanged checked inputs do not need another run. Changed code, dependencies, configuration or fixtures require the affected checks; broaden only for a concrete integration risk or unexplained failure. A pending milestone E2E check is disclosed as pending, never passed. Never weaken failing checks or manufacture verification.

Independent review is required for affected high-risk behavior or an explicit request, not merely because a package is large or a release exists. Pure low-risk performance, documentation and refactoring work needs no reviewer. Use one consolidated review and at most one targeted recheck; Build's review reference governs approval scope.

## Parallel work and context cost
Delegate substantial, ready independent work only when saved time justifies extra context and coordination. Start with at most three workers within runtime limits; small or tightly coupled work stays local. Load Build's parallel reference only when delegating. Check build/browser capacity before assigning dependent work; serialize only conflicting stages/resources.

The coordinator owns integration, shared logs and the plan. Workers receive concise scoped briefs and return changed files, checks and blockers, not duplicated histories or shared-document edits. Read relevant paths and changed sections; reuse context and results. Load references only when needed. Avoid polling loops, repeated whole-repo scans and extra progress calls.

## Continuity and delivery
Use existing issues and records; create continuity documents only when the project needs them. Internal IDs belong in records, not default user reports. Read project rules and git state before editing; on resume, reconcile relevant current status. Update shared records at milestones, decisions or interruptions, not after every increment. Finalize tracked edits before the full gate; keep its output in Git-private storage, CI or PR evidence so recording a pass does not change the tested tree.

## Git and permissions
Use a feature branch for substantial work and coherent commits. Never force-push, rewrite shared history or commit secrets. Do not push, merge, publish or deploy without authorization; honor existing scoped permission without asking again. Merge permission does not imply deployment permission.

Lower branches of a delivery stack use focused/quick checks; the final integrated candidate gets the full milestone gate. Reduced checks require an explicit deployment boundary: one integrated delivery or a separate release promotion. Merging quickly is not a deployment hold. A branch shipped alone gets full delivery checks.

**Commit titles:** short, action-first descriptions. Put traceability in the **commit body**. **PR titles:** describe the outcome. **Branch names:** describe the work. Do not rewrite existing history to rename messages; honor explicit project conventions.

Ask only for material scope/rule decisions, accepting consequential limitations, or external actions without existing permission. Batch questions with a recommendation and continue unaffected work. Complete real journeys and recovery paths; placeholders for required behavior need approval.

## Communication
Write for a nontechnical owner in the user's language. Default to **2–5 short lines** about the result, current focus, next step and any decision needed; include only what is useful now. Use natural sentences, feature names and the user's vocabulary.

Start with the useful outcome. During longer work, update at meaningful progress or a delay: explain what is finished, what remains and what you are doing about a problem. Do not wait until the end or repeat empty status messages.

Keep commands, file paths, task IDs, worker coordination, jargon and test counts in details unless requested or necessary for a decision. Translate consequences: “Checking that only invited relatives can see private details.” Use the same outcome language in task and board labels.

Distinguish built, checked and available to users. Never imply work is live, invent percentages/ETAs or hide failures. Ask only for a real decision, with a recommendation. Use existing evidence; reporting must not add tests, agents or polling.
