import unittest

from sdf_cli.evidence_front_matter import EvidenceMachineRecord, render_machine_record


class CompactVerificationRecordTest(unittest.TestCase):
    def test_render_has_only_lifetime_counts_and_latest_checks(self):
        record = EvidenceMachineRecord(
            contract_version=4,
            change_id="sample",
            written_by="software-dark-factory 0.1.0",
            repository={
                "name": "unavailable",
                "path": "unavailable",
                "github": "unavailable",
            },
            branch={"name": "unavailable", "head": "unavailable"},
            declared={
                field: "unknown" for field in ("surface", "model", "reasoning", "speed")
            },
            started_at="2026-01-01T00:00:00+00:00",
            closed_at=None,
            closeout_status="open",
            total_runs=2,
            failed_runs=1,
            final_pass_followed_earlier_failure=True,
            latest_run={
                "status": "passed",
                "total_duration_seconds": 1.0,
                "checks": [{"name": "ok", "status": "passed", "duration_seconds": 1.0}],
            },
            body=b"",
            yaml_start=0,
            yaml_end=0,
        )
        output = render_machine_record(record)
        self.assertIn("total_runs: 2", output)
        self.assertIn("latest_run:", output)
        self.assertNotIn("detail_runs", output)
        self.assertNotIn("schema_version", output)


if __name__ == "__main__":
    unittest.main()
