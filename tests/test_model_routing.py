#!/usr/bin/env python3
"""Native-routing policy/configuration regressions, not live model-call tests."""
from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = "core/CLAUDE.md"
ROUTING = "skills/build/references/model-routing.md"
PARALLEL = "skills/build/references/parallel-work.md"
REVIEW = "skills/build/references/review-loop.md"
VALIDATION = "docs/MODEL-ROUTING-VALIDATION.md"
WORKFLOWS = [f"skills/{name}/SKILL.md" for name in ("build", "discover", "reassess")]
AGENTS = ["agents/worker.md", "agents/reviewer.md"]
CONTROLS = [f"skills/effort-{level}/SKILL.md" for level in ("low", "medium", "high")]
TEMPLATES = ["core/PROJECT-CLAUDE.template.md", "skills/discover/references/project-claude-template.md"]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def metadata(path):
    return yaml.safe_load(read(path).split("---\n", 2)[1])


class ModelRoutingTest(unittest.TestCase):
    def contains(self, path, *terms):
        text = read(path).lower()
        for term in terms:
            with self.subTest(path=path, term=term):
                self.assertIn(term.lower(), text)

    def test_all_tiers_have_task_definitions_not_model_pins(self):
        rows = re.findall(r"^\| (fast|balanced|deep|maximum) \| ([^|]+) \| ([^|]+) \|$",
                          read(ROUTING), re.M)
        self.assertEqual([row[0] for row in rows], ["fast", "balanced", "deep", "maximum"])
        for tier, task, effort in rows:
            self.assertTrue(task.strip(), tier)
            self.assertTrue(effort.strip(), tier)
            self.assertNotRegex(task + effort, r"\b(?:haiku|sonnet|opus|fable|gpt)\b")
        self.contains(ROUTING, "separate from Fast/Standard/Critical", "test scopes",
                      "Effort labels are model-specific")

    def test_core_has_lean_routing_entry_and_quality_floor(self):
        self.contains(CORE, "## Model and effort routing", "references/model-routing.md",
                      "No external model ranking", "per-turn lookup", "classifier agent",
                      "Short answers need no routing call", "never silently downgrade",
                      "Routing never relaxes permissions, testing, independent review or delivery gates")

    def test_preferences_and_main_session_are_preserved(self):
        self.contains(CORE, "Preserve explicit user model/effort preferences in their scope",
                      "Keep the main-session model unless", "without losing context",
                      "Do not rewrite global settings", "Workflow loading must not reset")
        self.contains(ROUTING, "unspecified preference scope", "safe way", "restore prior settings",
                      "Respect scoped pins", "Never rewrite saved global settings")

    def test_workflow_load_cannot_unconditionally_override_preferences(self):
        for path in WORKFLOWS + AGENTS:
            with self.subTest(path=path):
                config = metadata(path)
                self.assertNotIn("model", config)
                self.assertNotIn("effort", config)
        for path in WORKFLOWS:
            self.contains(path, "Loading this workflow does not override the user's model or effort")

    def test_effort_controls_remain_native_and_guarded_before_invocation(self):
        for level, path in zip(("low", "medium", "high"), CONTROLS):
            with self.subTest(path=path):
                config = metadata(path)
                self.assertEqual(config["effort"], level)
                self.assertIs(config["user-invocable"], False)
                self.assertNotIn("model", config)
                self.assertNotIn("context", config)
                self.assertNotIn("allowed-tools", config)
                description = config["description"].lower()
                # The condition must be visible before the body/override loads.
                for term in ("claude-only", "only after", "preferences", "never override", "codex"):
                    self.assertIn(term, description)
        self.contains(ROUTING, "before invoking", "Reading their Markdown is not invoking them",
                      "never invent `effort-maximum`")

    def test_native_model_and_effort_are_both_selected(self):
        self.contains(CORE, "model AND supported effort", "native invocation fields",
                      "prose alone is not enforcement")
        self.contains(ROUTING, "both model and supported effort", "actual schema",
                      "not invented parameter names", "Check role defaults and forced overrides")
        self.contains(PARALLEL, "resolve the assignment's semantic tier", "model and supported effort")

    def test_capability_discovery_is_bounded_and_not_a_new_service(self):
        self.contains(ROUTING, "Discover only when needed", "not every turn",
                      "Do not start another service", "scrape private caches",
                      "acquire credentials", "spawn an agent to discover models",
                      "not a new mandatory register")

    def test_claude_aliases_are_conditional_not_global_tier_bindings(self):
        self.contains(ROUTING, "Claude Code adapter", "family aliases rather than version IDs",
                      "conditional candidates", "not guaranteed", "`best` currently means `opus`",
                      "`default` clears an override", "Future aliases require native capability evidence")
        self.contains(ROUTING, "not full IDs or `inherit`", "forced subagent model",
                      "allowlists can cause substitution", "forks may behave differently")

    def test_codex_discovery_does_not_invent_aliases_or_rank_names(self):
        self.contains(ROUTING, "Codex adapter", "not Claude aliases", "model/list",
                      "nextCursor", "supported/default effort", "isDefault",
                      "do not establish maximum capability", "do not bake it into Vibe defaults",
                      "Without usable discovery")

    def test_codex_main_controls_are_not_assumed_ephemeral(self):
        self.contains(ROUTING, "actually exposes them", "not automatically an agent tool",
                      "`turn/start`", "persist as thread defaults",
                      "`turn/steer` does not switch models", "Do not launch a second app-server")

    def test_codex_role_precedence_and_cross_model_effort_are_explicit(self):
        self.contains(ROUTING, "default_subagent_model", "default_subagent_reasoning_effort",
                      "custom agent file's", "model_reasoning_effort", "override that resolution",
                      "model's default effort, not the parent's", "instead of rewriting their TOML",
                      "Claude skill frontmatter is not a Codex effort control")

    def test_reused_nested_workers_must_qualify_for_new_work(self):
        self.contains(PARALLEL, "reused or nested workers", "actual parent/worker configuration",
                      "an old fast route does not qualify for consequential work")
        self.contains(ROUTING, "Reused/nested workers must qualify", "fast parent's suitability")

    def test_maximum_is_bounded_and_does_not_expand_orchestration(self):
        self.contains(CORE, "specific unusually hard problem", "time/usage budget")
        self.contains(ROUTING, "not automatically the highest numeric effort",
                      "Ultra/Ultracode modes", "more agents or unlimited retries",
                      "Do not reduce testing because a model is stronger")

    def test_observed_settings_are_not_inferred_from_requests(self):
        self.contains(CORE, "requested tier/model/effort", "configured and observed",
                      "not the agent's self-identification", "unobserved remains unknown")
        self.contains(ROUTING, "requested", "configured", "observed", "not observed proof",
                      "Missing observations remain unknown", "never label configuration as observation",
                      "without a hidden serving-model ID")

    def test_fallback_cannot_silently_lower_consequential_quality(self):
        self.contains(ROUTING, "Re-evaluate once", "within budget and demonstrably suitable",
                      "never silently downgrade", "review/approval gate pending",
                      "No repeated fallback loop", "unapproved provider switch")
        self.contains(REVIEW, "approval gate pending, not silently downgraded")
        self.contains("agents/reviewer.md", "collect useful findings without issuing APPROVE")

    def test_no_versioned_model_defaults_or_magic_new_aliases(self):
        for path in [CORE, ROUTING, PARALLEL, REVIEW] + WORKFLOWS + AGENTS + CONTROLS + TEMPLATES:
            with self.subTest(path=path):
                self.assertNotRegex(read(path), r"(?i)\b(?:gpt-\d|claude-(?:\d|(?:opus|sonnet|haiku|fable)-\d))")
        for path in WORKFLOWS + AGENTS + CONTROLS:
            self.assertNotIn("model", metadata(path))

    def test_project_templates_match_and_use_new_policy(self):
        self.assertEqual(read(TEMPLATES[0]), read(TEMPLATES[1]))
        self.contains(TEMPLATES[0], "fast/balanced/deep/maximum", "Preserve scoped user preferences",
                      "Consequential approval stays pending", "global settings changes")

    def test_existing_testing_permissions_and_bounded_review_are_retained(self):
        self.contains(CORE, "Routine feature deployments", "Formal production release/promotion",
                      "Never force-push", "Merge permission does not imply deployment permission",
                      "Never manufacture verification")
        self.contains(REVIEW, "one full review and one targeted recheck", "never edits",
                      "exact full HEAD SHA", "No independent reviewer by default")
        reviewer = metadata("agents/reviewer.md")
        self.assertEqual(reviewer["tools"], "Read, Grep, Glob, Bash")
        self.contains("agents/reviewer.md", "Never edit source", "Never approve an unresolved acceptance failure")

    def test_reference_is_on_demand_and_has_official_sources(self):
        header = read(ROUTING).split("## Tiers", 1)[0]
        for term in ("Purpose:", "Read when:", "Skip when:", "Sections:"):
            self.assertIn(term, header)
        for url in ("https://code.claude.com/docs/en/model-config",
                    "https://code.claude.com/docs/en/sub-agents",
                    "https://code.claude.com/docs/en/skills",
                    "https://developers.openai.com/codex/app-server",
                    "https://developers.openai.com/codex/subagents"):
            self.assertIn(url, read(ROUTING))
        self.contains(ROUTING, "not an interception layer", "do not prove live routing")

    def test_validation_does_not_claim_static_tests_prove_runtime(self):
        self.contains(VALIDATION, "policy regressions", "do not run authenticated",
                      "fresh-context independent review", "exact final head",
                      "requested/configured/observed", "unverified", "not overhead on each feature",
                      "unmerged and unpublished", "merging would deliver",
                      "not permission to ship changed behavior under the released version")


if __name__ == "__main__":
    unittest.main()
