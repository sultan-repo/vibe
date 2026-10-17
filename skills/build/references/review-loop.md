# Risk-aware review and bounded external review gates

Load when preparing high-risk rules or when Reassess decides independent review is required. Routine Build does not launch Codex.

## Before building high-risk logic

1. Classify risk by consequences (auth, consent, permissions, privacy/deletion, payment, migrations, destructive effects, production config, races), not diff size.
2. Confirm a concise rules contract in `docs/RULES.md` or an existing equivalent: actors, invariants, equivalence/identity, permitted action scope, transitions, retries/races, recovery, non-goals and relevant requirement IDs. Ask the owner only for material open decisions before implementation.
3. Test stateful rules with model-based/property/sequence tests when appropriate, otherwise record equivalent deterministic sequences. Normal tests and CI run during Build and remain required regardless of reviewer choice.
4. Keep individual increments coherent and reviewable. Do not introduce unapproved features during defect fixes.

## Two review tiers

- **Routine Build and intermediate milestones:** implementer runs tests and checks; optionally use the fresh-context Claude `reviewer` subagent once for a *substantial* increment where it adds value. Do not automatically review small changes. Claude handles normal defects and focused self-verification. No Codex review loop here.
- **Reassess independent gate:** run the configured independent reviewer only for high-risk *pre-merge*, release candidate, explicit independent review request, or an owner-approved exceptional risk. Collect changes since the prior review/base into **one consolidated review**. Do not review each increment or ordinary milestone independently. A high-risk PR must pass its pre-merge gate, even when the broader milestone is unfinished.
- On first setup, ask once "Use Codex CLI for final independent review? (Recommended: Yes; alternative: Claude reviewer.)" Record `Reviewer: codex-cli` or `Reviewer: claude-subagent` in project CLAUDE.md. A Codex preference is for **gate reviews**, not ordinary Build. Claude can still review intermediate work. Never silently switch the configured final reviewer if it fails.
- Codex uses local CLI/authentication only; check `command -v codex` and `codex login status` on the review machine. No pasted credentials or machine-wide config. Choose per-invocation reasoning: `medium` for documentation/tests or a narrow check, `high` for ordinary cumulative code, `xhigh` for critical state/consent/auth/concurrency. If the current model does not support the chosen effort, surface the error rather than silently downgrade.
- Installed via plugin: helper under `CLAUDE_PLUGIN_ROOT/scripts/codex-review.py`; install-script alternative: `~/.claude/vibe-tools/codex-review.py` (requires Python 3).

## Reassess review gate

1. **Check for reuse before running anything.** An existing clean approval is reusable only for the *same full HEAD SHA*, unchanged reviewed rules/requirements/scope, no unresolved required findings, and still-applicable test/CI evidence. An explicit request for a new review overrides reuse. Record the decision and SHA in STATUS.md.
2. **Gather actual evidence first.** Build/CI runs the project's tests in a writable environment, with commands, results, date, full HEAD and a link or log. Codex read-only mode is for code inspection, not for rerunning tests that require filesystem writes. The reviewer may accept trustworthy, checkable test/CI evidence it did not personally execute. Distinguish `unverified_requirements` (missing/untrustworthy acceptance evidence, BLOCKING) from `reviewer_limitations` (e.g. unable to rerun a test in read-only mode even though its CI log passes, NON-BLOCKING); never fabricate evidence or quietly drop an actual gap.
3. Commit a clean HEAD and prepare the reviewer brief outside the repo (see `reviewer-brief.md`). Include the cumulative diff/base, full SHA, rules and requirements, links to checks, evidence, and unresolved finding IDs. Run the selected reviewer. When using Codex from the project root:

   ```bash
   python3 /path/to/vibe/scripts/codex-review.py \
     --brief /tmp/vibe-review-brief.txt \
     --head "$(git rev-parse HEAD)" \
     --effort high \
     --output /tmp/vibe-review-result.json
   ```

   Use the actual risk-selected effort. The helper enforces read-only Codex execution, schema checks and fail-closed approval; it does not itself run tests, verify CI, merge or deploy. For a Claude-only gate, use the fresh-context `reviewer` subagent with the same brief and evidence requirements.
4. Triage every real finding: `bug` within approved scope gets a targeted fix and regression test; `spec_question` goes to the owner/DECISIONS; `out_of_scope` gets a deferred requirement ID. An approved safety invariant cannot be waived as out of scope. Classify blocker/required/minor with stable IDs. Do not expand the feature just to appease review.
5. **Hard stop against endless Codex rounds:** maximum **two Codex invocations per gate**: one full consolidated review, then **at most one narrowly targeted recheck** of blocker/required fixes or missing evidence. Claude can triage and locally verify the fixes before that recheck. Never launch a second full sweep automatically. After the second invocation, if blocked or a new substantial mechanism is needed, STOP the automatic loop; report the exact remaining blocker and options (redesign, split, owner decision). Do not treat the stop as approval, and do not bypass high-risk/release gates. An owner can explicitly authorize a fresh cycle only after a meaningful design/scope change, never just to keep retrying unchanged code.
6. If reviewer approval predates the last code commit, it cannot authorize the current HEAD. Reassess either performs the allowed targeted recheck or marks the gate blocked. All required acceptance evidence, applicable CI and independent approval must cover the final HEAD and scope. A pending review may coexist with verified local requirements, but never with a clean high-risk merge/release-ready verdict.
7. Keep round counts and prior findings in STATUS.md or a compact review record. Only inform the owner when a gate starts, ends or is blocked, or when urgent risk arises. Avoid round-by-round messages.

## Standing permissions

Owner-granted merge permission must explicitly name repository/branch, conditions (review, tests and CI on final HEAD) and exclusions. Never infer authorization or extend it to deploy, release, paid actions or destructive production changes.
