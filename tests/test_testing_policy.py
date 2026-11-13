#!/usr/bin/env python3
"""Static policy regressions, not a simulation of Claude or application coverage."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = "core/CLAUDE.md"
BUILD = "skills/build/SKILL.md"
REASSESS = "skills/reassess/SKILL.md"
DISCOVER = "skills/discover/SKILL.md"
POLICY = "skills/build/references/testing-policy.md"
REVIEW = "skills/build/references/review-loop.md"
PARALLEL = "skills/build/references/parallel-work.md"
CACHE = "hooks/verification-cache.md"
TEMPLATES = ("core/PROJECT-CLAUDE.template.md",
             "skills/discover/references/project-claude-template.md")


def read(path):
    return (ROOT / path).read_text(encoding="utf-8").lower()


class TestingPolicyTest(unittest.TestCase):
    def assert_terms(self, path, *terms):
        text = read(path)
        for term in terms:
            with self.subTest(path=path, term=term):
                self.assertIn(term.lower(), text)

    def test_three_scopes_are_reachable_from_each_workflow(self):
        for path in (CORE, BUILD, REASSESS, POLICY, *TEMPLATES):
            self.assert_terms(path, "affected", "expanded", "release")
        for path in (CORE, BUILD, REASSESS, DISCOVER, PARALLEL, REVIEW):
            self.assert_terms(path, "testing-policy.md")

    def test_feature_completion_does_not_reset_coverage_to_full(self):
        self.assert_terms(CORE, "not an automatic full-suite trigger")
        self.assert_terms(BUILD, "feature completion alone does not trigger full e2e")
        self.assert_terms(REASSESS, "a milestone label alone does not require full e2e")
        self.assert_terms(PARALLEL, "feature completion alone does not require full e2e")
        obsolete = (
            "at a major milestone:** integrate the work and run the project's full",
            "at major milestone completion, require the full relevant checks",
            "full end-to-end coverage belongs at the milestone",
            "full milestone gate:",
            "the major milestone where full e2e is due",
            "run the full integrated gate once at the agreed major milestone",
        )
        for path in (CORE, BUILD, REASSESS, DISCOVER, PARALLEL, REVIEW, *TEMPLATES):
            for rule in obsolete:
                with self.subTest(path=path, rule=rule):
                    self.assertNotIn(rule, read(path))

    def test_small_feature_deployments_do_not_require_full_e2e(self):
        for path in (CORE, BUILD, REASSESS, POLICY, *TEMPLATES):
            self.assert_terms(path, "routine feature deployment", "auto-deploying",
                              "affected", "expanded")
        self.assert_terms(POLICY, "automatic deployment from `main`",
                          "feature-scoped browser", "smoke", "rollback")
        for path in (CORE, BUILD, REASSESS, POLICY):
            self.assertNotIn("before any production release/deployment", read(path))

    def test_full_e2e_requires_explicit_owner_request_or_formal_release(self):
        for path in (CORE, BUILD, REASSESS, POLICY):
            self.assert_terms(path, "formal production release", "full relevant", "e2e")
        self.assert_terms(CORE, "explicitly requested by the owner")
        self.assert_terms(BUILD, "owner requests it")
        self.assert_terms(POLICY, "full journey e2e", "explicit owner requests",
                          "explicit project hooks/ci", "cannot be bounded")
        for path in TEMPLATES:
            self.assert_terms(path, "formal production release", "full relevant", "e2e")


    def test_impact_uses_cumulative_changes_and_a_real_base(self):
        self.assert_terms(POLICY, "current integration base", "cumulative changes",
                          "not just the latest commit", "staged", "unstaged",
                          "untracked", "renames/deletions", "target branch",
                          "base is missing or stale")
        for path in (CORE, BUILD, REASSESS, PARALLEL):
            self.assert_terms(path, "cumulative")

    def test_shared_consumers_and_selector_limits_are_explicit(self):
        self.assert_terms(POLICY, "consumers", "api contracts", "global styling",
                          "dependencies/lockfiles", "background jobs",
                          "different filenames or directories do not prove isolation",
                          "selector is a heuristic, not sole proof of coverage")

    def test_ui_acceptance_keeps_observed_journeys(self):
        for path in (BUILD, POLICY):
            self.assert_terms(path, "failure/recovery", "affected devices",
                              "a unit pass alone is not ui acceptance")
        self.assert_terms(POLICY, "feature-scoped browser evidence", "unavailable environment",
                          "mobile-specific")

    def test_empty_selection_and_missing_acceptance_do_not_pass(self):
        for path in (CORE, BUILD, REASSESS):
            self.assert_terms(path, "zero selected tests", "changed behavior")
        self.assert_terms(POLICY, "zero executed tests", "add relevant coverage or expand",
                          "do not use a zero-test-success option",
                          "full green suite also cannot prove an uncovered new requirement")
        self.assert_terms(CACHE, "adapter must reject an empty selection")

    def test_uncertainty_and_failures_expand_instead_of_disappearing(self):
        for path in (CORE, BUILD, POLICY, *TEMPLATES):
            self.assert_terms(path, "full relevant checks when impact cannot be bounded")
        self.assert_terms(POLICY, "unexpected failure triggers diagnosis",
                          "do not retry a full suite blindly", "weaken a gate",
                          "fixed defect needs regression evidence")

    def test_high_risk_invariants_and_bounded_review_survive(self):
        self.assert_terms(POLICY, "critical invariants before merge",
                          "authentication", "authorization", "consent", "personal data",
                          "privacy/deletion", "payments", "migrations",
                          "delivery controls", "consequential concurrency")
        self.assert_terms(REVIEW, "one full review and one targeted recheck",
                          "fresh-context", "required security/data failures still block",
                          "exact full head sha")
        self.assert_terms(REASSESS, "one full review", "one targeted follow-up",
                          "never approve high-risk delivery with required findings unresolved")

    def test_project_gates_need_authorized_validated_adoption(self):
        self.assert_terms(POLICY, "project rules, hooks, required ci",
                          "does not authorize disabling or rewriting them",
                          "preserve the old gate until the replacement is validated")
        self.assert_terms(CORE, "never silently override a higher level")
        self.assert_terms(CACHE, "upgrading vibe alone does not migrate project hooks")

    def test_evidence_scope_cannot_be_widened_by_a_cache_hit(self):
        self.assert_terms(POLICY, "subset does not certify a superset",
                          "cumulative selection base", "selected tests/filters",
                          "test-map/adapter version", "browser/device projects",
                          "dependencies", "configuration", "fixtures", "environment")
        self.assert_terms(CACHE, "do not reuse a marker across different selection scopes",
                          "never relabel a subset as full",
                          "if scope cannot be represented safely, do not cache")

    def test_cache_modes_and_failure_invalidation_remain_compatible(self):
        self.assert_terms(POLICY, "modes remain **quick/full**",
                          "full and quick records separately",
                          "failed or interrupted rerun invalidates prior evidence",
                          "required ci is not bypassed", "exact-head review approval")
        self.assert_terms(CACHE, "--full-includes-quick", "keep each mode's successful evidence",
                          "failed or interrupted run invalidates prior evidence",
                          "malformed records miss the cache")
        for path in (POLICY, CACHE):
            self.assertNotRegex(read(path), r"--mode\s+(affected|expanded|release)\b")

    def test_no_new_per_turn_or_agent_overhead(self):
        self.assert_terms(CORE, "during existing planning", "no extra agent, per-turn scan",
                          "keep cheap broad checks")
        self.assert_terms(POLICY, "not another agent, scheduler or mandatory register",
                          "not on unchanged conversation turns",
                          "not a new dual-run requirement for every feature")

    def test_templates_are_identical_and_preserve_continuity(self):
        self.assertEqual(read(TEMPLATES[0]), read(TEMPLATES[1]))
        for path in TEMPLATES:
            self.assert_terms(path, "full release gate", "zero selected tests",
                              "full evidence separate", "ten-line now summary",
                              "startup automatically loads docs/status.md's now block")

    def test_parallel_integration_does_not_inherit_worker_local_passes(self):
        self.assert_terms(PARALLEL, "current target-branch base",
                          "worker-local passes do not prove the combined result",
                          "lower branches must not deploy independently",
                          "integration changes invalidate the affected evidence")

    def test_feature_verdict_is_not_release_readiness(self):
        self.assert_terms(CORE, "feature acceptance is not release readiness")
        self.assert_terms(REASSESS, "full release e2e remains pending",
                          "do not call the release verified until its full evidence exists")
        self.assert_terms(POLICY, "passed, failed, skipped, pending and unavailable")

    def test_adoption_requires_runtime_comparison_without_quality_claims(self):
        self.assert_terms(POLICY, "bounded shadow comparison", "same candidates and environment",
                          "replay known regressions", "every omitted failure",
                          "not a guarantee of future quality", "keep expanded/full checks",
                          "elapsed time and duplicate runs")
        self.assert_terms("docs/TESTING-VALIDATION.md", "static policy regression tests",
                          "not proof of an agent's runtime decisions",
                          "no automatic project migration or measured speedup is claimed")

    def test_readme_stays_simple_but_explains_the_boundary(self):
        self.assert_terms("README.md", "focused tests for changed features",
                          "full verification before formal production releases",
                          "existing project test requirements still apply",
                          "skills/build/references/testing-policy.md")
        self.assertLess(len(read("README.md").split()), 700)


if __name__ == "__main__":
    unittest.main()
