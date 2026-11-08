# Vibe independent reviewer brief (template)

- Repository / project:
- Base and **head commit (full SHAs)**:
- Gate: high-risk milestone/merge/release, explicit request, or concrete earlier risk:
- Affected diff, integration paths and scope exclusions:
- Applicable requirements, rules and acceptance criteria:
- Checks: commands, results, date, tested SHA/context and evidence links:
- Prior findings (stable IDs, claimed fixes, regression tests):
- Remaining evidence gaps / material uncertainties:
- Attempt: one full pass or the targeted recheck; recheck scope:

Keep the brief outside tracked source. Link primary evidence instead of copying histories or logs. Inspect affected integration; never edit. Reuse credible passing checks and run more only to resolve a named evidence gap. A recheck covers the reported fixes, not a new audit.

Return the reviewed full HEAD SHA, concise acceptance coverage, evidence-backed findings with stable IDs and severity, prior-finding disposition, limitations and one verdict: APPROVE, APPROVE WITH REQUIRED FIXES or REJECT. Unverified acceptance and unresolved required findings cannot receive APPROVE.
