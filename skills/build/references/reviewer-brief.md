# Vibe independent reviewer brief (template)

- Repository / project:
- Base ref and full base SHA:
- **Head commit (full SHA):**
- Diff / affected behavior (links or commands):
- Approved increment + requirement IDs / acceptance criteria:
- Applicable rules contract sections and invariants:
- Tests, exact commands, outputs and date:
- Prior findings (stable IDs, claimed fixes, regression tests):
- Unknowns / expected failure and recovery paths:
- Out of scope / deferred IDs:

Inspect the diff *and* surrounding code. Do not edit files. Use blocker for dangerous correctness/security/data loss; required for unmet acceptance or reliability; minor for non-blocking maintainability. Categorize findings as bug/spec_question/out_of_scope. Cite concrete evidence and explain impact. Mark each prior finding fixed/open/disputed with evidence. Do not approve an unverified acceptance criterion. Do not silently assume an open spec question is resolved.

For Codex: return JSON matching `scripts/review-result.schema.json` exactly, including the full head_sha and final verdict APPROVE, APPROVE_WITH_REQUIRED_FIXES, or REJECT. For Claude subagent: use the same structure in prose.
