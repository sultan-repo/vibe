# Vibe v4.10.0

## Changes

- Vibe automatically adopts its principles in the active project during authorized editing, using a small managed policy block that preserves existing project rules. Read-only questions and plan mode do not write files.
- Discover, Build and Reassess are internal workflows selected from normal language. They are model-invocable, not commands the user must choose.
- Startup can report possible expensive commit/push or CI gates when a bounded configuration fingerprint changes. It resolves the actual hook path, executes no project scripts, and never disables existing protections.
- Optional `check` and `pre-push --require-evidence` actions consume matching verification evidence without launching tests on a miss. Missing, stale, insufficient or pending evidence blocks promotion. Existing run-on-miss behavior remains available.
- The progress board module, command/tool registration, tests and active guidance are removed. Native task tracking, concise updates, continuity and force-push safeguards remain.

## Limits and migration

Policy adoption does not automatically migrate project hooks/CI. Narrower development coverage still needs a bounded comparison against full checks; production verification, required CI and independent review remain intact. Evidence-only enforcement requires separate verification orchestration. Worktree isolation does not isolate shared ports or data, and evidence is worktree-local. Updating the helper invalidates old marker identities conservatively.

No measured speedup or unchanged defect-detection rate is claimed. Static advisories are not exhaustive shell analysis. Deterministic tests are not evidence of live model routing or application regression coverage. Complete the release-candidate checks and obtain owner authorization before publication.
