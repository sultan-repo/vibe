# Capability-based model routing

**Purpose:** fit model and reasoning effort to the assignment without changing Vibe's quality bar.
**Read when:** first delegated assignment, nontrivial override, or routing diagnosis; reuse it afterward.
**Skip when:** a short answer, unchanged configuration, or ordinary work needs no override.
**Sections:** tiers; dispatch; Claude Code; Codex; evidence/fallback; official sources.

## Tiers describe work, not product names

| Tier | Need | Effort intent |
| --- | --- | --- |
| fast | Bounded mechanical work with clear checks | Least reasoning sufficient for this task |
| balanced | Ordinary implementation or exploration | Normal coding/problem-solving capacity |
| deep | Difficult debugging, architecture, consequential invariants or review | Sustained reasoning appropriate to this model |
| maximum | A specific unusually hard problem that justifies extra usage | Highest useful supported capacity within the existing time/usage budget |

These are Vibe semantics, not literal host arguments or universal model rankings. They are separate from Fast/Standard/Critical workflows and affected/expanded/release test scopes. Effort labels are model-specific: low on one model need not mean less capability than high on another. Maximum is not automatically the highest numeric effort or an entitlement to new paid features, Ultra/Ultracode modes, more agents or unlimited retries. Do not reduce testing because a model is stronger.

## Dispatch contract

1. During existing planning, establish the assignment's tier, tools, input modalities/context needs, risk and budget. Preserve explicit user preferences in their scope, including role-specific models/effort, provider/privacy constraints and host restrictions. An unspecified preference scope is not permission to override it. Keep the main-session model by default; any switch needs an authorized, exposed native control with known persistence and a safe way to preserve context and restore prior settings. Never rewrite saved global settings.
2. Resolve from the active host's existing configuration, tool schema, native catalog/aliases and applicable owner mappings. Use official host guidance when capability meaning is unclear; no external leaderboard, version-number comparison or name-based guess. Discover only when needed and retain the small session mapping. Refresh after a relevant host/model/provider/configuration change, rejection or fallback, not every turn. Do not start another service, scrape private caches, acquire credentials or spawn an agent to discover models.
3. For each useful subagent assignment, resolve **both model and supported effort** before dispatch. Prefer the least costly suitable allowed configuration, not the smallest model regardless of risk. Respect scoped pins even when native precedence would let Vibe override them. Pass explicit native invocation fields where exposed and compatible with those preferences; use the actual schema, not invented parameter names. Check role defaults and forced overrides first. A prose brief alone does not set runtime controls. If a preferred pin is unsuitable, preserve it, report the consequential limitation and seek a material decision rather than bypassing it.
4. Reuse this decision until the assignment or capability context changes. Reused/nested workers must qualify for their new work; do not inherit a fast parent's suitability for a deep review. Keep the compact route in the existing brief/evidence when useful, not a new mandatory register. Do not spawn a worker solely to change model or effort.

## Claude Code adapter

Use available family aliases rather than version IDs. Current host guidance offers `haiku` for simple work, `sonnet` for everyday coding, `opus` for complex reasoning and `fable` for the hardest work. These are conditional candidates, not guaranteed account/provider availability or permanent tier bindings. `best` currently means `opus`; `default` clears an override, not a balanced-tier selection. Future aliases require native capability evidence, not a Vibe release or an assumed name ranking. [1]

The Agent tool's `model` argument accepts supported family aliases, not full IDs or `inherit`. Agent frontmatter and environment settings have different precedence; a forced subagent model can remove invocation choice, and allowlists can cause substitution. Preserve owner defaults rather than overriding them just because a tool permits it. Use per-invocation `effort` only when the exposed schema supports it; cross-model defaults and forks may behave differently. Inspect available metadata/warnings for a substitution. [2]

Vibe's workflow and agent definitions omit fixed model/effort frontmatter to preserve native user defaults. The existing internal `effort-low`, `effort-medium` and `effort-high` skills are Claude-only controls: check support and preference scope **before invoking**. Their effort metadata affects the current turn and can override a session choice; their instruction bodies cannot undo that pre-load override. Reading their Markdown is not invoking them. Use native controls for other supported effort levels only when exposed; never invent `effort-maximum`. [3]

## Codex adapter

Use the current native catalog or host-provided model metadata, not Claude aliases or Vibe-invented model aliases. An already exposed app-server `model/list` supplies model IDs and supported/default effort metadata; follow `nextCursor` as needed before claiming a model is unavailable. Respect provider/account availability, visibility and input capabilities. `isDefault`, catalog order and model names do not establish maximum capability. A model ID returned by this runtime may be used in that session; do not bake it into Vibe defaults. Without usable discovery, preserve a known-suitable current configuration rather than guessing.

Only use app-server controls when the connected host actually exposes them. A documented API or UI `/model` command is not automatically an agent tool. `turn/start` model/effort overrides persist as thread defaults; they are not an automatically restored one-turn switch. `turn/steer` does not switch models. Do not launch a second app-server just to route. [4]

For native workers, inspect the effective role configuration. Spawn values, `[agents].default_subagent_model` / `default_subagent_reasoning_effort`, and parent inheritance participate in resolution. A custom agent file's `model` or `model_reasoning_effort` can override that resolution. Changing model without effort may select that model's default effort, not the parent's. Pass a compatible model/effort pair through exposed native fields; honor existing role pins instead of rewriting their TOML. If independent controls are unavailable, use an adequate existing role/current configuration or disclose the limitation. Claude skill frontmatter is not a Codex effort control. [5]

## Evidence and fallback

Keep three concepts separate: **requested** tier/model/effort; **configured** effective native settings after known precedence; **observed** runtime model/effort from available native events or metadata. A requested alias, successful tool call, passing task or agent self-identification is not observed proof. Missing observations remain unknown; do not add polling or diagnostic model calls merely to fill fields. Adequacy may be established from trustworthy native configuration and documented capabilities without a hidden serving-model ID; disclose that observation limit, and never label configuration as observation.

On a rejection, cap, fallback or material mismatch, stop relying on the original route. Re-evaluate once using already available capabilities. Use an alternative only when allowed, within budget and demonstrably suitable; never silently downgrade. Otherwise preserve a suitable current configuration, narrow independent work, or report the blocker. If suitability for consequential work cannot be established, leave its required review/approval gate pending. Useful findings can continue but cannot become an approval by renaming the tier. No repeated fallback loop, unapproved provider switch, relaxed checks or broader permissions.

This is a policy for using native controls, not an interception layer that can force an unavailable host feature. Static policy tests and package validation do not prove live routing adherence or savings.

## Official sources

Verified 2026-11-15. Installed host schemas, account restrictions and runtime evidence govern actual availability; recheck these sources on a material capability change, not per task.

1. [Claude model configuration](https://code.claude.com/docs/en/model-config)
2. [Claude subagent model and effort controls](https://code.claude.com/docs/en/sub-agents)
3. [Claude skill frontmatter](https://code.claude.com/docs/en/skills)
4. [Codex app-server model discovery and turn controls](https://developers.openai.com/codex/app-server)
5. [Codex subagent configuration and inheritance](https://developers.openai.com/codex/subagents)
