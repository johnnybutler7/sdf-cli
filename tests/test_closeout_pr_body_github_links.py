import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive, write_verification_config
from tests.pr_body_command_helpers import run_pr_body_check, run_pr_body_write

FULL_SHA = "1234567890abcdef1234567890abcdef12345678"


class CloseoutPrBodyGithubLinksTest(unittest.TestCase):
    def test_pr_body_write_github_mode_creates_clickable_blob_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "github-pr-body")
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
                "github-pr-body",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=FULL_SHA,
            )
            artifact = repo / ".sdf" / "handoffs" / "github-pr-body" / "pr-body.md"
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("not publication-ready", result.stdout)
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/github-pr-body/"
            "evidence.md#acceptance--review-focus)",
            content,
        )
        self.assertEqual(
            content.count(
                "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
                f"{FULL_SHA}/.sdf/evidence/github-pr-body/"
                "evidence.md#acceptance--review-focus)"
            ),
            1,
        )
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/github-pr-body/evidence.md#machine-record)",
            content,
        )
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/github-pr-body/"
            "evidence.md#verification)",
            content,
        )
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/github-pr-body/"
            "evidence.md#guidance-applied)",
            content,
        )
        self.assertNotIn("](.sdf/evidence/github-pr-body/", content)

    def test_pr_body_write_github_mode_requires_repo_and_ref(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "missing-github-options")

            result = run_pr_body_write(
                repo,
                "missing-github-options",
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

    def test_pr_body_write_rejects_malformed_github_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "bad-github-repo")

            result = run_pr_body_write(
                repo,
                "bad-github-repo",
                link_mode="github",
                github_repo="/Users/example/sdf-cli",
                github_ref=FULL_SHA,
            )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("--github-repo must look like owner/name", result.stderr)

    def test_pr_body_check_accepts_valid_github_blob_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "valid-github-pr-body")
            write_pr_body_with_links(
                repo,
                "valid-github-pr-body",
                [github_blob("valid-github-pr-body", "evidence.md")],
            )

            result = run_github_check(repo, "valid-github-pr-body")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("status: ready", result.stdout)
        self.assertNotIn("warning:", result.stdout)
        self.assertNotIn("missing evidence link", result.stdout)
        self.assertNotIn("wrong GitHub evidence link", result.stdout)

    def test_pr_body_check_rejects_wrong_github_repo_or_ref(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "wrong-github-pr-body")
            write_pr_body_with_links(
                repo,
                "wrong-github-pr-body",
                [
                    github_blob(
                        "wrong-github-pr-body",
                        "evidence.md",
                        github_repo="wrong/sdf-cli",
                    ),
                ],
            )

            result = run_github_check(repo, "wrong-github-pr-body")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("missing evidence link: evidence.md", result.stdout)
        self.assertIn(
            "wrong GitHub evidence link: https://github.com/wrong/sdf-cli/blob/",
            result.stdout,
        )

    def test_pr_body_check_rejects_github_blob_link_to_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "broken-github-pr-body")
            write_pr_body_with_links(
                repo,
                "broken-github-pr-body",
                [
                    github_blob("broken-github-pr-body", "missing.md"),
                ],
            )

            result = run_github_check(repo, "broken-github-pr-body")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("missing evidence link: evidence.md", result.stdout)
        self.assertIn(
            "broken evidence link: https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/broken-github-pr-body/missing.md",
            result.stdout,
        )

def write_pr_body_with_links(repo: Path, change_id: str, links: list[str]) -> None:
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
                f"- [Evidence notes]({links[0]})",
            ]
        ),
        encoding="utf-8",
    )


def github_blob(
    change_id: str,
    filename: str,
    *,
    github_repo: str = "acme/sdf-cli",
    github_ref: str = FULL_SHA,
) -> str:
    return (
        f"https://github.com/{github_repo}/blob/{github_ref}/"
        f".sdf/evidence/{change_id}/{filename}"
    )


def run_github_check(repo: Path, change_id: str):
    return run_pr_body_check(
        repo,
        change_id,
        link_mode="github",
        github_repo="acme/sdf-cli",
        github_ref=FULL_SHA,
    )


if __name__ == "__main__":
    unittest.main()
