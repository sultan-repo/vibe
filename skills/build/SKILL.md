---
name: build
user-invocable: false
effort: medium
description: 'Implement requested software features, fixes and continuations from normal conversation. Coordinate useful parallel work, select affected or expanded checks during development and require full integrated verification before production delivery. No slash command is required. Exclude explanation, discovery-only and review-only requests.'
---

# Build: deliver with minimal overhead

Use `$ARGUMENTS` when supplied; otherwise use the current request and authorized project state. **Continuous delivery is the default**: finish the approved outcome without stopping after each increment. Select skills internally; never ask the user to run workflow commands.

After loading this workflow, apply the core's effort selection if this work needs a level other than medium. Effort changes do not change acceptance or verification requirements.

## 1. Read only what this work needs
- Inspect project CLAUDE.md, git state and relevant code/tests. On resume, reconcile existing status with the code. Search large records for applicable decisions; do not reread unchanged files or load every reference.
- Apply the core's automatic project adoption during authorized edits, even when this project did not go through Discover. Use the existing policy block when current; adoption does not migrate test gates.
- Missing continuity files do **not** force Discover. Use existing tracking. Invoke Discover only for requested exploration or unresolved material intent.
- For ongoing work, checkpoint the active task and branch in the canonical status record before substantial work or worker launches. Apply the core's state-change and handoff triggers; do not wait for a merge. Use the existing tracker when authoritative.
- Use the core's Fast path for small fixes. For Standard work, make a brief internal plan with the next useful outcome and actual deployment boundary. Choose affected, expanded or release scope from the cumulative diff, dependencies and acceptance criteria. A feature milestone does not automatically require the full suite. Load `references/testing-policy.md` for nontrivial selection, uncertain impact or gate adoption; keep the reason and pending release checks in existing tracking, not a new register or owner checkpoint.
- For Critical behavior, load `references/review-loop.md` and identify the affected invariants. Clarify material ambiguity while continuing unaffected work.

## 2. Implement and check the change
- Before substantial standard frontend or backend functionality, apply the core's reuse-before-rebuilding rule: inspect existing code, installed packages and platform features first. For a new dependency or nontrivial choice, load `references/reuse-policy.md`, verify current official sources, and compare only credible options against the actual requirements. Keep small low-risk helpers direct. Record material decisions briefly in existing tracking, share the choice with workers, and test the difficult integration before broad adoption. Do not turn this into mandatory browsing for every edit or a rewrite of working code.
- Prefer the smallest effective implementation. Deliver failure, empty and recovery paths where relevant; avoid speculative abstractions, agents and duplicate documentation.
- Add meaningful regression/acceptance tests for changed behavior. During iteration, run affected tests and useful lint/type checks. Do not automatically run the full suite, production build or browser matrix after each edit, commit, worker or non-deploying push. Keep cheap broad checks when selection adds overhead.
- Exercise changed user journeys with targeted E2E, including relevant failure/recovery paths and affected devices. A unit pass alone is not UI acceptance. Use a build when changed behavior or a concrete build risk requires it. Expand to consumers for shared changes, high-risk invariants, missing coverage or unexplained failures; zero selected tests for changed behavior is not a pass. Run full relevant checks when impact cannot be bounded. Never postpone critical checks or remove failing checks.
- Delegate substantial independent tasks only when the time saved warrants the extra context. Load `references/parallel-work.md` for ownership, build/browser capacity and measurement budgets. Keep small or coupled work local.
- Commit coherent deliverables with human-readable, action-first commit titles; put IDs in the commit body, not the title. Continue authorized implementation without stopping after each increment.
- Reuse native task tracking if useful. Name tasks for the user's outcome in their language; keep engineering details in descriptions. Only the coordinator updates the plan at meaningful changes. Do not introduce a custom progress UI or poll workers continuously.

## 3. Complete the outcome or delivery gate
- Integrate workers against the current target base, resolve conflicts and re-evaluate cumulative impact. Run missing affected/expanded checks on the integrated result, not just worker snapshots. Feature completion alone does not trigger full E2E. Require full relevant checks and applicable end-to-end journeys before any production release/deployment, an auto-deploying merge, or an explicit project integration gate; also broaden fully when impact cannot be bounded. Documentation-only work without executable or operational changes needs document checks, not app E2E.
- Reuse valid test/CI evidence instead of rerunning unchanged checks in the coordinator, reviewer, push hook and release step. For an existing duplicate gate, load the optional `hooks/verification-cache.md` pattern from the Vibe plugin, or `~/.claude/vibe-tools/verification-cache.md` with the installer. Preserve coverage scope/base and all relevant inputs; a subset pass is not full evidence. Adapt only within authorized project work, preserving existing gates until their replacement is validated. Never require setup commands or bypass checks.
- Use Reassess to confirm the outcome without resetting its test scope. Do not automatically request independent review for normal increments, low-risk performance/refactoring/docs or a low-risk release. A high-risk change needs one consolidated review before merge/release; an explicit review request also applies. Preserve exact-HEAD review scope separately from reusable test evidence.
- Combine simultaneous status changes into one coordinator update without delaying the core's triggers. Keep final verification output outside tracked files. Later status-only edits need applicable document checks, not another product gate by default; preserve required hooks/CI and the original evidence's scope. Never pre-mark a pending check passed. Report feature acceptance separately from release readiness, with deferred full E2E explicitly pending.

## 4. Report the outcome
Apply the core's communication rules throughout the work. Finish with what the user can do now, what was checked and any remaining limitation in everyday language. Say whether the change is available to users or still awaiting publication. Link technical evidence when useful. Do not claim speed or token savings without a comparison. Stop only at completion or a real blocker, material decision or missing permission.

Before a handoff, confirm the canonical record and referenced unfinished work are saved remotely and discoverable from a fresh checkout or the declared tracker. Preserve the Now fields and Updated's default-branch baseline; keep feature commit/check evidence in resume details. Record branches, blockers and the next approved action; put necessary resume details below Now. Use existing scoped permissions, never merge unfinished product work just to save status. If persistence fails, preserve what is possible and report the unsaved gap. No extra agent, review or full suite is needed to write the checkpoint.
