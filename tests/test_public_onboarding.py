import unittest
from pathlib import Path


class PublicOnboardingTest(unittest.TestCase):
    def test_readme_explains_agent_first_operating_model_and_prompts(self):
        readme = self._read("README.md")

        self.assertIn("## Recommended use: let the coding agent run SDF", readme)
        self.assertIn("deterministic", readme)
        self.assertIn("repository-local execution surface", readme)
        self.assertIn("### Prompt for an installation agent", readme)
        self.assertIn("Read this README and install Software Dark Factory", readme)
        self.assertIn("### Prompt for an ordinary governed change", readme)
        self.assertIn("Implement <describe the change>", readme)
        self.assertIn(
            "Humans define repository standards and retain review, approval, and merge",
            readme,
        )

    def test_getting_started_uses_agent_led_path_and_current_installation(self):
        guide = self._read("GETTING-STARTED.md")

        for heading in (
            "## Install and configure SDF with a coding agent",
            "## What the repository owner decides",
            "## What the coding agent executes",
            "## Give the first governed change",
            "## Inspect the result as a human reviewer",
            "## Manual command reference and troubleshooting",
            "## Current support boundary",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, guide)
        self.assertIn("pipx install software-dark-factory", guide)
        self.assertNotIn("not published to PyPI", guide)
        self.assertNotIn("intended post-release installation", guide)

    def _read(self, relative_path: str) -> str:
        root = Path(__file__).resolve().parents[1]
        return (root / relative_path).read_text(encoding="utf-8")
