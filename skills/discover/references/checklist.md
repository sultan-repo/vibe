# Enrichment checklist

Decide applicability first. Skip whole dimensions that do not fit the product. Do not add capabilities because they appear here; add them because omitting them would hurt the intended outcome.

## Dimensions

**Product and business**
- Intended value and success measures.
- Missing business rules.
- Adoption and usability.
- Valuable capabilities absent from the original idea.
- A different approach that achieves the objective better or more simply.

**Users and experience**
- Personas and roles.
- Complete user journeys, not isolated screens.
- Onboarding and configuration.
- Accessibility and responsiveness.
- Empty, loading, error, and offline states.
- Points of likely confusion.

**Operational workflows**
- Staff and administrator responsibilities.
- Approvals and supervision.
- Assignment and ownership.
- Status transitions.
- Escalation and manual intervention.
- Manual versus automated steps.
- Concurrent operations and handovers.

**Technology and integrations**
- Architecture and component boundaries.
- External APIs and dependencies.
- Platform and compatibility constraints.
- Data contracts and integration failure modes.
- Technical debt that blocks the objective.

**Security and data**
- Authentication and authorization.
- Sensitive-data protection.
- Consistency and integrity.
- Privacy, retention, deletion.
- Privilege changes and misuse cases.
- Backup, recovery, reconciliation.

**Reliability and performance**
- Timeouts and retries.
- Duplicate or conflicting operations.
- Partial failures and interrupted workflows.
- Scale, latency, resource use.

**AI and automation (when applicable)**
- Agent responsibilities and boundaries.
- Model limits, hallucination, wrong tool actions.
- Context and memory.
- Evaluation and fallback.
- Human oversight.

**Deployment and operations**
- Environment configuration.
- Deployment and rollback.
- Monitoring and diagnostics.
- Recovery, maintenance, support.
- Compliance requirements that apply.

## Scenarios to check per feature

1. Normal successful path.
2. Alternative valid paths.
3. Invalid input and invalid state.
4. User mistakes and undo.
5. Concurrent activity.
6. Security and misuse.
7. Network or dependency failure.
8. Partial completion and recovery.
9. Administrative intervention.
10. Interaction with existing functionality.

Prioritize omissions that would undermine the outcome. Ignore the rest.
