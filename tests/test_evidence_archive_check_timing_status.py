import tempfile
import unittest
from pathlib import Path

from tests.evidence_archive_helpers import replace_section, write_current_archive

from sdf_cli.evidence_archive_check import (
    check_evidence_archive,
    render_evidence_archive_check,
)


class EvidenceArchiveCheckTimingStatusTest(unittest.TestCase):
    def test_command_without_per_command_status_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "missing-per-command-status")
            write_embedded_commands(
                repo,
                "missing-per-command-status",
                [
                        "- `PYTHONPATH=src python3 -m unittest discover -s tests`",
                        "- `python3 -m ruff check src tests`",
                        "- Timing: 3.21s overall.",
                ],
            )

            result = run_check(repo, "missing-per-command-status")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn(
                "missing verification status in evidence.md: "
                "command 1 missing Status:",
                result.stdout,
            )
            self.assertIn(
                "missing verification status in evidence.md: "
                "command 2 missing Status:",
                result.stdout,
            )

    def test_command_allows_status_without_timing_when_timing_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "timing-unavailable")
            write_embedded_commands(
                repo,
                "timing-unavailable",
                [
                        "- Command: `python3 -m ruff check src tests`",
                        "  - Status: passed.",
                ],
            )

            result = run_check(repo, "timing-unavailable")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("status: ready", result.stdout)

    def test_command_preserves_recorded_timing_when_available(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "timing-recorded")
            write_embedded_commands(
                repo,
                "timing-recorded",
                [
                        "- Command: `sdf closeout check --repo . "
                        "--change-id timing-recorded`",
                        "  - Status: passed.",
                        "  - Timing: 12.34s total.",
                        "  - Tracked timings:",
                        "    - python-unit-tests: 8.12s.",
                ],
            )

            result = run_check(repo, "timing-recorded")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("status: ready", result.stdout)

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


def write_archive(repo: Path, change_id: str) -> None:
    write_current_archive(repo, change_id)


def write_embedded_commands(
    repo: Path,
    change_id: str,
    command_lines: list[str],
) -> None:
    evidence = archive_path(repo, change_id) / "evidence.md"
    content = replace_section(
        evidence.read_text(encoding="utf-8"),
        "### Commands",
        command_lines,
    )
    evidence.write_text(content, encoding="utf-8")


def archive_path(repo: Path, change_id: str) -> Path:
    return repo / ".sdf" / "evidence" / change_id


if __name__ == "__main__":
    unittest.main()
