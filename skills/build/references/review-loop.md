# High-risk rules and independent review

Load only for high-risk behavior or a required independent review. Use affected/expanded verification during development under `testing-policy.md`; full end-to-end verification is required before production delivery, for unbounded impact or by an explicit project integration gate, not merely because a feature milestone ended.

## Before building high-risk behavior

Classify the actual changes: authentication, authorization, identity/security verification, consent, personal data, privacy/deletion, payments, migrations, destructive operations, production configuration, delivery controls and consequential concurrency require appropriate invariants and review. Merely running verification is not high-risk work. A performance or refactoring label does not exempt a migration or permission change.

Reuse existing rules and acceptance criteria. Write only missing consequential invariants, boundaries, retries/races and recovery behavior in the existing rules record. Ask the owner only about material ambiguity. Add focused acceptance/regression tests; use sequence/property tests when stateful risks justify them. Do not defer checks needed to protect data or an irreversible action until the milestone.

## Review tiers

- **Build:** No independent reviewer by default, including substantial low-risk performance, documentation or refactoring work. Run focused checks as changes warrant. Do not review per worker, increment or commit.
- **Reassess:** Use a fresh-context reviewer in the active host once at a major milestone, merge or release boundary that includes high-risk changes, or on an explicit independent-review request. A concrete newly discovered high risk may require earlier review before an irreversible action. Ordinary low-risk milestones and releases do not require a reviewer; their applicable verification still runs.
- **Reuse:** Reuse a clean approval covering the exact full HEAD SHA, requirements, rules and scope, with current test/CI evidence and no unresolved required findings. A tree-based test cache is not independent-review approval.

## Reassess gate procedure

1. Integrate and commit the candidate, then obtain the applicable checks once in a suitable environment or CI. Keep evidence tied to its full SHA outside tracked files. Reuse trustworthy results; reviewers do not rerun broad suites just to reproduce them.
2. Prepare a short brief using `reviewer-brief.md`: base/head, cumulative affected diff, applicable rules/acceptance, test evidence, uncertainties and prior findings. Pass paths and evidence, not the full conversation.
3. In Claude Code use the installed reviewer. In Codex use an authorized fresh native agent with the same read-only brief. If independent review is unavailable, report it as pending and continue work outside that gate. Prefer high effort for consequential review; explicitly requested low-risk reviews can use medium through a supported non-fork invocation override. Respect owner choices and host caps, and do not assume prose changes an external reviewer CLI's effort. It inspects evidence and affected integration, runs only checks that resolve a specific evidence gap, and **never edits**. Classify findings as `bug`, `spec_question` or `out_of_scope`, with severity and concrete evidence.
4. Fix required defects in scope with focused regression checks. Ask about material specification questions; keep unrelated improvements out of the loop. Required security/data failures still block readiness.
5. Allow at most **one full review and one targeted recheck** of required fixes or missing evidence. No new full sweep during recheck. If blockers remain or recur, report the exact issue and return to a design/scope decision; another cycle requires a materially changed plan and explicit authorization.
6. Approval applies only to the reviewed final HEAD/scope. If only commit identity changed, use targeted confirmation of the final SHA and unchanged covered code, base integration, rules and scope, within the recheck budget. Keep the gate pending until the final HEAD is approved; valid test evidence remains reusable separately. Never approve unobserved acceptance or unresolved required findings.
7. Record the approved SHA/scope and remaining blockers in existing evidence or tracking, without creating a bookkeeping commit that invalidates the gate. Report meaningful results and urgent risks, not every review exchange.

## Standing permissions

Follow owner-granted targets and conditions, required checks/CI and review when applicable. Do not infer merge permission or extend it to deployment, release, secrets, paid services or destructive production actions.
