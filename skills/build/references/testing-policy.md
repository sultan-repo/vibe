# Change-aware verification

Load for nontrivial test selection, uncertain impact or authorized gate adoption, not every turn. The coordinator selects checks during existing planning. This is a coverage policy, not another agent, scheduler or mandatory register. Fast/Standard/Critical describe execution; affected/expanded/release describe test coverage.

## Select the coverage, not the ceremony

| Scope | Trigger | Required evidence |
| --- | --- | --- |
| **Affected** | Bounded feature or fix with understood dependencies | Relevant unit/integration checks, targeted E2E for changed journeys and their failure/recovery paths, and useful lint/type/build checks. Documentation-only changes with no executable or operational effect need document checks. |
| **Expanded** | Shared behavior, consequential risk, uncertain impact or inadequate evidence | Tests for affected consumers, contracts and critical invariants, plus relevant browser/device journeys. Use full relevant checks when impact cannot be bounded. |
| **Release** | Any production delivery, including a small release or auto-deploying merge | Full relevant project suite and applicable E2E on the integrated release candidate, or valid full evidence for those same inputs. Include required deployment, migration and rollback checks. |

Feature completion, a worker finishing, a PR, a milestone label or a non-deploying push does not itself require full E2E. An explicit project integration gate still applies. Re-evaluate combined impact when integrating features; do not assume individually isolated branches remain isolated together. Keep cheap broad unit/lint/type checks when selecting a subset costs more than running them. Never remove tests or reduce assertions to improve timing.

## Establish affected behavior

Use the current integration base and cumulative changes, not just the latest commit. Include staged, unstaged and relevant untracked changes, renames/deletions, and changes brought in from the target branch. When the base is missing or stale, or the combined impact cannot be established, use expanded scope and full relevant checks until bounded.

Trace changed behavior to its consumers and acceptance criteria using existing test organization, dependency information and project knowledge. Include shared UI/layout/styles, API contracts, routes, authorization, data schemas, background jobs, configuration/flags, dependencies/lockfiles and fixtures as applicable. Different filenames or directories do not prove isolation. A dependency-based changed-test selector is a heuristic, not sole proof of coverage, particularly across UI/API or external-service boundaries.

For a bounded change, identify the affected journeys, dependencies, checks and any exclusions in the existing plan or evidence. Reuse an existing feature-to-test map when available; update only the changed mapping when necessary. Do not create a mandatory registry or scan the entire repository on every turn. Selection is revisited when scope, dependencies, base or failures change, not on unchanged conversation turns.

Changed UI journeys need observed browser evidence, including applicable failure/recovery paths and affected devices. A unit pass alone is not UI acceptance. An unavailable environment is unverified, not a reason to substitute an invented pass. Build only when the change needs build evidence; reuse the same candidate's build across browser/device checks when inputs match.

## Expand rather than guess

- Shared code, contracts, routing, global styling or configuration require consumer coverage, not only the edited feature's tests. Include affected browser/device combinations; a desktop pass does not establish a mobile-specific fix.
- Authentication, authorization, identity/security verification, consent, personal data, privacy/deletion, payments, migrations, destructive actions, production configuration, delivery controls and consequential concurrency require critical invariants before merge and required independent review. A small diff or refactor label does not exempt them. Use expanded scope; use full relevant checks when their impact cannot be bounded.
- Missing coverage, an empty selection, zero executed tests for changed behavior, unexplained failures or a stale/unknown dependency map cannot establish acceptance. Add relevant coverage or expand to established checks. Do not use a zero-test-success option to turn missing evidence into a pass. A full green suite also cannot prove an uncovered new requirement; add its acceptance evidence.
- An unexpected failure triggers diagnosis and affected/dependent regression, expanding further if its cause is unclear. Do not retry a full suite blindly, discard a failure as unrelated without evidence, quarantine it or weaken a gate just to finish. A fixed defect needs regression evidence before acceptance.

## Keep production and review gates intact

Full release coverage applies before every production delivery, not only major versions. Establish which branches, tags or merges can deploy. A branch that can deploy alone needs its own full delivery evidence. Merging a stack quickly is not a deployment hold; reduced development checks require one integrated delivery or an explicit release promotion.

Existing project rules, hooks, required CI and independent-review gates remain in force. A Vibe update does not authorize disabling or rewriting them. During authorized adoption, reconcile contradictory project instructions and scripts together; preserve the old gate until the replacement is validated. Report an overriding project gate rather than silently bypassing it.

A high-risk change still needs one consolidated fresh-context Claude review and at most one targeted recheck under `review-loop.md`. Exact-HEAD approval, unresolved required findings and external-action permissions are separate from test coverage. Selecting fewer tests never grants merge or deployment permission.

## Reuse evidence without widening its claim

Reuse requires a stable tested snapshot, sufficient coverage and unchanged inputs: code/tree, cumulative selection base, selected tests/filters, test-map/adapter version, browser/device projects, dependencies, configuration, fixtures and relevant environment. Recheck missing or invalidated evidence only. Evidence for a subset does not certify a superset; a test count or green exit code alone does not establish coverage.

For duplicate gates, use the optional `hooks/verification-cache.md` contract (or its installed `vibe-tools` copy). Its executable modes remain **quick/full**, not affected/expanded/release. A project adapter maps affected/expanded selections to quick only when their scope and context are represented; release maps to full with the complete required suite. Never relabel quick evidence as full. The context must fingerprint the selection contract and base as well as external inputs. If scope or mutable external state cannot be represented safely, do not cache those checks.

Full satisfies quick only under an explicit coverage-superset contract. Keep full and quick records separately. A failed or interrupted rerun invalidates prior evidence for the same inputs. Required CI is not bypassed by a local cache hit, and test evidence is not exact-HEAD review approval. Keep results outside tracked files so reporting does not change the candidate.

Report passed, failed, skipped, pending and unavailable checks distinctly in existing evidence. A feature may be accepted with affected/expanded coverage while full release E2E remains pending. Never describe that feature verdict as full release readiness.

## Validate adoption once, then measure

Before relaxing a project's existing full-development gate, run a bounded shadow comparison on representative changes against the same candidates and environment: an isolated feature, shared UI/API changes, a high-risk change, and missing/incorrect selection. Replay known regressions where available. Compare targeted results with the full suite and inspect every omitted failure. No missed regression in a small sample is a check on the mapping, not a guarantee of future quality.

If selection misses a relevant failure or impact cannot be bounded, keep expanded/full checks and correct the mapping before adoption. Also verify that push/release reuse preserves full evidence and invalidates it after changed inputs or a failed rerun. Record elapsed time and duplicate runs; do not claim speedups or unchanged defect detection without evidence. This comparison is an adoption check, not a new dual-run requirement for every feature. Preserve the full production gate afterward.

See `docs/TESTING-VALIDATION.md` in the repository for the policy's acceptance scenarios and runtime limits.
