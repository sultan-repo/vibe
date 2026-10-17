# High-risk rules and bounded Claude review

Load this reference when preparing high-risk behavior or when Reassess requires a final review. Small changes do not need review ceremony.

## Before building high-risk behavior

1. Classify by consequences, not diff size. Auth, consent, permissions, personal data, privacy/deletion, money, migrations, destructive actions, production config and consequential concurrency are high-risk.
2. Write a concise rules contract (docs/RULES.md or existing equivalent), linked to requirement IDs: actors, permissions, invariants, equivalence/identity, transitions and action scope, retries, races, recovery and non-goals. Ask the owner to confirm only material ambiguities.
3. Add acceptance examples. For stateful high-risk rules, use randomized/property/state-machine sequences against a reference model when useful, otherwise explain equivalent deterministic coverage.
4. Keep each increment coherent. Fix defects in approved scope without smuggling new features into a fix loop.

## Review tiers

- **Build:** Implement, test, lint/typecheck and exercise the actual user journey. Claude may invoke its fresh-context `reviewer` subagent for a focused check of a meaningful substantial increment. Do **not** automatically review trivial changes or launch multiple independent reviews for each intermediate commit.
- **Reassess:** Review product alignment at ordinary milestones without an automatic code-review round. At a **high-risk pre-merge gate**, **release-readiness gate**, or **explicit review request**, use the fresh-context Claude `reviewer` subagent for a consolidated, independent check of relevant changes. A new material risk may justify an earlier review when necessary for an irreversible action.
- **Reuse:** If a successful independent review already covers the same exact full HEAD SHA, requirements, rules and scope, with valid test/CI evidence and no unresolved required findings, record and reuse it. Do not review unchanged code again unless the user explicitly requests a fresh pass.

## Reassess gate procedure

1. Run project checks *before review* in a suitable writable environment (or CI); record commands, outcomes and evidence tied to the full commit SHA. The reviewer can accept trustworthy CI/test evidence without personally repeating every command. Distinguish unproven acceptance from a reviewer execution limitation; never call an unverified acceptance criterion passed.
2. Commit the final code and prepare a reviewer brief outside the repo using `reviewer-brief.md`. Include the base and full HEAD SHA, cumulative diff, applicable invariants, requirement IDs, test/CI output, known uncertainties and previously reported findings.
3. Invoke the fresh-context `reviewer` subagent with the brief. It reads code and available evidence and runs checks where possible, but **never edits**. Classify each finding as `bug`, `spec_question`, or `out_of_scope`, with severity blocker/required/minor, stable ID and evidence.
4. Fix real bugs in scope and add regression tests. Refer material specification questions to the owner and record decisions; defer unrelated improvements under a requirement ID. Never defer an approved security/data invariant just because its fix is nontrivial.
5. **Stop automatic loops:** Allow at most **one full reviewer pass and one targeted recheck** of required fixes or missing evidence for the current gate. Do not launch a new full sweep in the recheck. If blockers remain or a previously reviewed blocker recurs, stop, report the exact issue and return to design/scope decision. Do not approve or merge high-risk work while required findings remain; a new review cycle requires a material changed plan and explicit authorization.
6. Approval is valid only for the reviewed final HEAD/scope and must be accompanied by passing relevant acceptance checks and CI. New code commits invalidate that approval; record the gate as pending until it passes again. A pending gate does not erase valid local test evidence.
7. Track the review status (pending/approved full SHA, covered scope, outstanding severity and next step) concisely in STATUS.md. Inform the owner on gate start, stop or finish, and immediately for urgent risk, not for each review comment.

## Standing permissions

Any owner-granted permission to merge requires exact conditions and repo/branch targets, plus current acceptance tests, CI and a required review approval. Never infer merge permission or extend it to deployment, release, secrets, paid services or destructive production actions.
