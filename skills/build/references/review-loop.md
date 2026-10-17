# High-risk rules and independent review

Load this reference only for a high-risk increment or a requested independent review. Keep small, low-risk work free of these steps.

## Before implementing high-risk behavior

1. Classify risk by consequences, not diff size. Auth, permissions, consent, privacy/deletion, payments, destructive changes, data migrations, production settings, concurrency, and irreversible external effects qualify.
2. Write the minimum *rules contract* needed to remove ambiguity: actors and permissions; business invariants; identity/equivalence (what counts as "the same" event, invitation, payment, or request); transitions and action scope; retries, races, reversals, and deletion; deliberate non-goals. Add it to `docs/RULES.md` or an existing equivalent, linked by requirement IDs.
3. Ask the owner to confirm material rules before implementing them, alongside the normal discover checkpoint. Do not request approval for details already answered or minor implementation choices.
4. Define acceptance examples, including invalid, concurrent, retry, and recovery sequences. For high-risk *stateful* logic, run property/state-machine or randomized sequence tests against a simple reference model before independent review. If unsuitable, explain why and use deterministic sequences instead.
5. Scope each increment to one reviewable behavior/rule area. Soft limit, not an arbitrary line cap. Split independent mechanisms into separately approved increments before review.

## Reviewer choice (one-time onboarding)

In the first discover checkpoint, or before the first independent review if discover was skipped, ask exactly once: **"Use Codex CLI as your default independent reviewer? (Recommended: Yes; alternative: Claude reviewer.)"** Batch this with other decisions rather than forcing a separate setup wizard.

- Record `Reviewer: codex-cli` or `Reviewer: claude-subagent` in project CLAUDE.md under Delivery. When unset, ask once; do not assume Yes. A declined Codex choice means use the existing fresh-context Claude reviewer.
- If Yes, verify `command -v codex` and `codex login status` *on the machine running the review*. Give setup guidance if missing. Do not request credentials, copy sign-ins, change global Codex config or silently switch reviewer.
- For Codex, select per-invocation reasoning effort: `medium` for documentation/tests-only or very light follow-ups; `high` for normal implementation and narrow rechecks; `xhigh` for critical logic, complex state/concurrency and the final approval review of high-risk code. Respect project-specific constraints; if the selected model rejects the level, surface that limitation and ask before changing model or effort. Do not silently downgrade.
- Use the currently authenticated Codex model unless the user explicitly chooses another. A model and its available reasoning levels may change; no hardcoded model name is required.
- For a plugin install, find this plugin's `scripts/codex-review.py` relative to its installation root (`CLAUDE_PLUGIN_ROOT` when available). For the script install, use `~/.claude/vibe-tools/codex-review.py`. Require Python 3 for the helper.

## Review loop for each approved increment

1. Implement only approved behavior. A review fix may modify supporting code essential to that behavior, but must not add a distinct API, entity, mechanism, or user journey as an unapproved feature. Material discoveries return to discover and become another increment.
2. Run relevant checks and the user journey *before* review. State what ran and record test evidence. Commit a clean worktree so review has an immutable HEAD. For high-risk stateful logic, the model-based sequence tests above are a gate.
3. Prepare a reviewer brief in a temporary file **outside the repo**. Include base and **full head SHA**, diff scope, requirement IDs with acceptance criteria, applicable rules document sections, relevant tests and outputs, uncertainties, previous finding IDs and their claimed fixes, severity definitions, and the required verdict schema. Provide enough context to inspect surrounding behavior, not just the diff.
4. When configured for Codex, from the project root invoke (replace paths and SHA):

   ```bash
   python3 /path/to/vibe/scripts/codex-review.py \
     --brief /tmp/vibe-review-brief.txt \
     --head "$(git rev-parse HEAD)" \
     --effort xhigh \
     --output /tmp/vibe-review-result.json
   ```

   Use `medium`, `high`, or `xhigh` as assessed, not always `xhigh`. The wrapper enforces local sign-in, a clean matching commit, read-only Codex execution, structured output and a fail-closed verdict. It does **not** run the project's tests, confirm CI status or authorize merges. With the Claude reviewer choice, spawn the fresh-context `reviewer` subagent using the same brief, demand evidence and record a verdict. That path has no automatic CLI gate; treat unverified acceptance criteria as blocking.
5. Triage **every** finding:
   - `bug`: a defect in approved behavior. Fix within scope and add a regression test.
   - `spec_question`: behavior ambiguous or a material product choice. Pause the affected area, record the owner's answer in DECISIONS.md, update rules/requirements, then implement.
   - `out_of_scope`: unrelated improvement, linked to a deferred requirement ID. **Never** defer a bug that violates an approved safety invariant merely because the fix needs new code.
   Classify severity as **blocker**, **required**, or **minor** and retain stable finding IDs across rounds. Do not resolve disputed findings merely by relabeling them.
6. After **three unsuccessful review rounds**, or **one recurrence of a blocker in previously reviewed code**, stop the patch/review loop. Diagnose root cause and offer: redesign within approved rules, narrow/split scope (with approval for changed behavior), or request the owner's decision. Do not call the increment verified while required findings remain.
7. Track round number, blockers/required findings, regression tests and next action concisely in STATUS.md. Save detailed evidence in an existing tracker or a dedicated `docs/reviews/` record only when needed. Notify the owner when the loop starts, hits its stop rule or finishes; surface urgent risk immediately, not every round.
8. Final completion requires: latest committed HEAD, acceptance checks observed to pass against that code, any required property/stateful tests, no unresolved blocker/required finding or material spec question, and an independent approval on that exact HEAD. A new code change invalidates the previous approval. Project CI/branch protection still governs actual merge.

## Standing permissions

The owner may explicitly grant `merge when X` authorization in project CLAUDE.md: target branch/repo, allowed PR category, passing required CI, tests against the final HEAD, independent approval for that HEAD, and exclusions. Never infer permission from silence. A standing merge permission never implies push to a different repo, release, deploy, publish, secrets change, paid action or destructive production change. Stop if any condition cannot be verified.
