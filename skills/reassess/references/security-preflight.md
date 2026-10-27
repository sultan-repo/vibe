# Targeted security preflight (only when risk justifies it)

Use at a Reassess high-risk pre-merge or release gate **only for affected surfaces**, not as a new mandatory agent or general scanner. This checklist supplements tests and the existing fresh-context Claude reviewer; it cannot certify security by itself.

## Applicability

Read changed files and the approved rules contract. Check only categories affected by the diff:
- **Auth/permissions:** server-side authorization on each reachable action, ownership checks, privilege escalation and revocation.
- **Consent/privacy/deletion:** exact affected entity, data retention, revoked state, retries, duplicate requests and cross-user isolation.
- **Secrets/config:** committed credentials and logs, access scopes, configuration/hook execution, MCP/tool permissions and unintended external connections.
- **User-controlled content:** validation, injection into SQL/shell/templates and prompt-injection boundaries where AI consumes untrusted content.
- **Money/irreversible operations:** idempotency, authorization, double submission, cancellation and recovery.

## Minimal procedure

1. Inspect the actual changed paths (`git diff --name-only <base>...HEAD`) plus the specific callers/config relevant to the risk. Never print secret values; report file paths or descriptions instead.
2. Reuse **existing** linters, security tests and dependency/secret scanning **if configured**. Do not silently install scanners, upload project files or change permissions.
3. List only **material** security findings with evidence and affected requirement ID. A confirmed approved invariant violation remains blocking. If no applicable security-sensitive surface changed, record `not applicable` in the Reassess evidence and stop.
4. Don't turn this check into an architectural redesign. New mechanisms or scope require the normal Discover/Approve path. The final Claude reviewer still enforces its one full pass plus one targeted recheck limit.

This is an evidence checklist, **not** an AgentShield replacement or claim of an automated vulnerability scan.
