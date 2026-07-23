import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive
from tests.pr_body_command_helpers import run_command, run_pr_body_check


class CloseoutPrBodyGithubReviewGuardTest(unittest.TestCase):
    def test_pr_body_check_github_mode_rejects_repo_relative_evidence_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            change_id = "repo-relative-github-pr-body"
            write_archive(repo, change_id)
            write_pr_body_with_repo_relative_links(repo, change_id)

            result = run_pr_body_check(
                repo,
                change_id,
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref="1234567890abcdef1234567890abcdef12345678",
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("status: not ready", result.stdout)
        self.assertIn(
            "repo-relative evidence link in GitHub mode: "
            ".sdf/evidence/repo-relative-github-pr-body/evidence.md",
            result.stdout,
        )
        self.assertNotIn("missing evidence link", result.stdout)

    def test_close_help_requires_immutable_head_sha_links(self):
        result = run_command(["close", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("<full-pr-head-sha>", result.stdout)
        self.assertIn(
            "By default, close infers GitHub blob links from origin and the "
            "immutable current HEAD when possible",
            result.stdout,
        )
        self.assertIn(
            "repo-relative links for local/offline review",
            result.stdout,
        )


def write_pr_body_with_repo_relative_links(repo: Path, change_id: str) -> None:
    artifact = repo / ".sdf" / "handoffs" / change_id / "pr-body.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            [
                "# What you are reviewing",
                "",
                "## Review focus",
                "",
                "## Run context",
                "",
                "## Guidance applied",
                "",
                "## Verification",
                "",
                f"- [Evidence notes](.sdf/evidence/{change_id}/evidence.md)",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
