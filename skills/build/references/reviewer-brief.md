# Vibe independent reviewer brief (template)

- Repository / project:
- Base ref and full base SHA:
- **Head commit (full SHA):**
- Diff / affected behavior (links or commands):
- Approved increment + requirement IDs / acceptance criteria:
- Applicable rules contract sections and invariants:
- Tests, exact commands, outputs, date and commit SHA (CI links where available):
- Prior findings (stable IDs, claimed fixes, regression tests):
- Unknowns / expected failure and recovery paths:
- Out of scope / deferred IDs:
- Gate (ordinary focused Build review, high-risk pre-merge, release, explicit request):
- Review attempt (full first pass or one targeted recheck) and previous findings:

Inspect the diff *and* surrounding code. Do not edit files. Use blocker for dangerous correctness/security/data loss; required for unmet acceptance or reliability; minor for non-blocking maintainability. Categorize findings as bug/spec_question/out_of_scope. Cite concrete evidence and explain impact. Mark each prior finding fixed/open/disputed with evidence. Do not approve an unverified acceptance criterion. Do not silently assume an open spec question is resolved.

For the fresh-context Claude reviewer, return a concise evidence-based report with the reviewed full HEAD SHA, requirements coverage, findings by severity and stable ID, any limitations, and one clear verdict: APPROVE, APPROVE WITH REQUIRED FIXES, or REJECT. When this is a targeted recheck, inspect the specified fixes and affected integration, not a new full sweep.
