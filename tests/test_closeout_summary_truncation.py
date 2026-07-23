import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_archive,
    write_verification_config,
)
from tests.pr_body_command_helpers import run_pr_body_write


class CloseoutSummaryTruncationTest(unittest.TestCase):
    def test_short_verification_output_keeps_single_evidence_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "short-verification")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            result = run_pr_body_write(repo, "short-verification")
            output = (
                repo / ".sdf" / "handoffs" / "short-verification" / "pr-body.md"
            ).read_text(encoding="utf-8")

        evidence_line = (
            "- [Evidence notes](.sdf/evidence/short-verification/"
            "evidence.md#verification)"
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(output.count(evidence_line), 1)

    def test_evidence_references_survive_long_run_and_playbook_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(
                repo,
                "long-sections",
                run_context_lines=numbered_lines("Run context", 12),
                branch_lines=numbered_lines("Branch detail", 12),
                playbook_applied_lines=numbered_lines("Applied playbook", 12),
                playbook_consulted_lines=numbered_lines("Consulted playbook", 12),
            )
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            result = run_pr_body_write(repo, "long-sections")
            output = (
                repo / ".sdf" / "handoffs" / "long-sections" / "pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/long-sections/"
            "evidence.md#machine-record)",
            output,
        )
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/long-sections/"
            "evidence.md#guidance-applied)",
            output,
        )
        self.assertNotIn("Run context 12", output)
        self.assertIn("Applied playbook 5", output)
        self.assertNotIn("Applied playbook 6", output)
        self.assertNotIn("Applied playbook 12", output)
        self.assertNotIn("Consulted playbook 1", output)


def numbered_lines(label: str, count: int) -> list[str]:
    return [f"- {label} {index}" for index in range(1, count + 1)]


if __name__ == "__main__":
    unittest.main()
