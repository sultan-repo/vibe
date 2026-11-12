"""Static reuse-policy contracts, not evidence of model choices or speed gains."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = "core/CLAUDE.md"
BUILD = "skills/build/SKILL.md"
POLICY = "skills/build/references/reuse-policy.md"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ReusePolicyTest(unittest.TestCase):
    def terms(self, path, *terms):
        text = read(path).lower()
        for term in terms:
            with self.subTest(path=path, term=term):
                self.assertIn(term.lower(), text)

    def test_core_and_build_load_reference_only_for_relevant_choices(self):
        for path in (CORE, BUILD):
            self.terms(path, "references/reuse-policy.md", "substantial", "existing", "low-risk")
        section = read(CORE).split("## Reuse before rebuilding\n", 1)[1].split("\n## ", 1)[0]
        self.assertLess(len(section.split()), 115)
        self.terms(BUILD, "not turn this into mandatory browsing for every edit")

    def test_existing_capabilities_precede_external_search(self):
        self.terms(POLICY, "Start inside the project", "installed packages", "framework/platform",
                   "before searching outside", "competing UI kit", "Installed does not mean safe")

    def test_custom_work_and_existing_product_rules_remain_valid(self):
        self.terms(POLICY, "trivial low-risk helper", "product-specific rules explicit",
                   "Do not replace working code", "approved scope", "custom implementation is a valid outcome",
                   "not improvised cryptography or authentication")

    def test_research_is_bounded_current_and_source_verified(self):
        self.terms(POLICY, "current official documentation", "package registry", "security advisories",
                   "exact package identity", "compatible version", "two or three", "Stop when",
                   "untrusted data", "never private source", "online verification is unavailable",
                   "do not silently add an unverified dependency")

    def test_quality_and_lifecycle_cost_not_code_count(self):
        self.terms(POLICY, "future maintenance effort", "not generated line count", "transitive dependencies",
                   "quiet mature software", "not proof of security", "License", "attribution",
                   "accessibility", "Arabic/RTL", "bundle/runtime", "server-rendering",
                   "Backend", "failure recovery", "concurrency", "operating costs")

    def test_source_ownership_and_permission_boundaries(self):
        self.terms(POLICY, "copied/generated component source", "origin/version", "security updates",
                   "existing project permissions", "Paid services", "external data sharing",
                   "license exceptions", "owner approval", "privileged or production environment")

    def test_integration_keeps_existing_quality_and_release_gates(self):
        self.terms(POLICY, "hardest representative requirement", "synthetic data", "not mandatory ceremony",
                   "lockfile/reproducibility", "avoid unrelated upgrades", "focused acceptance",
                   "affected/expanded/release", "full production verification remains intact",
                   "Broaden when", "Do not retest an entire upstream library")

    def test_no_new_ceremony_or_unsupported_savings_claim(self):
        self.terms(POLICY, "not a command, startup scan, mandatory research agent",
                   "separate dependency register", "few lines", "coordinator shares",
                   "No measured time, token or quality improvement", "Do not add a benchmark to every feature")
        self.assertLess(len(read(POLICY).split()), 1150)
        self.assertLess(len(read("README.md").split()), 700)
        self.terms("README.md", "Reuse before rebuilding", "references/reuse-policy.md")

    def test_workflows_stay_model_invocable_without_new_command(self):
        self.terms(BUILD, "user-invocable: false", "No slash command is required")
        self.assertNotIn("disable-model-invocation: true", read(BUILD))
        self.assertFalse((ROOT / "skills/reuse/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
