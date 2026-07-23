import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive, write_verification_config
from tests.pr_body_command_helpers import run_pr_body_check, run_pr_body_write

COMMIT_SHA = "0123456789abcdef0123456789abcdef01234567"


class CloseoutPrBodyGithubRefStabilityTest(unittest.TestCase):
    def test_pr_body_write_github_mode_commit_sha_ref_has_no_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "github-pr-body-sha")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )

            result = run_pr_body_write(
                repo,
                "github-pr-body-sha",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=COMMIT_SHA,
            )
            artifact = (
                repo / ".sdf" / "handoffs" / "github-pr-body-sha" / "pr-body.md"
            )
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("warning: --github-ref", result.stdout)
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{COMMIT_SHA}/.sdf/evidence/github-pr-body-sha/"
            "evidence.md#acceptance--review-focus)",
            content,
        )

    def test_pr_body_write_rejects_malformed_github_ref_local_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "bad-github-ref")

            result = run_pr_body_write(
                repo,
                "bad-github-ref",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref="/Users/example/sdf-cli",
            )

        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "--github-ref must be the full 40-character immutable PR head SHA",
            result.stderr,
        )

    def test_pr_body_check_github_mode_commit_sha_ref_has_no_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "valid-github-pr-body-sha")
            write_pr_body_with_links(repo, "valid-github-pr-body-sha")

            result = run_pr_body_check(
                repo,
                "valid-github-pr-body-sha",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=COMMIT_SHA,
            )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("status: ready", result.stdout)
        self.assertNotIn("warning: --github-ref", result.stdout)


def write_pr_body_with_links(repo: Path, change_id: str) -> None:
    artifact = repo / ".sdf" / "handoffs" / change_id / "pr-body.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    links = [
        github_blob(change_id, "evidence.md"),
    ]
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
                f"- [Evidence notes]({links[0]})",
            ]
        ),
        encoding="utf-8",
    )


def github_blob(change_id: str, filename: str) -> str:
    return (
        f"https://github.com/acme/sdf-cli/blob/{COMMIT_SHA}/"
        f".sdf/evidence/{change_id}/{filename}"
    )


if __name__ == "__main__":
    unittest.main()
