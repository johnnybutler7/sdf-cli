import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.closeout_summary_fixtures import write_run_context, write_verification_config
from tests.evidence_archive_helpers import write_current_archive
from tests.pr_body_command_helpers import run_pr_body_check, run_pr_body_write

from sdf_cli.pr_body import link_archive_file_references


class CurrentArchivePrBodyHandoffTest(unittest.TestCase):
    def test_embedded_verification_archive_links_to_evidence_verification_section(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            configure_git_context(repo)
            archive = repo / ".sdf" / "evidence" / "embedded-verification"
            write_current_archive(repo, "embedded-verification")
            write_run_context(repo, "embedded-verification")
            write_verification_config(
                repo,
                "version: 1\ncommands:\n  - name: ok\n"
                "    command: python3 -c \"print('ok')\"\n",
            )

            with patch.dict(os.environ, {"GITHUB_PR_HEAD_SHA": "b" * 40}):
                write_result = run_pr_body_write(repo, "embedded-verification")
                check_result = run_pr_body_check(repo, "embedded-verification")
            handoff = (
                repo / ".sdf" / "handoffs" / "embedded-verification" / "pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(write_result.exit_code, 0)
        self.assertEqual(check_result.exit_code, 0)
        self.assertFalse((archive / "verification.md").exists())
        for label, filename, anchor in (
            ("Evidence notes", "evidence.md", "#acceptance--review-focus"),
            ("Evidence notes", "evidence.md", "#machine-record"),
            ("Evidence notes", "evidence.md", "#guidance-applied"),
            ("Evidence notes", "evidence.md", "#verification"),
        ):
            self.assertIn(
                f"- [{label}](https://github.com/acme/sdf-cli/blob/"
                f"{'b' * 40}/.sdf/evidence/embedded-verification/"
                f"{filename}{anchor})",
                handoff,
            )
        for role in (
            "Review evidence:",
            "Run-context evidence:",
            "Guidance evidence:",
            "Verification evidence:",
        ):
            self.assertNotIn(role, handoff)

    def test_current_one_file_references_use_labelled_evidence_notes_links(self):
        change_id = "one-file-links"
        markdown = "\n".join(
            [
                "## Review focus",
                f"- Review evidence: `.sdf/evidence/{change_id}/evidence.md`",
                "## Run context",
                f"- Run-context evidence: `.sdf/evidence/{change_id}/evidence.md`",
                "## Guidance applied",
                f"- Guidance evidence: `.sdf/evidence/{change_id}/evidence.md`",
                "## Verification",
                f"- Verification evidence: `.sdf/evidence/{change_id}/evidence.md`",
            ]
        )

        rendered = link_archive_file_references(
            markdown,
            change_id=change_id,
            link_mode="github",
            github_repo="acme/sdf-cli",
            github_ref="main",
        )

        for anchor in (
            "#acceptance--review-focus",
            "#machine-record",
            "#guidance-applied",
            "#verification",
        ):
            self.assertIn(
                "- [Evidence notes](https://github.com/acme/sdf-cli/blob/"
                f"main/.sdf/evidence/{change_id}/evidence.md{anchor})",
                rendered,
            )
        for role in CURRENT_EVIDENCE_CAPTIONS:
            self.assertNotIn(role, rendered)

    def test_check_reports_regeneration_for_missing_current_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_current_archive(repo, "missing-current-pr-body")
            write_run_context(repo, "missing-current-pr-body")

            result = run_pr_body_check(
                repo,
                "missing-current-pr-body",
                link_mode="repo-relative",
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("missing file: pr-body.md", result.stdout)
        self.assertIn(
            "recovery: sdf close "
            f"--repo {repo} --change-id missing-current-pr-body "
            "--link-mode repo-relative",
            result.stdout,
        )
        self.assertIn(
            "then check: sdf close "
            f"--repo {repo} --change-id missing-current-pr-body "
            "--link-mode repo-relative",
            result.stdout,
        )

    def test_writes_ignored_local_handoff_not_archive_artifact(self):
        active_pr_sha = "a" * 40
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            configure_git_context(repo)
            archive = repo / ".sdf" / "evidence" / "current-pr-body"
            write_current_archive(repo, "current-pr-body")
            write_run_context(repo, "current-pr-body")
            write_verification_config(
                repo,
                "version: 1\ncommands:\n  - name: ok\n"
                "    command: python3 -c \"print('ok')\"\n",
            )

            with patch.dict(os.environ, {"GITHUB_PR_HEAD_SHA": active_pr_sha}):
                write_result = run_pr_body_write(repo, "current-pr-body")
                check_result = run_pr_body_check(repo, "current-pr-body")
            handoff_exists = (
                repo / ".sdf" / "handoffs" / "current-pr-body" / "pr-body.md"
            ).is_file()
            archive_has_pr_body = (archive / "pr-body.md").exists()
            handoff = (
                repo / ".sdf" / "handoffs" / "current-pr-body" / "pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(write_result.exit_code, 0)
        self.assertEqual(check_result.exit_code, 0)
        self.assertTrue(handoff_exists)
        self.assertFalse(archive_has_pr_body)
        self.assertIn(".sdf/handoffs/current-pr-body/pr-body.md", write_result.stdout)
        for fragment in ("#acceptance--review-focus", "#guidance-applied"):
            self.assertIn(
                "- [Evidence notes](https://github.com/acme/sdf-cli/blob/"
                f"{active_pr_sha}/.sdf/evidence/current-pr-body/"
                f"evidence.md{fragment})",
                handoff,
            )
        for role in CURRENT_EVIDENCE_CAPTIONS:
            self.assertNotIn(role, handoff)
        self.assertNotIn(".sdf/handoffs/", handoff)


CURRENT_EVIDENCE_CAPTIONS = (
    "Review evidence:",
    "Run-context evidence:",
    "Guidance evidence:",
    "Verification evidence:",
)


def configure_git_context(repo: Path) -> None:
    subprocess.run(
        ["git", "init", "-b", "feature/current-links"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:acme/sdf-cli.git"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
