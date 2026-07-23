import unittest
from pathlib import Path

from sdf_cli.closeout_check import CloseoutCheckResult
from sdf_cli.closeout_handoff import CloseoutHandoffResult, render_closeout_handoff
from sdf_cli.evidence_archive_check import (
    EvidenceArchiveCheckResult,
    EvidenceArchiveFileCheck,
)
from sdf_cli.pr_body_artifact import PrBodyWriteResult
from sdf_cli.pr_body_check import PrBodyCheckResult
from sdf_cli.verification_results import VerificationRunResult


class CloseoutHandoffRenderingTest(unittest.TestCase):
    def test_renders_pr_body_check_problems_after_deduplicated_warnings(self):
        result = CloseoutHandoffResult(
            change_id="rendering",
            closeout_result=_passing_closeout_result(),
            write_result=PrBodyWriteResult(
                change_id="rendering",
                artifact_path=".sdf/handoffs/rendering/pr-body.md",
                written=True,
                warnings=("shared warning", "write warning"),
            ),
            check_result=PrBodyCheckResult(
                change_id="rendering",
                artifact_path=".sdf/handoffs/rendering/pr-body.md",
                exists=True,
                missing_sections=("## Verification",),
                missing_evidence_links=("evidence.md",),
                broken_evidence_links=(".sdf/evidence/rendering/missing.md",),
                absolute_evidence_links=("/tmp/evidence.md",),
                repo_relative_evidence_links=(".sdf/evidence/rendering/evidence.md",),
                wrong_github_evidence_links=("https://github.com/example/wrong",),
                warnings=("shared warning", "check warning"),
            ),
            closeout_record_written=True,
        )

        self.assertEqual(
            render_closeout_handoff(result),
            "\n".join(
                [
                    "SDF close",
                    f"Resolved repository path: {Path('receiver').resolve()}",
                    "closeout check: passed",
                    "closeout result record: written "
                    "(.sdf/evidence/rendering/evidence.md machine record)",
                    "pr-body write: written (.sdf/handoffs/rendering/pr-body.md)",
                    "pr-body check: failed",
                    "github: not mutated",
                    "shared warning",
                    "write warning",
                    "check warning",
                    "missing section: ## Verification",
                    "missing evidence link: evidence.md",
                    "broken evidence link: .sdf/evidence/rendering/missing.md",
                    "absolute evidence link: /tmp/evidence.md",
                    "repo-relative evidence link in GitHub mode: "
                    ".sdf/evidence/rendering/evidence.md",
                    "wrong GitHub evidence link: https://github.com/example/wrong",
                ]
            ),
        )


def _passing_closeout_result() -> CloseoutCheckResult:
    repo_path = Path("receiver")
    return CloseoutCheckResult(
        repo_label="receiver",
        repo_path=repo_path,
        evidence_result=EvidenceArchiveCheckResult(
            change_id="rendering",
            repo_path=repo_path,
            archive_exists=True,
            files=(
                EvidenceArchiveFileCheck(
                    filename="evidence.md",
                    exists=True,
                    missing_headings=(),
                    contract_version=5,
                ),
            ),
        ),
        verification_result=VerificationRunResult(
            repo_path=repo_path,
            config_path=repo_path / ".sdf/verification.yml",
            status="passed",
            exit_code=0,
            command_results=(),
        ),
    )


if __name__ == "__main__":
    unittest.main()
