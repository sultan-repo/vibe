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
This project follows Vibe v4.7. Normal requests select the workflow; the user does not run workflow commands.
- Milestones: <usable features or delivery boundaries; do not make each task a milestone>
- During implementation: focused checks, no automatic full suite or independent reviewer per package/commit/push.
- At a major milestone: full checks and E2E once on the integrated candidate; reuse valid evidence at release. Run relevant high-risk checks before affected work merges.
- Independent review: affected high-risk behavior or an explicit owner request; low-risk documentation, performance and refactoring do not require it.
- Deployment boundary: <integrated delivery or separate release promotion; intermediate stack branches must not deploy alone with reduced checks>
- Standing permissions: <none, or exact authorized repository/branches/actions/checks/exclusions>
- Existing hooks/CI: <applicable project requirements; preserve them when adapting Vibe>

For duplicate verification, the coordinator may adapt Vibe's optional verification-cache helper and pre-push template to the existing gate. Reuse requires the actual pushed tree, a clean stable checkout, the right mode and unchanged declared context. Full includes quick only if the project defines that relationship. Test reuse does not replace required CI or reviewer approval. No owner setup command is needed.

## Conventions and continuity
<Only conventions that cannot be inferred from code. Use existing issues/ADRs/tasks; create extra records only when needed.>
The coordinator owns shared decision/status files and collects worker text through reports. Batch tracked edits before the full gate; record its final evidence outside tracked files.
