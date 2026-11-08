# Vibe v4.7.0

Vibe now uses focused checks while implementing and validates the complete integrated result at major milestones. The coordinator chooses the workflow, checks and useful parallel work from normal requests.

## What changed

- **Focused development checks:** affected tests and useful lint/type checks during iteration. A full suite, production build or browser matrix is no longer the default after every edit, worker, commit or ordinary push.
- **One integrated milestone gate:** full relevant checks and E2E at an agreed usable feature or delivery boundary. Valid evidence is reused at release. Targeted browser/build checks and high-risk invariant checks still run earlier when the actual change needs them.
- **Selective independent review:** affected high-risk behavior or an explicit owner request. Low-risk releases and pure documentation/performance/refactoring work do not automatically get a reviewer. High-risk behavior inside those packages remains subject to review.
- **Less context overhead:** shorter core, Build and Reassess instructions; selective reads and reference loading; concise worker briefs; batched shared records and no per-edit board calls.
- **Progress in everyday language:** short updates for a nontechnical owner, in their language, covering the useful result, current work, next step and any decision. Task labels and the board follow the same approach; technical details remain available, and finished work is distinguished from checked or published work. No extra reporting agents or polling.
- **Automatic effort selection:** native medium defaults for the workflows and scoped workers, low for mechanical work and high for difficult reasoning or consequential review. Internal controls can change effort without user commands or another agent. Host/environment overrides remain authoritative; reading instructions alone does not apply a runtime setting.
- **Adaptive parallel work:** choose the worker count from ready independent work, resources and owner/runtime limits. One to three is a starting point, not a cap; ten or more can run immediately when justified. Keep one shared worker budget, preflight build/browser capacity, reserve scarce resources and bound performance experiments. No extra monitoring agents or review gates.
- **Optional verification reuse:** a stdlib-only helper and pre-push template for existing duplicate project gates. Evidence is scoped to the actual pushed tree, check mode, gate command and declared context; clean stable inputs are required. The helper is not registered as another Claude hook.
- **Less duplicate CI:** feature/release PRs use pull-request checks; main pushes remain checked before publication.

## Preserved boundaries

Project instructions and required CI retain precedence. The coordinator adapts an authorized workflow change to existing rules and hooks; updating Vibe alone does not replace stricter project policy. Reduced checks on a stack require a real deployment boundary, not rapid successive merges. Test reuse does not substitute for required CI or exact-HEAD independent-review approval.

## Verification and limits

See [verification details](RELEASE-4.7.md) for the checks run on this candidate. Publication remains gated by successful trusted main CI and an exact tested commit/tag.

No numeric delivery-time or model-token saving is claimed. The source instructions are shorter and default repeated work is removed, but authenticated comparative Claude runs and interactive UI observations have not been performed for this version. Effort metadata and native package validation do not prove that an owner's cloud host applied the requested setting; adoption uses available runtime evidence to confirm it. Existing installations need to load the updated plugin before the new policy applies; project-specific overrides remain authoritative.
