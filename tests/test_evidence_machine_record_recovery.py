import tempfile
import unittest
from pathlib import Path

from tests.evidence_archive_helpers import current_template_for, populated_template_for

from sdf_cli.evidence_archive_check import (
    check_evidence_archive,
    render_evidence_archive_check,
)
from sdf_cli.evidence_front_matter import (
    initialize_evidence_machine_record,
    load_evidence_machine_record,
)


class EvidenceMachineRecordRecoveryTest(unittest.TestCase):
    def test_contract_five_unsupported_field_reports_error_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence = self._current_contract_five(repo, "unsupported-field")
            original = evidence.read_text(encoding="utf-8")
            evidence.write_text(
                original.replace(
                    'contract: 5\n', 'contract: 5\nunexpected: "field"\n'
                ),
                encoding="utf-8",
            )

            result = check_evidence_archive(str(repo), "unsupported-field")
            output = render_evidence_archive_check(result)

        self.assertFalse(result.passed)
        self.assertEqual(result.files[0].missing_headings, ())
        self.assertIn("invalid contract 5 machine record", output)
        self.assertIn("unsupported fields", output)
        self.assertIn("## Machine Record is tool-owned", output)
        self.assertIn("Restore evidence.md from Git", output)
        self.assertIn("sdf start --change-id unsupported-field", output)

    def test_contract_five_malformed_yaml_reports_the_parser_error_first(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence = self._current_contract_five(repo, "malformed-yaml")
            original = evidence.read_text(encoding="utf-8")
            evidence.write_text(
                original.replace('contract: 5\n', 'contract: 5\n  malformed\n'),
                encoding="utf-8",
            )

            result = check_evidence_archive(str(repo), "malformed-yaml")
            output = render_evidence_archive_check(result)

        self.assertFalse(result.passed)
        self.assertIn("machine-record YAML is malformed", output)
        self.assertNotIn("missing heading", output)

    def test_valid_contract_five_and_historical_contract_four_remain_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            current = self._current_contract_five(repo, "current")
            historical = self._contract_four(repo, "historical")

            current_record = load_evidence_machine_record(current, change_id="current")
            historical_record = load_evidence_machine_record(
                historical, change_id="historical"
            )

        self.assertEqual(current_record.contract_version, 5)
        self.assertEqual(historical_record.contract_version, 4)

    def _current_contract_five(self, repo: Path, change_id: str) -> Path:
        evidence = repo / ".sdf" / "evidence" / change_id / "evidence.md"
        evidence.parent.mkdir(parents=True)
        evidence.write_text(current_template_for("evidence.md"), encoding="utf-8")
        initialize_evidence_machine_record(
            evidence,
            change_id=change_id,
            started_at="2026-01-01T00:00:00+00:00",
        )
        return evidence

    def _contract_four(self, repo: Path, change_id: str) -> Path:
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
