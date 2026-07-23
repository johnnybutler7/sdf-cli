import tempfile
import unittest
from pathlib import Path

from tests.evidence_archive_helpers import current_template_for, populated_template_for

from sdf_cli.evidence_archive_check import (
    check_evidence_archive,
    render_evidence_archive_check,
)
from sdf_cli.evidence_archive_contract import (
    CONTRACT_FOUR_ARCHIVE_HEADINGS,
    REQUIRED_ARCHIVE_HEADINGS,
)
from sdf_cli.evidence_front_matter import (
    initialize_evidence_machine_record,
    load_evidence_machine_record,
)


class EvidenceArchiveCheckTest(unittest.TestCase):
    def test_current_dogfood_archive_is_one_contract_five_evidence_file(self):
        archive = (
            Path(".")
            / ".sdf"
            / "evidence"
            / "concise-late-evidence-contract"
        )
        evidence = archive / "evidence.md"
        if not evidence.is_file():
            self.skipTest("current dogfood archive has not been synthesized yet")
        content = evidence.read_text(encoding="utf-8")
        record = load_evidence_machine_record(
            evidence,
            change_id="concise-late-evidence-contract",
        )

        self.assertEqual(
            tuple(sorted(path.name for path in archive.iterdir() if path.is_file())),
            ("evidence.md",),
        )
        self.assertEqual(content.count("## Machine Record"), 1)
        self.assertEqual(content.count("```yaml\ncontract: 5\n"), 1)
        self.assertIsNotNone(record)

    def test_valid_archive_with_routine_files_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "valid-routine")

            result = run_check(repo, "valid-routine")

            self.assertEqual(result.exit_code, 0)
            self.assertIn(
                "Evidence archive check: .sdf/evidence/valid-routine",
                result.stdout,
            )
            self.assertIn(
                f"Resolved repository path: {repo.resolve()}",
                result.stdout,
            )
            self.assertIn("status: ready", result.stdout)
            self.assertIn("present: evidence.md", result.stdout)

    def test_missing_archive_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            result = run_check(repo, "missing-archive")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn(
                "missing archive: .sdf/evidence/missing-archive",
                result.stdout,
            )
            self.assertFalse((repo / ".sdf").exists())

    def test_missing_required_routine_file_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            archive_path(repo, "missing-routine").mkdir(parents=True)
            (archive_path(repo, "missing-routine") / "review.md").write_text(
                "historical\n", encoding="utf-8"
            )

            result = run_check(repo, "missing-routine")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn("missing file: evidence.md", result.stdout)

    def test_missing_required_heading_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "missing-heading")
            evidence = archive_path(repo, "missing-heading") / "evidence.md"
            evidence.write_text(
                "# Evidence\n## Request / Provenance\n", encoding="utf-8"
            )
            initialize_evidence_machine_record(
                evidence,
                change_id="missing-heading",
                started_at="2026-01-01T09:00:00+00:00",
                contract_version=4,
            )

            result = run_check(repo, "missing-heading")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn(
                "missing heading in evidence.md: ## Risk / Confidence / Limits",
                result.stdout,
            )

    def test_missing_verification_command_status_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "missing-command-status")
            evidence = archive_path(repo, "missing-command-status") / "evidence.md"
            evidence.write_text(
                "\n".join(
                    [
                        "# Evidence",
                        "",
                        "## Request / Provenance",
                        "## Change Summary",
                        "## Acceptance / Review Focus",
                        "## Scope",
                        "## Boundaries / Non-Claims",
                        "## Risk / Confidence / Limits",
                        "## Guidance Applied",
                        "### Consulted",
                        "### Applied",
                        "### Not Applicable",
                        "### Why This Mattered",
                        "### Gaps / Learning",
                        "## Verification",
                        "",
                        "### Commands",
                        "",
                        "- Command: `python3 -m ruff check src tests`",
                        "",
                        "### Results",
                        "",
                        "- Final closeout result: not recorded yet.",
                        "",
                        "### Blockers / Skips",
                        "",
                        "No blockers or skips.",
                        "",
                        "### Evidence Output",
                        "",
                        "Not recorded.",
                        "",
                        "## Run / Handoff Context",
                        "## Handoff / Reviewer Notes",
                    ]
                ),
                encoding="utf-8",
            )
            initialize_evidence_machine_record(
                evidence,
                change_id="missing-command-status",
                started_at="2026-01-01T09:00:00+00:00",
                contract_version=4,
            )

            result = run_check(repo, "missing-command-status")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn(
                "missing verification status in evidence.md: command 1 missing Status:",
                result.stdout,
            )

    def test_new_contract_empty_judgement_fields_fail_with_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "fresh-scaffold", populated=False)

            result = run_check(repo, "fresh-scaffold")

            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not ready", result.stdout)
            self.assertIn(
                "unresolved scaffold placeholder in evidence.md "
                "## Intent: needs judgement",
                result.stdout,
            )
            self.assertIn(
                "unresolved scaffold placeholder in evidence.md "
                "## Guidance applied: needs judgement",
                result.stdout,
            )
            self.assertIn(
                "recovery: replace scaffold prompts with specific evidence; "
                "the checker is read-only and does not auto-fill evidence.",
                result.stdout,
            )


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


def write_archive(repo: Path, change_id: str, populated: bool = True) -> None:
    archive = archive_path(repo, change_id)
    archive.mkdir(parents=True)
    content = (
        populated_template_for("evidence.md")
        if populated
        else current_template_for("evidence.md")
    )
    required_headings = (
        CONTRACT_FOUR_ARCHIVE_HEADINGS
        if populated
        else REQUIRED_ARCHIVE_HEADINGS["evidence.md"]
    )
    for heading in required_headings:
        if heading == "## Machine Record":
            continue
        assert heading in content
    evidence = archive / "evidence.md"
    evidence.write_text(content, encoding="utf-8")
    initialize_evidence_machine_record(
        evidence,
        change_id=change_id,
        started_at="2026-01-01T09:00:00+00:00",
        contract_version=4 if populated else 5,
    )


def archive_path(repo: Path, change_id: str) -> Path:
    return repo / ".sdf" / "evidence" / change_id
