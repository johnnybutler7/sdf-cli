import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_verification_config
from tests.evidence_archive_helpers import write_current_archive
from tests.pr_body_command_helpers import run_handoff
from tests.test_closeout_handoff_command import write_verification_counter


class CloseoutHandoffResultRecordTest(unittest.TestCase):
    def test_contract_four_records_only_compact_current_run_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_current_archive(repo, "handoff-success")
            write_verification_counter(repo, repo / "count.txt")
            result = run_handoff(repo, "handoff-success")
            record = (repo / ".sdf/evidence/handoff-success/evidence.md").read_text()

        self.assertEqual(result.exit_code, 0)
        for expected in (
            "contract: 4",
            'written_by: "software-dark-factory 0.1.0"',
            'closeout_status: "passed"',
            "total_runs: 1",
            "failed_runs: 0",
            'status: "passed"',
            'name: "count-verification"',
        ):
            self.assertIn(expected, record)
        for removed in (
            "schema_version",
            "archive_contract_version",
            "closeout_result:",
            "detail_runs",
            "verification_history",
            "facts:",
            "recorded_at",
        ):
            self.assertNotIn(removed, record)

    def test_closeout_refreshes_the_writer_to_the_executing_cli_version(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            change_id = "refresh-writer"
            write_current_archive(repo, change_id)
            evidence_path = repo / ".sdf/evidence" / change_id / "evidence.md"
            evidence_path.write_text(
                evidence_path.read_text(encoding="utf-8").replace(
                    'written_by: "software-dark-factory 0.1.0"',
                    'written_by: "software-dark-factory 0.0.14"',
                ),
                encoding="utf-8",
            )
            write_verification_counter(repo, repo / "count.txt")

            result = run_handoff(repo, change_id)
            record = evidence_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn('written_by: "software-dark-factory 0.1.0"', record)
        self.assertNotIn('written_by: "software-dark-factory 0.0.14"', record)

    def test_failed_then_passing_run_retains_only_the_compact_aggregate(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            change_id = "handoff-history"
            write_current_archive(repo, change_id)
            write_verification_config(
                repo,
                """version: 1
commands:
  - name: fail
    command: python3 -c \"import sys; sys.exit(1)\"
""",
            )
            self.assertEqual(run_handoff(repo, change_id).exit_code, 1)
            write_verification_config(
                repo,
                """version: 1
commands:
  - name: fixed
    command: python3 -c \"print('ok')\"
""",
            )
            self.assertEqual(run_handoff(repo, change_id, overwrite=True).exit_code, 0)
            record = (repo / ".sdf/evidence" / change_id / "evidence.md").read_text()

        self.assertIn("total_runs: 2", record)
        self.assertIn("failed_runs: 1", record)
        self.assertIn("final_pass_followed_earlier_failure: true", record)
        self.assertIn('name: "fixed"', record)
        self.assertNotIn('name: "fail"', record)
        self.assertNotIn("detail_runs", record)


if __name__ == "__main__":
    unittest.main()
