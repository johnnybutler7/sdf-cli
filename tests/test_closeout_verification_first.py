import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    replace_section,
    write_archive,
    write_sentinel_verification_config,
    write_verification_config,
)
from tests.pr_body_command_helpers import run_handoff


class CloseoutVerificationFirstTest(unittest.TestCase):
    def test_closeout_runs_verification_before_readiness_assessment(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_archive(
                repo,
                "unresolved-judgement",
                change_summary_lines=["- Change summary: TBD."],
            )
            write_sentinel_verification_config(repo, marker)

            result = run_handoff(repo, "unresolved-judgement")
            marker_content = marker.read_text(encoding="utf-8")
            evidence = (
                repo / ".sdf" / "evidence" / "unresolved-judgement" / "evidence.md"
            ).read_text(encoding="utf-8")
            artifact = (
                repo / ".sdf" / "handoffs" / "unresolved-judgement" / "pr-body.md"
            )

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(marker_content, "ran")
        self.assertIn('name: "would-write-sentinel"', evidence)
        self.assertIn('closeout_status: "failed"', evidence)
        self.assertIn("Remaining readiness problems:", result.stdout)
        self.assertIn("- Unresolved judgement fields:", result.stdout)
        self.assertIn(
            "evidence.md ## Change Summary: - Change summary: TBD.",
            result.stdout,
        )
        self.assertIn("- Verification failure:\n  none", result.stdout)
        self.assertFalse(artifact.exists())

    def test_verification_placeholder_is_replaced_before_final_readiness(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "verification-placeholder")
            evidence_path = (
                repo
                / ".sdf"
                / "evidence"
                / "verification-placeholder"
                / "evidence.md"
            )
            evidence_path.write_text(
                replace_section(
                    evidence_path.read_text(encoding="utf-8"),
                    "### Commands",
                    [
                        "<!-- sdf:verification-summary:start -->",
                        "- Command: not run yet.",
                        "  - Status: not run yet.",
                        "<!-- sdf:verification-summary:end -->",
                    ],
                ),
                encoding="utf-8",
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

            result = run_handoff(repo, "verification-placeholder")
            evidence = evidence_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("closeout check: passed", result.stdout)
        self.assertNotIn("- Command: not run yet.", evidence)
        self.assertIn("- Configured verification: passed", evidence)
        self.assertIn('closeout_status: "passed"', evidence)

    def test_failed_verification_is_recorded_and_blocks_closeout(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "verification-failed")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: failing-check
    command: python3 -c "import sys; sys.exit(7)"
""",
            )

            result = run_handoff(repo, "verification-failed")
            evidence = (
                repo / ".sdf" / "evidence" / "verification-failed" / "evidence.md"
            ).read_text(encoding="utf-8")
            artifact = (
                repo / ".sdf" / "handoffs" / "verification-failed" / "pr-body.md"
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("closeout check: failed", result.stdout)
        self.assertIn("- Verification failure:", result.stdout)
        self.assertIn("failing-check: failed (exit 7)", result.stdout)
        self.assertIn('closeout_status: "failed"', evidence)
        self.assertIn('status: "failed"', evidence)
        self.assertNotIn('closeout_status: "passed"', evidence)
        self.assertFalse(artifact.exists())

    def test_genuine_verification_failure_is_not_an_expected_completion_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                '''
version: 1
commands:
  - name: failing-check
    command: python3 -c "import sys; sys.exit(7)"
''',
            )

            result = run_handoff(repo, "genuine-failure")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("- Verification failure:", result.stdout)
        self.assertIn("failing-check: failed (exit 7)", result.stdout)
        self.assertIn("- Fix closeout failures first, then rerun:", result.stdout)
        self.assertNotIn("Expected first-close stop:", result.stdout)

    def test_unrecordable_evidence_remains_a_genuine_closeout_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence = repo / ".sdf" / "evidence" / "unrecordable" / "evidence.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("# Evidence\n", encoding="utf-8")
            write_verification_config(
                repo,
                '''
version: 1
commands:
  - name: would-pass
    command: python3 -c "print('ok')"
''',
            )

            result = run_handoff(repo, "unrecordable")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Full verification: skipped", result.stdout)
        self.assertIn("evidence archive is not recordable", result.stdout)
        self.assertIn("- Fix closeout failures first, then rerun:", result.stdout)
        self.assertNotIn("Expected first-close stop:", result.stdout)


if __name__ == "__main__":
    unittest.main()
