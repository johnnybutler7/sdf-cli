import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    replace_section,
    write_archive,
    write_sentinel_verification_config,
    write_verification_config,
    write_verification_counter,
)
from tests.pr_body_command_helpers import run_handoff


class CloseoutLateArchiveTest(unittest.TestCase):
    def test_close_without_prior_archive_creates_contract_five_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            result = run_handoff(repo, "late-created")
            evidence_path = repo / ".sdf" / "evidence" / "late-created" / "evidence.md"
            evidence = evidence_path.read_text(encoding="utf-8")
            artifact = repo / ".sdf" / "handoffs" / "late-created" / "pr-body.md"
            marker_exists = marker.exists()
            evidence_exists = evidence_path.exists()
            artifact_exists = artifact.exists()

        self.assertEqual(result.exit_code, 1)
        self.assertTrue(marker_exists)
        self.assertTrue(evidence_exists)
        self.assertIn("contract: 5", evidence)
        self.assertIn('change_id: "late-created"', evidence)
        self.assertIn('started_at: "unavailable"', evidence)
        self.assertIn("repository:", evidence)
        self.assertIn("branch:", evidence)
        self.assertIn("closeout check: failed", result.stdout)
        self.assertIn("pr-body write: skipped", result.stdout)
        self.assertIn("Expected first-close stop:", result.stdout)
        self.assertIn(
            "Configured verification passed; evidence completion is still required.",
            result.stdout,
        )
        self.assertIn(
            "This is an expected evidence-completion stop, not a verification failure.",
            result.stdout,
        )
        self.assertIn(
            "Edit `.sdf/evidence/late-created/evidence.md` and complete: "
            "Intent, Review focus, Limits, Guidance applied.",
            result.stdout,
        )
        self.assertIn(
            "sdf close --repo " + str(repo) + " --change-id late-created",
            result.stdout,
        )
        self.assertFalse(artifact_exists)

    def test_late_archive_creation_records_verification_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            result = run_handoff(repo, "late-recorded")
            evidence = (
                repo / ".sdf" / "evidence" / "late-recorded" / "evidence.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 1)
        self.assertIn('closeout_status: "failed"', evidence)
        self.assertIn("verification:", evidence)
        self.assertIn("  total_runs: 1", evidence)
        self.assertIn('name: "would-write-sentinel"', evidence)
        self.assertNotIn("- Configured verification: passed", evidence)
        self.assertNotIn("- Command: not run yet.", evidence)
        self.assertIn("- Unresolved judgement fields:", result.stdout)
        self.assertIn("## Intent: needs judgement", result.stdout)

    def test_failed_verification_on_late_created_archive_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: late-failing-check
    command: python3 -c "import sys; sys.exit(4)"
""",
            )

            result = run_handoff(repo, "late-verification-failed")
            evidence = (
                repo
                / ".sdf"
                / "evidence"
                / "late-verification-failed"
                / "evidence.md"
            ).read_text(encoding="utf-8")
            artifact = (
                repo
                / ".sdf"
                / "handoffs"
                / "late-verification-failed"
                / "pr-body.md"
            )
            artifact_exists = artifact.exists()

        self.assertEqual(result.exit_code, 1)
        self.assertIn("late-failing-check: failed (exit 4)", result.stdout)
        self.assertIn('closeout_status: "failed"', evidence)
        self.assertIn('status: "failed"', evidence)
        self.assertNotIn("- Configured verification: failed", evidence)
        self.assertFalse(artifact_exists)

    def test_rerunning_close_after_judgement_fields_are_completed_writes_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_verification_counter(repo, marker)

            first_result = run_handoff(repo, "late-rerun")
            evidence_path = repo / ".sdf" / "evidence" / "late-rerun" / "evidence.md"
            evidence_path.write_text(
                _populate_judgement_fields(
                    evidence_path.read_text(encoding="utf-8")
                ),
                encoding="utf-8",
            )

            result = run_handoff(repo, "late-rerun")
            evidence = evidence_path.read_text(encoding="utf-8")
            artifact = repo / ".sdf" / "handoffs" / "late-rerun" / "pr-body.md"
            marker_content = marker.read_text(encoding="utf-8")
            artifact_exists = artifact.exists()
            artifact_content = artifact.read_text(encoding="utf-8")

        self.assertEqual(first_result.exit_code, 1)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(marker_content, "2")
        self.assertTrue(artifact_exists)
        self.assertIn("closeout check: passed", result.stdout)
        self.assertIn("pr-body check: ready", result.stdout)
        self.assertIn('closeout_status: "passed"', evidence)
        self.assertIn("  total_runs: 2", evidence)
        self.assertIn("## Review focus", artifact_content)
        self.assertIn("evidence.md#review-focus", artifact_content)

    def test_existing_contract_four_archive_remains_readable_and_closeable(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_archive(repo, "existing-path")
            write_verification_counter(repo, marker)

            result = run_handoff(
                repo,
                "existing-path",
                surface="codex_local",
                model="gpt-5.6",
                reasoning="medium",
                speed="fast",
            )
            evidence = (
                repo / ".sdf" / "evidence" / "existing-path" / "evidence.md"
            ).read_text(encoding="utf-8")
            marker_content = marker.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(marker_content, "1")
        self.assertIn("closeout check: passed", result.stdout)
        self.assertIn("contract: 4", evidence)
        self.assertIn('  surface: "codex_local"', evidence)
        self.assertIn('  model: "gpt-5.6"', evidence)
        self.assertIn('  reasoning: "medium"', evidence)
        self.assertIn('  speed: "fast"', evidence)
        self.assertIn('started_at: "2026-01-01T09:00:00+00:00"', evidence)
        self.assertNotIn('started_at: "unavailable"', evidence)

    def test_existing_contract_four_archive_is_not_rewritten_to_contract_five(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_archive(repo, "existing-contract-four")
            write_verification_counter(repo, marker)

            result = run_handoff(repo, "existing-contract-four")
            evidence = (
                repo / ".sdf" / "evidence" / "existing-contract-four" / "evidence.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("contract: 4", evidence)
        self.assertNotIn("contract: 5", evidence)
        self.assertIn("## Request / Provenance", evidence)

    def test_late_close_does_not_duplicate_verification_within_one_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_verification_counter(repo, marker)

            result = run_handoff(repo, "late-once")
            marker_content = marker.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(marker_content, "1")

    def test_late_created_tiny_archive_is_concise(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            run_handoff(repo, "tiny-change")
            evidence = (
                repo / ".sdf" / "evidence" / "tiny-change" / "evidence.md"
            ).read_text(encoding="utf-8")

        self.assertLess(len(evidence.splitlines()), 60)
        self.assertIn("## Intent", evidence)
        self.assertIn("## Review focus", evidence)
        self.assertIn("## Limits", evidence)
        self.assertIn("## Guidance applied", evidence)
        self.assertNotIn("## Request / Provenance", evidence)
        self.assertNotIn("## Risk / Confidence / Limits", evidence)
        self.assertNotIn("## Handoff / Reviewer Notes", evidence)


def _populate_judgement_fields(markdown: str) -> str:
    content = markdown
    judgement = {
        "## Intent": ["- Exercise late-created contract-5 closeout."],
        "## Review focus": ["- Review the concise judgement gate and machine record."],
        "## Limits": ["- Fixture only; no external service behaviour is covered."],
        "## Guidance applied": ["- None material for this fixture."],
    }
    for heading, lines in judgement.items():
        content = replace_section(content, heading, lines)
    return content


if __name__ == "__main__":
    unittest.main()
