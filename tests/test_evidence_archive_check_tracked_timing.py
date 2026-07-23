import tempfile
import unittest
from pathlib import Path

from tests.evidence_archive_helpers import (
    replace_section,
    write_current_archive,
)

from sdf_cli.evidence_archive_check import (
    check_evidence_archive,
    render_evidence_archive_check,
)


class EvidenceArchiveCheckTrackedTimingTest(unittest.TestCase):
    def test_missing_tracked_timing_breakdown_passes_when_status_is_present(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "missing-tracked-timing")
            write_embedded_verification(
                repo,
                "missing-tracked-timing",
                    [
                        "  - Status: passed.",
                        "  - Timing: 1.04s total duration reported by SDF summary.",
                    ],
            )

            result = run_check(repo, "missing-tracked-timing")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("status: ready", result.stdout)

    def test_allows_tracked_timings_not_reported_when_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "tracked-timing-not-reported")
            write_embedded_verification(
                repo,
                "tracked-timing-not-reported",
                    [
                        "  - Status: passed.",
                        "  - Timing: 1.04s total duration reported by SDF summary.",
                        "  - Tracked timings: not reported by full "
                        "verification output.",
                    ],
            )

            result = run_check(repo, "tracked-timing-not-reported")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("status: ready", result.stdout)

    def test_accepts_recorded_tracked_timing_breakdown(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "tracked-timing-recorded")
            write_embedded_verification(
                repo,
                "tracked-timing-recorded",
                    [
                        "  - Status: passed.",
                        "  - Timing: 1.04s total duration reported by SDF summary.",
                        "  - Tracked timings:",
                        "    - python-unit-tests: 0.65s.",
                        "    - ruff: 0.15s.",
                    ],
            )

            result = run_check(repo, "tracked-timing-recorded")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("status: ready", result.stdout)


class CommandResult:
    def __init__(self, exit_code: int, stdout: str) -> None:
        self.exit_code = exit_code
        self.stdout = stdout


def embedded_command_lines(command_details: list[str]) -> list[str]:
    return [
        "- Command: `PYTHONPATH=src python3 -m sdf_cli.main "
        "verify --repo .`",
        *command_details,
    ]


def run_check(repo: Path, change_id: str) -> CommandResult:
    result = check_evidence_archive(repo=str(repo), change_id=change_id)
    return CommandResult(
        exit_code=result.exit_code,
        stdout=render_evidence_archive_check(result),
    )


def write_archive(repo: Path, change_id: str) -> None:
    write_current_archive(repo, change_id)


def write_embedded_verification(
    repo: Path,
    change_id: str,
    command_details: list[str],
) -> None:
    evidence = archive_path(repo, change_id) / "evidence.md"
    content = replace_section(
        evidence.read_text(encoding="utf-8"),
        "### Commands",
        embedded_command_lines(command_details),
    )
    evidence.write_text(content, encoding="utf-8")


def archive_path(repo: Path, change_id: str) -> Path:
    return repo / ".sdf" / "evidence" / change_id


if __name__ == "__main__":
    unittest.main()
