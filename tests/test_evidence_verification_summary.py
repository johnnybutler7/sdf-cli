import unittest
from pathlib import Path

from sdf_cli.evidence_verification_summary import compact_check_summary
from sdf_cli.verification_results import (
    VerificationCommandResult,
    VerificationRunResult,
)


class EvidenceVerificationSummaryTest(unittest.TestCase):
    def test_compact_check_summary_omits_executor_facts(self):
        result = VerificationRunResult(
            repo_path=Path("."),
            config_path=Path("verification.yml"),
            status="passed",
            exit_code=0,
            command_results=(
                VerificationCommandResult(
                    "ok",
                    "echo ok",
                    True,
                    0,
                    "passed",
                    "",
                    "",
                    0.5,
                    facts=(("test_count", 2),),
                ),
            ),
        )
        self.assertEqual(compact_check_summary(result), "`ok` (passed, 0.50s)")
