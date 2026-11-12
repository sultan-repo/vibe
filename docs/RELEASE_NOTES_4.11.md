# Vibe v4.11.0

## Reuse before rebuilding

Vibe now explicitly checks project code, installed packages and platform capabilities before building substantial standard frontend or backend functionality. When those are insufficient, it evaluates suitable maintained libraries using current authoritative sources before choosing a custom implementation.

The choice is based on total integration, testing, operational and maintenance effort, with requirement fit, security, compatibility and license constraints. Frontend evaluation includes accessibility, mobile, design fit and Arabic/RTL when required; backend evaluation includes deployment, data handling and recovery behavior.

Small low-risk helpers can stay custom. Product-specific business rules remain explicit. Existing working code is not replaced merely because a library exists. Unfamiliar or consequential integrations get a bounded representative check; a library's reputation is not application acceptance.

## Low overhead, unchanged protections

The policy uses a short core rule, an existing Build step and one on-demand reference. It adds no slash command, startup scan, mandatory research agent, dependency register or per-feature benchmark. Material choices are recorded briefly in existing tracking and shared with workers.

Paid services, external data sharing, major architecture changes and policy exceptions retain existing approval requirements. Verification, required CI, release protections, automatic project adoption and native task tracking are unchanged. No new runtime dependency is installed by this release.

No measured speedup or unchanged defect-detection rate is claimed. Static regression checks and plugin validation do not prove live model adherence or comparative token/time savings. Actual dependency decisions and their integrations must still be verified in the relevant project.
