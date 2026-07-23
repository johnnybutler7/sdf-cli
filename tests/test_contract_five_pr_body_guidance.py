import tempfile
import unittest
from pathlib import Path

from tests.contract_five_pr_body_fixtures import (
    known_context,
    write_contract_five_archive,
    write_passing_verification,
)
from tests.pr_body_command_helpers import run_pr_body_write


class ContractFivePrBodyGuidanceTest(unittest.TestCase):
    def test_projects_material_guidance_before_the_evidence_link(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(
                repo,
                "material-guidance",
                guidance=["- Renderer guidance kept the summary compact."],
                declared=known_context(),
            )
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "material-guidance")
            content = (
                repo / ".sdf/handoffs/material-guidance/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        summary = "- Renderer guidance kept the summary compact."
        evidence_link = (
            "- [Evidence notes](.sdf/evidence/material-guidance/"
            "evidence.md#guidance-applied)"
        )
        self.assertIn(summary, content)
        self.assertIn(evidence_link, content)
        self.assertLess(content.index(summary), content.index(evidence_link))

    def test_falls_back_when_no_material_guidance_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(
                repo,
                "no-material-guidance",
                guidance=["- None material."],
                declared=known_context(),
            )
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "no-material-guidance")
            content = (
                repo / ".sdf/handoffs/no-material-guidance/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("- No material guidance was recorded.", content)
        self.assertNotIn("- None material.", content)
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/no-material-guidance/"
            "evidence.md#guidance-applied)",
            content,
        )


if __name__ == "__main__":
    unittest.main()
