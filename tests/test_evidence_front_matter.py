import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from tests.evidence_archive_helpers import populated_template_for

from sdf_cli.closeout_handoff import run_closeout_handoff
from sdf_cli.evidence_archive_check import check_evidence_archive
from sdf_cli.evidence_contract import EvidenceMachineRecord
from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    initialize_evidence_machine_record,
    load_evidence_machine_record,
    update_declared_run_context,
    update_evidence_machine_record,
)
from sdf_cli.evidence_machine_context import UNAVAILABLE, repository_context


class EvidenceMachineRecordTest(unittest.TestCase):
    def test_repository_context_uses_repo_relative_path_for_selected_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "selected-repository"
            repo.mkdir()

            with patch(
                "sdf_cli.evidence_machine_context._git_output",
                return_value="git@github.com:owner/selected-repository.git",
            ):
                context = repository_context(repo)

        self.assertEqual(context["name"], "selected-repository")
        self.assertEqual(context["path"], ".")
        self.assertEqual(context["github"], "owner/selected-repository")

    def test_repository_context_is_unavailable_without_selected_repository(self):
        self.assertEqual(
            repository_context(None),
            {"name": UNAVAILABLE, "path": UNAVAILABLE, "github": UNAVAILABLE},
        )

    def test_contract_five_round_trips_without_changing_human_body(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.md"
            path.write_text("# Evidence\n\nHuman text\n")
            initialize_evidence_machine_record(
                path, change_id="slice", started_at="2026-01-01T00:00:00+00:00"
            )
            update_declared_run_context(
                path,
                change_id="slice",
                declared={
                    "surface": "codex_local",
                    "model": "gpt-5.5",
                    "reasoning": "medium",
                    "speed": "fast",
                },
            )
            content = path.read_text()
            record = load_evidence_machine_record(path, change_id="slice")
        self.assertIn("Human text", content)
        self.assertIn("contract: 5", content)
        self.assertIn("repository:", content)
        self.assertIn("branch:", content)
        self.assertIsInstance(record, EvidenceMachineRecord)
        self.assertEqual(record.declared["model"], "gpt-5.5")

    def test_contract_five_machine_record_rerenders_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.md"
            path.write_text("# Evidence\n\nHuman text\n")
            initialize_evidence_machine_record(
                path, change_id="slice", started_at="2026-01-01T00:00:00+00:00"
            )
            record = load_evidence_machine_record(path, change_id="slice")
            original = path.read_bytes()
            assert record is not None

            update_evidence_machine_record(path, change_id="slice", record=record)

            self.assertEqual(path.read_bytes(), original)

    def test_historical_record_is_one_clear_unsupported_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.md"
            path.write_text("# Evidence\n")
            with self.assertRaisesRegex(
                EvidenceFrontMatterError, "historical or unsupported"
            ):
                load_evidence_machine_record(path, change_id="old")

    def test_contract_three_archive_is_reported_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            archive = repo / ".sdf/evidence/old"
            archive.mkdir(parents=True)
            evidence = archive / "evidence.md"
            original = (
                populated_template_for("evidence.md")
                + "## Machine Record\n\n```yaml\ncontract: 3\n```\n"
            )
            evidence.write_text(original, encoding="utf-8")
            result = check_evidence_archive(str(repo), "old")
            unchanged = evidence.read_text(encoding="utf-8")

        self.assertTrue(result.historical)
        self.assertEqual(unchanged, original)

    def test_incomplete_contract_four_fields_are_historical_and_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence = self._populated_contract_four(repo, "incomplete")
            original = evidence.read_text(encoding="utf-8").replace(
                'closeout_status: "open"\n', ""
            )
            evidence.write_text(original, encoding="utf-8")

            result = check_evidence_archive(str(repo), "incomplete")
            handoff = run_closeout_handoff(str(repo), "incomplete")
            unchanged = evidence.read_text(encoding="utf-8")

        self.assertFalse(result.passed)
        self.assertTrue(result.historical)
        self.assertEqual(
            result.files[0].front_matter_error,
            "historical or unsupported evidence machine record "
            "(contract 4 or 5 required)",
        )
        self.assertEqual(handoff.closeout_record_written, False)
        self.assertEqual(unchanged, original)

    def test_missing_contract_four_writer_is_historical(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence = self._populated_contract_four(repo, "missing-writer")
            original = evidence.read_text(encoding="utf-8").replace(
                'written_by: "software-dark-factory 0.1.0"\n', ""
            )
            evidence.write_text(original, encoding="utf-8")

            result = check_evidence_archive(str(repo), "missing-writer")

        self.assertTrue(result.historical)
        self.assertEqual(
            result.files[0].front_matter_error,
            "historical or unsupported evidence machine record "
            "(contract 4 or 5 required)",
        )

    def test_malformed_contract_four_boolean_and_latest_check_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence = self._populated_contract_four(repo, "malformed")
            record = load_evidence_machine_record(evidence, change_id="malformed")
            assert record is not None
            update_evidence_machine_record(
                evidence,
                change_id="malformed",
                record=replace(
                    record,
                    total_runs=1,
                    latest_run={
                        "status": "passed",
                        "total_duration_seconds": 1.0,
                        "checks": [
                            {
                                "name": "unit",
                                "status": "passed",
                                "duration_seconds": 1.0,
                            }
                        ],
                    },
                ),
            )
            original = evidence.read_text(encoding="utf-8").replace(
                "  final_pass_followed_earlier_failure: false\n", ""
            )
            evidence.write_text(
                original.replace("        duration_seconds: 1.00\n", ""),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvidenceFrontMatterError, "historical or unsupported"
            ):
                load_evidence_machine_record(evidence, change_id="malformed")
            result = check_evidence_archive(str(repo), "malformed")
            unchanged = evidence.read_text(encoding="utf-8")

        self.assertTrue(result.historical)
        self.assertEqual(
            unchanged, original.replace("        duration_seconds: 1.00\n", "")
        )

    def _populated_contract_four(self, repo: Path, change_id: str) -> Path:
        evidence = repo / ".sdf" / "evidence" / change_id / "evidence.md"
        evidence.parent.mkdir(parents=True)
        evidence.write_text(populated_template_for("evidence.md"), encoding="utf-8")
        initialize_evidence_machine_record(
            evidence,
            change_id=change_id,
            started_at="2026-01-01T00:00:00+00:00",
            contract_version=4,
        )
        return evidence
