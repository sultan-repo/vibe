---
name: build
effort: medium
description: 'Implement requested software features, fixes and continuations from normal conversation. Coordinate useful parallel work, use focused checks during development and full integrated checks at major milestones. No slash command is required. Exclude explanation, discovery-only and review-only requests.'
---

# Build: deliver with minimal overhead

Use `$ARGUMENTS` when supplied; otherwise use the current request and authorized project state. **Continuous delivery is the default**: finish the approved outcome without stopping after each increment. Select skills internally; never ask the user to run workflow commands.

After loading this workflow, apply the core's effort selection if this work needs a level other than medium. Effort changes do not change acceptance or verification requirements.

## 1. Read only what this work needs
- Inspect project CLAUDE.md, git state and relevant code/tests. On resume, reconcile existing status with the code. Search large records for applicable decisions; do not reread unchanged files or load every reference.
- Missing continuity files do **not** force Discover. Use existing tracking. Invoke Discover only for requested exploration or unresolved material intent.
- For ongoing work, checkpoint the active task and branch in the canonical status record before substantial work or worker launches. Apply the core's state-change and handoff triggers; do not wait for a merge. Use the existing tracker when authoritative.
- Use the core's Fast path for small fixes. For Standard work, make a brief internal plan with the next major milestone: an agreed usable feature or delivery boundary, not each package. Identify focused checks now and the full integration/E2E checks due there. This is coordinator planning, not another owner checkpoint.
- For Critical behavior, load `references/review-loop.md` and identify the affected invariants. Clarify material ambiguity while continuing unaffected work.

## 2. Implement and check the change
- Prefer the smallest effective implementation. Deliver failure, empty and recovery paths where relevant; avoid speculative abstractions, agents and duplicate documentation.
- Add meaningful regression/acceptance tests for changed behavior. During iteration, run affected tests and useful lint/type checks. Do not automatically run the full suite, production build or browser matrix after each edit, commit, worker or push.
- Use a targeted browser check when the changed interaction cannot be validated adequately otherwise, or a build to diagnose a concrete build problem. Full end-to-end coverage belongs at the milestone; do not postpone critical invariant checks or remove failing checks.
- Delegate substantial independent tasks only when the time saved warrants the extra context. Load `references/parallel-work.md` for ownership, build/browser capacity and measurement budgets. Keep small or coupled work local.
- Commit coherent deliverables with human-readable, action-first commit titles; put IDs in the commit body, not the title. Continue authorized implementation without stopping after each increment.
- Reuse native task tracking if useful. Name tasks for the user's outcome in their language; keep engineering details in descriptions. Only the coordinator updates the plan at meaningful changes. Use optional `mcp__vibe__progress` only when native tracking is unavailable and a longer task benefits; never add board calls to Fast work or poll workers continuously. The board opens automatically where supported.

## 3. Complete the milestone
- Integrate workers against the current target base, resolve conflicts and finalize tracked edits. Run the project's full relevant checks and applicable end-to-end journeys once on that stable candidate. Documentation-only work without executable or operational changes needs document checks, not app E2E. A standalone bounded fix needs focused evidence unless risk or delivery requires more.
- Reuse valid test/CI evidence instead of rerunning unchanged checks in the coordinator, reviewer, push hook and release step. For an existing duplicate gate, load the optional `hooks/verification-cache.md` pattern from the Vibe plugin, or `~/.claude/vibe-tools/verification-cache.md` with the installer. Adapt it internally to project rules and existing hooks; never require the user to run setup commands or bypass checks.
- Use Reassess to confirm the milestone's outcome. Do not automatically request independent review for normal increments, low-risk performance/refactoring/docs or a low-risk release. A high-risk change needs one consolidated review before merge/release; an explicit review request also applies. Preserve exact-HEAD review scope separately from reusable test evidence.
- Combine simultaneous status changes into one coordinator update without delaying the core's triggers. Keep final verification output outside tracked files. Later status-only edits need applicable document checks, not another product gate by default; preserve required hooks/CI and the original evidence's scope. Never pre-mark a pending check passed. When E2E is deferred to the agreed milestone, report that fact without treating every intermediate task as a failed release.

## 4. Report the outcome
Apply the core's communication rules throughout the work. Finish with what the user can do now, what was checked and any remaining limitation in everyday language. Say whether the change is available to users or still awaiting publication. Link technical evidence when useful. Do not claim speed or token savings without a comparison. Stop only at completion or a real blocker, material decision or missing permission.

Before a handoff, confirm the canonical record and referenced unfinished work are saved remotely and discoverable from a fresh checkout or the declared tracker. Preserve the Now fields and Updated's default-branch baseline; keep feature commit/check evidence in resume details. Record branches, blockers and the next approved action; put necessary resume details below Now. Use existing scoped permissions, never merge unfinished product work just to save status. If persistence fails, preserve what is possible and report the unsaved gap. No extra agent, review or full suite is needed to write the checkpoint.
