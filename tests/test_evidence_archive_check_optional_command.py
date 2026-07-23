import tempfile
import unittest
from pathlib import Path

from tests.evidence_archive_helpers import write_current_archive

from sdf_cli.evidence_archive_check import (
    check_evidence_archive,
    render_evidence_archive_check,
)
from sdf_cli.evidence_archive_templates import template_for
from sdf_cli.evidence_front_matter import initialize_evidence_machine_record


class EvidenceArchiveCheckOptionalCommandTest(unittest.TestCase):
    def test_invalid_unsafe_change_id_fails_clearly_and_creates_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            result = run_check(repo, "../unsafe")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn("change-id must use only", result.stdout)
            self.assertFalse((repo / ".sdf").exists())

    def test_checker_does_not_create_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            archive = archive_path(repo, "partial")
            archive.mkdir(parents=True)
            (archive / "evidence.md").write_text(
                template_for("evidence.md"),
                encoding="utf-8",
            )
            initialize_evidence_machine_record(
                archive / "evidence.md",
                change_id="partial",
                started_at="2026-01-01T09:00:00+00:00",
            )

            result = run_check(repo, "partial")

            self.assertEqual(result.exit_code, 1)
            self.assertFalse((archive / "verification.md").exists())
            self.assertFalse((archive / "run.md").exists())

    def test_historical_sidecars_are_not_required_or_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "historical-sidecars")
            archive = archive_path(repo, "historical-sidecars")
            (archive / "review.md").write_text("historical\n", encoding="utf-8")
            (archive / "playbooks.md").write_text("# Playbooks\n", encoding="utf-8")

            result = run_check(repo, "historical-sidecars")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("present: evidence.md", result.stdout)
            self.assertNotIn("playbooks.md", result.stdout)
            self.assertNotIn("review.md", result.stdout)

    def test_current_archive_shape_passes_without_legacy_run_file(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "current-shape")

            result = run_check(repo, "current-shape")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("present: evidence.md", result.stdout)
        self.assertNotIn("run.md", result.stdout)


class CommandResult:
    def __init__(self, exit_code: int, stdout: str) -> None:
        self.exit_code = exit_code
        self.stdout = stdout


def run_check(repo: Path, change_id: str) -> CommandResult:
    result = check_evidence_archive(repo=str(repo), change_id=change_id)
    return CommandResult(
        exit_code=result.exit_code,
        stdout=render_evidence_archive_check(result),
    )


def write_archive(
    repo: Path,
    change_id: str,
) -> None:
    write_current_archive(repo, change_id)


def archive_path(repo: Path, change_id: str) -> Path:
    return repo / ".sdf" / "evidence" / change_id


if __name__ == "__main__":
    unittest.main()
