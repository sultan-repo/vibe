# Vibe independent reviewer brief (template)

- Repository / project:
- Base ref and full base SHA:
- **Head commit (full SHA):**
- Diff / affected behavior (links or commands):
- Approved increment + requirement IDs / acceptance criteria:
- Applicable rules contract sections and invariants:
- Tests, exact commands, outputs, trusted CI URL, dated evidence and commit SHA:
- Prior findings (stable IDs, claimed fixes, regression tests):
- Unknowns / expected failure and recovery paths:
- Out of scope / deferred IDs:
- Gate type (high-risk pre-merge, release, or explicitly requested) and review history: full review or targeted recheck, number of prior Codex calls:

This is a **single consolidated gate review**, not an invitation to propose feature additions. If marked *targeted recheck*, inspect only listed required fixes, related integration and evidence, not a fresh full sweep. Tests that need writes run in Build/CI, not in this read-only review. Accept traceable passing CI/test evidence when credible. Put inability to personally rerun those tests under optional `reviewer_limitations`, **not** `unverified_requirements`. The latter is only for acceptance claims lacking trustworthy proof.

Inspect the diff *and* surrounding code. Do not edit files. Use blocker for dangerous correctness/security/data loss; required for unmet acceptance or reliability; minor for non-blocking maintainability. Categorize findings as bug/spec_question/out_of_scope. Cite concrete evidence and explain impact. Mark each prior finding fixed/open/disputed with evidence. Do not approve an unverified acceptance criterion. Do not silently assume an open spec question is resolved.

For Codex: return JSON matching `scripts/review-result.schema.json` exactly (optional `reviewer_limitations` lists inspection constraints, not defects), including the full head_sha and final verdict APPROVE, APPROVE_WITH_REQUIRED_FIXES, or REJECT. For Claude subagent: use the same structure in prose.
