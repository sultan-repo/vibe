# Vibe v4.7.0 verification

## Scope

This candidate implements lighter milestone delivery, selective review, bounded parallel resource use and optional reuse of project verification. It changes Vibe only; it does not modify family-network or its deployment settings. Merge and publication have not been performed for this candidate.

## Evidence

Local candidate checks passed:

- `python3 -m unittest discover -s tests -v`: 30 tests, including 19 verification-cache regressions.
- `node --test tests/*.mjs`: 15 board/benchmark tests.
- `python3 hooks/test-force-push-hook.py`: all 28 safeguards.
- Shell/JSON/YAML syntax, matching project templates and exact startup-hook injection.
- Isolated install, reinstall and uninstall preserved personal files/settings and did not register a global verification gate.

Native strict plugin validation and Mod render tests run on the release PR and on main using pinned Claude Code 2.1.314. The Claude CLI is absent from the local executor; the pull request's CI records those outcomes rather than claiming a local native run.

The cache tests exercise real temporary Git repositories, including actual pre-push ref input, clean/dirty snapshots, full/quick reuse, context changes, failed verification and linked worktrees. They establish helper behavior, not the correctness of a project's adapted gate or its declaration of ignored/environment inputs.

A fresh-context read-only exercise covered an interim UI fix, constrained parallel workers, same-tree release, performance work with a migration, a progress question and a documentation-only release. It identified two wording gaps, resolved by making document-only E2E applicability explicit and using a bounded targeted confirmation for a changed commit identity with otherwise unchanged reviewed scope.

The core, Build and Reassess sources together changed from 3,409 to 2,291 whitespace-delimited words (about 33% less); the always-loaded core changed from 1,333 to 951 words (about 29% less). Word counts measure source size, not model billing tokens or runtime performance.

## Disclosed limits

Authenticated Claude execution and comparative elapsed-time/token measurements have not been run. A read-only scenario exercise checks policy consistency; it does not establish that live Claude always follows the policy. Interactive UI behavior remains unobserved for this version. The optional cache is not enabled in projects automatically and cannot infer every external verification input.

## Publication

The publisher accepts only a successful trusted main-push check run, verifies its exact source SHA, and creates/verifies the matching release tag. The published GitHub release adds the tested commit and CI URL. A passing release PR alone does not publish.
