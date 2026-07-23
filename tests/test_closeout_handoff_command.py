import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.closeout_summary_fixtures import (
    write_archive,
    write_sentinel_verification_config,
    write_verification_config,
    write_verification_counter,
)
from tests.pr_body_command_helpers import run_handoff

SUCCESSFUL_CLOSE_COMPLETION_MARKER = (
    "SDF close complete: verification passed, evidence recorded, and local "
    "handoff checked."
)


class CloseoutHandoffCommandTest(unittest.TestCase):
    def test_success_writes_checks_and_runs_closeout_once(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_archive(repo, "handoff-success")
            write_verification_counter(repo, marker)

            result = run_handoff(repo, "handoff-success")
            artifact = repo / ".sdf" / "handoffs" / "handoff-success" / "pr-body.md"
            content = artifact.read_text(encoding="utf-8")
            marker_content = marker.read_text(encoding="utf-8")
            evidence = (
                repo / ".sdf" / "evidence" / "handoff-success" / "evidence.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("SDF close", result.stdout)
        self.assertIn("closeout check: passed", result.stdout)
        self.assertIn(
            "pr-body write: written (.sdf/handoffs/handoff-success/pr-body.md)",
            result.stdout,
        )
        self.assertIn("pr-body check: ready", result.stdout)
        self.assertIn("github: not mutated", result.stdout)
        self.assertIn(
            "next: commit the change and evidence, then run sdf close",
            result.stdout,
        )
        self.assertTrue(result.stdout.rstrip().endswith(SUCCESSFUL_CLOSE_COMPLETION_MARKER))
        self.assertEqual(marker_content, "1")
        self.assertIn('closeout_status: "passed"', evidence)
        self.assertRegex(evidence, r'closed_at: "[^\n]+"')
        self.assertIn('name: "count-verification"', evidence)
        self.assertIn(
            "[Evidence notes](.sdf/evidence/handoff-success/"
            "evidence.md#acceptance--review-focus)",
            content,
        )

    def test_closeout_failure_skips_write_and_check(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            result = run_handoff(repo, "missing-archive")
            artifact = repo / ".sdf" / "handoffs" / "missing-archive" / "pr-body.md"
            record = (
                repo
                / ".sdf"
                / "evidence"
                / "missing-archive"
                / "closeout-result.yml"
            )
            marker_exists = marker.exists()

        self.assertEqual(result.exit_code, 1)
        self.assertIn("closeout check: failed", result.stdout)
        self.assertIn(
            "closeout result record: written "
            "(.sdf/evidence/missing-archive/evidence.md machine record)",
            result.stdout,
        )
        self.assertIn("pr-body write: skipped", result.stdout)
        self.assertIn("pr-body check: skipped", result.stdout)
        self.assertIn("github: not mutated", result.stdout)
        self.assertIn("SDF close summary", result.stdout)
        self.assertIn("- Full verification: passed (1 checks run)", result.stdout)
        self.assertNotIn(SUCCESSFUL_CLOSE_COMPLETION_MARKER, result.stdout)
        self.assertFalse(artifact.exists())
        self.assertFalse(record.exists())
        self.assertTrue(marker_exists)

    def test_existing_artifact_is_checked_but_not_regenerated(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_archive(
                repo,
                "handoff-existing",
                change_summary_lines=["- Original summary."],
            )
            write_verification_counter(repo, marker)
            artifact = repo / ".sdf" / "handoffs" / "handoff-existing" / "pr-body.md"

            first_result = run_handoff(repo, "handoff-existing")
            original_content = artifact.read_text(encoding="utf-8")
            evidence = (
                repo / ".sdf" / "evidence" / "handoff-existing" / "evidence.md"
            )
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    "- Original summary.",
                    "- Updated evidence summary.",
                ),
                encoding="utf-8",
            )

            result = run_handoff(repo, "handoff-existing")
            content = artifact.read_text(encoding="utf-8")
            marker_content = marker.read_text(encoding="utf-8")

        self.assertEqual(first_result.exit_code, 0)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("closeout check: passed", result.stdout)
        self.assertIn(
            "pr-body write: existing not regenerated "
            "(.sdf/handoffs/handoff-existing/pr-body.md)",
            result.stdout,
        )
        self.assertIn("pr-body check: ready", result.stdout)
        self.assertIn(
            "after evidence-only wording edits: commit the implementation and "
            "final evidence, then run",
            result.stdout,
        )
        self.assertIn("--refresh-handoff", result.stdout)
        self.assertIn(
            "recorded passing verification without rerunning the configured boundary",
            result.stdout,
        )
        self.assertNotIn("--overwrite", result.stdout)
        self.assertEqual(content, original_content)
        self.assertIn("- Original summary.", content)
        self.assertNotIn("- Updated evidence summary.", content)
        self.assertEqual(marker_content, "2")

    def test_malformed_existing_artifact_is_checked_and_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_archive(repo, "handoff-existing-invalid")
            write_verification_counter(repo, marker)
            artifact = (
                repo
                / ".sdf"
                / "handoffs"
                / "handoff-existing-invalid"
                / "pr-body.md"
            )
            artifact.parent.mkdir(parents=True)
            artifact.write_text("existing\n", encoding="utf-8")

            result = run_handoff(repo, "handoff-existing-invalid")
            content = artifact.read_text(encoding="utf-8")
            marker_content = marker.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("closeout check: passed", result.stdout)
        self.assertIn(
            "pr-body write: existing not regenerated "
            "(.sdf/handoffs/handoff-existing-invalid/pr-body.md)",
            result.stdout,
        )
        self.assertIn("pr-body check: failed", result.stdout)
        self.assertIn("missing section: # What you are reviewing", result.stdout)
        self.assertNotIn(SUCCESSFUL_CLOSE_COMPLETION_MARKER, result.stdout)
        self.assertEqual(content, "existing\n")
        self.assertEqual(marker_content, "1")

    def test_overwrite_replaces_existing_artifact_after_closeout_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "handoff-overwrite")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            artifact = repo / ".sdf" / "handoffs" / "handoff-overwrite" / "pr-body.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("existing\n", encoding="utf-8")

            result = run_handoff(repo, "handoff-overwrite", overwrite=True)
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "pr-body write: overwritten (.sdf/handoffs/handoff-overwrite/pr-body.md)",
            result.stdout,
        )
        self.assertTrue(content.startswith("# What you are reviewing\n"))

    def test_handoff_does_not_use_finalizer_or_github_mutation_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "handoff-no-mutation")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )

            with patch(
                "sdf_cli.commands.finalize_merged.finalize_merged_pr_body"
            ) as finalize:
                result = run_handoff(repo, "handoff-no-mutation")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("github: not mutated", result.stdout)
        finalize.assert_not_called()

if __name__ == "__main__":
    unittest.main()
