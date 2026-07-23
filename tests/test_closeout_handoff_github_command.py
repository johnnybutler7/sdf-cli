import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.closeout_summary_fixtures import (
    write_archive,
    write_run_context,
    write_sentinel_verification_config,
    write_verification_config,
)
from tests.pr_body_command_helpers import run_handoff

from sdf_cli.pr_body import PrBodyWriteResult, pr_body_artifact_path

BRANCH_REF_WARNING = "warning: --github-ref is not a full 40-character commit SHA"
FULL_SHA = "1234567890abcdef1234567890abcdef12345678"


class CloseoutHandoffGithubCommandTest(unittest.TestCase):
    def test_github_link_mode_requires_repo_and_ref_before_closeout(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_archive(repo, "handoff-github-required")
            write_sentinel_verification_config(repo, marker)

            result = run_handoff(
                repo,
                "handoff-github-required",
                link_mode="github",
            )

        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "--github-repo is required when --link-mode github",
            result.stderr,
        )
        self.assertIn(
            "--github-ref is required when --link-mode github",
            result.stderr,
        )
        self.assertFalse(marker.exists())

    def test_github_link_mode_writes_checked_blob_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(
                repo,
                "handoff-github",
                playbook_applied_lines=["- Testing shaped link coverage."],
                playbook_consulted_lines=["- `.sdf/playbooks/engineering.md`."],
            )
            write_run_context(repo, "handoff-github")
            write_ok_verification(repo)

            result = run_handoff(
                repo,
                "handoff-github",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=FULL_SHA,
            )
            artifact = repo / ".sdf" / "handoffs" / "handoff-github" / "pr-body.md"
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("pr-body check: ready", result.stdout)
        self.assertNotIn(BRANCH_REF_WARNING, result.stdout)
        self.assertIn(
            "https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/handoff-github/evidence.md",
            content,
        )
        self.assertIn(
            "https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/handoff-github/evidence.md#verification",
            content,
        )
        self.assertNotIn("](.sdf/evidence/handoff-github/", content)

    def test_github_link_guard_reports_repo_relative_artifact_on_check(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "handoff-github-guard")
            write_ok_verification(repo)
            first = run_handoff(repo, "handoff-github-guard")
            fake_write = successful_fake_write("handoff-github-guard")

            with patch(
                "sdf_cli.closeout_handoff.write_pr_body_artifact",
                return_value=fake_write,
            ):
                guarded = run_handoff(
                    repo,
                    "handoff-github-guard",
                    link_mode="github",
                    github_repo="acme/sdf-cli",
                    github_ref=FULL_SHA,
                )

        self.assertEqual(first.exit_code, 0)
        self.assertEqual(guarded.exit_code, 1)
        self.assertIn("closeout check: passed", guarded.stdout)
        self.assertIn(
            "pr-body write: written (.sdf/handoffs/handoff-github-guard/pr-body.md)",
            guarded.stdout,
        )
        self.assertIn("pr-body check: failed", guarded.stdout)
        self.assertIn(
            "repo-relative evidence link in GitHub mode: "
            ".sdf/evidence/handoff-github-guard/evidence.md",
            guarded.stdout,
        )

    def test_branch_ref_is_rejected_but_full_sha_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "handoff-branch-ref")
            write_ok_verification(repo)
            branch_result = run_handoff(
                repo,
                "handoff-branch-ref",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref="feature/handoff",
            )

            write_archive(repo, "handoff-full-sha")
            sha_result = run_handoff(
                repo,
                "handoff-full-sha",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=FULL_SHA,
            )

        self.assertEqual(branch_result.exit_code, 2)
        self.assertEqual(sha_result.exit_code, 0)
        self.assertIn(
            "--github-ref must be the full 40-character immutable PR head SHA",
            branch_result.stderr,
        )
        self.assertNotIn(BRANCH_REF_WARNING, sha_result.stdout)


def write_ok_verification(repo: Path) -> None:
    write_verification_config(
        repo,
        """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
    )


def successful_fake_write(change_id: str) -> PrBodyWriteResult:
    return PrBodyWriteResult(
        change_id=change_id,
        artifact_path=pr_body_artifact_path(change_id),
        written=True,
    )


if __name__ == "__main__":
    unittest.main()
