import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from sdf_cli.closeout_verification_handoff import verification_history_line
from sdf_cli.evidence_front_matter import (
    initialize_evidence_machine_record,
    load_evidence_machine_record,
    update_evidence_machine_record,
)


class CloseoutVerificationHandoffTest(unittest.TestCase):
    def test_formats_compact_lifetime_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / ".sdf/evidence/sample"
            archive.mkdir(parents=True)
            evidence = archive / "evidence.md"
            evidence.write_text("# Evidence\n", encoding="utf-8")
            initialize_evidence_machine_record(
                evidence, change_id="sample", started_at="2026-01-01T00:00:00+00:00"
            )
            record = load_evidence_machine_record(evidence, change_id="sample")
            assert record is not None
            update_evidence_machine_record(
                evidence,
                change_id="sample",
                record=replace(
                    record,
                    total_runs=2,
                    failed_runs=1,
                    final_pass_followed_earlier_failure=True,
                    latest_run={
                        "status": "passed",
                        "total_duration_seconds": 0.0,
                        "checks": [],
                    },
                ),
            )
            line = verification_history_line(_result(Path(directory)))

        self.assertEqual(
            line,
            "- Verification history: 2 runs; final pass followed an earlier "
            "verification failure.",
        )


def _result(repo):
    class Evidence:
        archive_path = ".sdf/evidence/sample"

    class Verification:
        exit_code = 0

    class Result:
        repo_path = repo
        evidence_result = Evidence()
        verification_result = Verification()

    return Result()
