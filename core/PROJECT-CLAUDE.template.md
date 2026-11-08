# <Project name>

## Objective
<The problem, intended users, useful outcome and success measure.>

## Non-goals and constraints
- <Non-goals, stack, compatibility requirements and prohibited actions.>

## Commands (the coordinator runs these)
- Install/run: `<commands>`
- Focused checks: `<affected tests and lint/typecheck commands>`
- Full milestone gate: `<project checks and end-to-end journeys>`

## Delivery
This project follows Vibe v4.8. Normal requests select the workflow; the user does not run workflow commands.
- Progress: short, natural updates for a nontechnical owner in their language. Explain the useful result, current focus, next step and any real decision. Keep engineering details in records; distinguish work finished from checked and available to users.
- Milestones: <usable features or delivery boundaries; do not make each task a milestone>
- During implementation: focused checks, no automatic full suite or independent reviewer per package/commit/push.
- At a major milestone: full checks and E2E once on the integrated candidate; reuse valid evidence at release. Run relevant high-risk checks before affected work merges.
- Independent review: affected high-risk behavior or an explicit owner request; low-risk documentation, performance and refactoring do not require it.
- Model effort: Vibe selects native low/medium/high effort by the current work; honor explicit owner choices and host limits. Confirm effective settings from available runtime evidence when adopting, without user commands or global settings changes.
- Deployment boundary: <integrated delivery or separate release promotion; intermediate stack branches must not deploy alone with reduced checks>
- Standing permissions: <none, or exact authorized repository/branches/actions/checks/exclusions>
- Existing hooks/CI: <applicable project requirements; preserve them when adapting Vibe>

For duplicate verification, the coordinator may adapt Vibe's optional verification-cache helper and pre-push template to the existing gate. Reuse requires the actual pushed tree, a clean stable checkout, the right mode and unchanged declared context. Full includes quick only if the project defines that relationship. Test reuse does not replace required CI or reviewer approval. No owner setup command is needed.

## Conventions and continuity
<Only conventions that cannot be inferred from code. Use existing issues/ADRs/tasks; create extra records only when needed.>
Continuity source: <canonical docs/STATUS.md on the shared branch, or the existing authoritative issue/tracker link; omit for one-off work that needs no record>.
The coordinator owns shared decision/status files; workers return their text in reports. Follow the core's start, state-change and handoff triggers, not merges alone. Keep a ten-line Now summary with Updated (date and code baseline), Position, In progress (branches), Next task and Waiting on owner; resume details/history stay below it. Save the record and referenced unfinished work remotely under existing permissions; disclose any gap. A new session must be able to resume from the declared source alone.
Batch simultaneous changes. Finalize tracked edits before the full gate and keep its evidence outside tracked files; later status-only edits need applicable document checks, preserving required hooks/CI. Startup automatically loads docs/STATUS.md's Now block when present and may warn using local Git information; it performs no network lookup. No owner command is needed.
