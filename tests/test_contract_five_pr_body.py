from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_archive,
    write_verification_config,
)
from tests.contract_five_pr_body_fixtures import (
    known_context,
    write_contract_five_archive,
    write_passing_verification,
)
from tests.pr_body_command_helpers import run_handoff, run_pr_body_write
from tests.pr_body_finalize_helpers import FakeGithubPrBoundary

from sdf_cli.closeout_check import run_closeout_check
from sdf_cli.pr_body import render_pr_body_markdown
from sdf_cli.pr_body_finalize_merged import (
    FinalizeMergedPrBodyOptions,
    finalize_merged_pr_body,
)

FULL_SHA = "1234567890abcdef1234567890abcdef12345678"
MERGE_SHA = "abcdef0123456789abcdef0123456789abcdef01"


class ContractFivePrBodyTest(unittest.TestCase):
    def test_small_passing_contract_five_change_gets_compact_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(
                repo,
                "tiny-pass",
                intent=["- Rename one reviewer-facing label."],
                review_focus=["- Review the label text and matching assertion."],
                limits=[
                    "- Standard SDF non-claims: `.sdf/standard-sdf-non-claims.md`.",
                    "- None material.",
                ],
                guidance=[
                    "- Applied: this detailed guidance should stay in evidence.",
                ],
                declared=known_context(),
            )
            write_passing_verification(repo, check_count=2)

            result = run_pr_body_write(repo, "tiny-pass")
            content = (repo / ".sdf/handoffs/tiny-pass/pr-body.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("- Rename one reviewer-facing label.", content)
        self.assertIn("## Review focus", content)
        self.assertNotIn("## Limits", content)
        self.assertIn("- Full verification: passed (2 checks,", content)
        self.assertNotIn("- Checks:", content)
        self.assertNotIn("check-1", content)
        self.assertIn(
            "- Applied: this detailed guidance should stay in evidence.",
            content,
        )
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/tiny-pass/evidence.md)",
            content,
        )
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/tiny-pass/"
            "evidence.md#guidance-applied)",
            content,
        )
        self.assertEqual(content.count("- [Evidence notes]("), 5)

    def test_contract_five_material_limits_are_rendered(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(
                repo,
                "material-limits",
                limits=[
                    "- Standard SDF non-claims: `.sdf/standard-sdf-non-claims.md`.",
                    "- No live receiver refresh was performed in this slice.",
                ],
                declared=known_context(),
            )
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "material-limits")
            content = (
                repo / ".sdf/handoffs/material-limits/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("## Limits", content)
        self.assertIn(
            "- No live receiver refresh was performed in this slice.",
            content,
        )
        self.assertNotIn("Standard SDF non-claims", content)

    def test_failed_verification_expands_check_detail(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(repo, "failed-verification")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: failing-check
    command: python3 -c "import sys; sys.exit(7)"
""",
            )

            closeout = run_closeout_check(str(repo), "failed-verification")
            content = render_pr_body_markdown(closeout)

        self.assertEqual(closeout.exit_code, 1)
        self.assertIn("- Full verification: failed (1 check,", content)
        self.assertIn("- Checks: `failing-check` (failed, exit 7,", content)

    def test_passing_verification_after_earlier_failure_adds_history(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(repo, "fixed-after-failure")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: once-failing-check
    command: python3 -c "import sys; sys.exit(3)"
""",
            )
            first = run_handoff(repo, "fixed-after-failure")
            write_passing_verification(repo)

            second = run_handoff(repo, "fixed-after-failure")
            content = (
                repo / ".sdf/handoffs/fixed-after-failure/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(first.exit_code, 1)
        self.assertEqual(second.exit_code, 0)
        self.assertIn("- Full verification: passed (1 check,", content)
        self.assertIn(
            "- Verification history: final pass followed an earlier verification "
            "failure (1 failed of 2 runs).",
            content,
        )
        self.assertIn("- Checks: `check-1` (passed,", content)

    def test_unknown_run_context_is_materially_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(repo, "unknown-context", declared=None)
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "unknown-context")
            content = (
                repo / ".sdf/handoffs/unknown-context/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "- Unknown run-context fields: surface, model, reasoning, speed.",
            content,
        )

    def test_contract_four_handoff_still_includes_applied_guidance(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(
                repo,
                "contract-four",
                playbook_applied_lines=["- Contract-4 guidance remains visible."],
            )
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "contract-four")
            content = (repo / ".sdf/handoffs/contract-four/pr-body.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("- Applied: Contract-4 guidance remains visible.", content)
        self.assertNotIn("- Guidance details:", content)

    def test_contract_five_evidence_links_support_repo_github_and_finalization(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(repo, "link-modes", declared=known_context())
            write_passing_verification(repo)

            local_result = run_pr_body_write(
                repo,
                "link-modes",
                link_mode="repo-relative",
            )
            local_content = (
                repo / ".sdf/handoffs/link-modes/pr-body.md"
            ).read_text(encoding="utf-8")
            github_result = run_pr_body_write(
                repo,
                "link-modes",
                overwrite=True,
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=FULL_SHA,
            )
            github_content = (
                repo / ".sdf/handoffs/link-modes/pr-body.md"
            ).read_text(encoding="utf-8")
            github = FakeGithubPrBoundary(github_content)

            finalized = finalize_merged_pr_body(
                FinalizeMergedPrBodyOptions(
                    pr_number="42",
                    github_repo="acme/sdf-cli",
                    merge_sha=MERGE_SHA,
                ),
                github=github,
            )

        self.assertEqual(local_result.exit_code, 0)
        self.assertIn(
            "[Evidence notes](.sdf/evidence/link-modes/evidence.md)",
            local_content,
        )
        self.assertEqual(github_result.exit_code, 0)
        self.assertIn(
            f"[Evidence notes](https://github.com/acme/sdf-cli/blob/{FULL_SHA}/"
            ".sdf/evidence/link-modes/evidence.md)",
            github_content,
        )
        self.assertTrue(finalized.updated)
        self.assertIsNotNone(github.updated_body)
        assert github.updated_body is not None
        self.assertIn(
            f"blob/{MERGE_SHA}/.sdf/evidence/link-modes/evidence.md",
            github.updated_body,
        )


if __name__ == "__main__":
    unittest.main()
