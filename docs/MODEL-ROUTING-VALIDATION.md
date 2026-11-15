# Capability routing: validation and adoption

**Purpose:** acceptance evidence for capability routing in v4.15.0, not a claim that unobserved runtime cases passed.
**Read when:** reviewing this change or diagnosing host routing. Normal tasks use the small core and on-demand [routing reference](../skills/build/references/model-routing.md).

## Scope and delivery boundary

Built on main/release v4.14.0 (`af080f173bb183ef8471ed4cd2381d50b3e638fb`). This changes native-control instructions, skill/agent metadata and project templates. No new resolver service, hook, model catalog, per-turn lookup or provider credentials. Existing installation, permission, test-selection and release mechanisms remain intact. Existing projects are not rewritten by this change.

Keep the PR unmerged and unpublished until current release checks and independent review pass and the owner explicitly authorizes delivery. Marketplace installs follow main, so merging would deliver these changes. The v4.15.0 version metadata, notes and publisher must agree before merge; retaining earlier metadata is not permission to ship changed behavior under the released version. Use the trusted-main publisher after authorized merge, not publication from a PR check. See [release verification](RELEASE-4.15.md).

## Acceptance cases

| Scenario | Required result |
| --- | --- |
| Owner pins a main model or effort | Workflow loading does not reset it; only a permitted scoped override is considered. |
| Mechanical worker versus consequential reviewer | Assign fast versus deep needs, resolve suitable native model/effort pairs; no fixed version IDs. |
| Main model cannot be switched safely | Keep it; delegate only already-useful work through supported controls. |
| Native model discovery is absent or partial | Do not invent aliases or infer absence from incomplete pagination; preserve known-suitable settings or disclose uncertainty. |
| Unknown/new model | Use documented capabilities or an owner mapping, not name/version ranking. |
| Claude forced model, allowlist substitution or effort cap | Preserve restrictions; requested is not observed; re-evaluate actual suitability. |
| Codex custom role overrides spawn values | Honor role preference and inspect effective settings; never claim spawn arguments prevailed without evidence. |
| Cross-model worker without compatible effort | Resolve supported effort explicitly where possible; otherwise disclose the effective/default limitation. |
| Fast parent or resumed worker receives consequential work | Re-evaluate suitability before assignment or acceptance. |
| Maximum tier | Specific hard problem and existing budget; no extra service, Ultra mode or agent pool implied. |
| Fallback is weaker/unknown | No silent downgrade; consequential approval remains pending until adequacy is established. |
| Metadata unavailable | Observed remains unknown; no agent self-identification or extra probing as proof. |

## Evidence requirements

Run `tests/test_skill_metadata.py` and `tests/test_model_routing.py`, then existing Vibe CI on the final integrated candidate. These are configuration/policy regressions. Preserve all other tests, native plugin validation, Codex installation checks, and required job identities. CI/package checks do not run authenticated end-to-end model routing unless separately recorded.

Perform one consolidated fresh-context independent review of the exact final head and relevant source documentation, since model selection affects consequential review controls. Reuse current CI, inspect preference precedence, aliases, capability gaps, no-downgrade behavior and unchanged quality gates. Permit at most one targeted recheck of required fixes. Record the verdict and evidence on the PR; author self-checks are not independent approval.

A real-host smoke test should observe a pinned-owner session, an ordinary worker and a consequential reviewer using native metadata, including at least one unsupported-control or fallback case. Exercise only available authorized hosts/accounts; do not purchase access or change global settings. Record requested/configured/observed values separately and report unavailable cases as unverified. This is a bounded validation exercise, not overhead on each feature. No speed, cost, token or unchanged defect-detection claim follows from static tests.
