import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.closeout_summary_fixtures import write_archive, write_verification_config
from tests.pr_body_command_helpers import run_pr_body_check, run_pr_body_write

from sdf_cli.pr_body_github_context import infer_current_pr_ref


class CloseoutPrBodyGithubInferenceTest(unittest.TestCase):
    def test_workflow_merge_sha_does_not_override_target_repository_head(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head_sha = configure_git_context(
                repo,
                remote_url="git@github.com:acme/sdf-cli.git",
                branch="feature/repository-head-wins",
            )

            with patch.dict(
                os.environ,
                {
                    "GITHUB_SHA": "f" * 40,
                    "GITHUB_PR_HEAD_SHA": "e" * 40,
                },
            ):
                inferred_ref = infer_current_pr_ref(str(repo))

        self.assertNotEqual(head_sha, "f" * 40)
        self.assertEqual(inferred_ref, head_sha)

    def test_explicit_hosted_pr_head_variable_is_used_without_local_head(self):
        with tempfile.TemporaryDirectory() as directory:
            hosted_head_sha = "e" * 40
            with patch.dict(
                os.environ,
                {
                    "GITHUB_SHA": "f" * 40,
                    "GITHUB_PR_HEAD_SHA": hosted_head_sha,
                },
            ):
                inferred_ref = infer_current_pr_ref(directory)

        self.assertEqual(inferred_ref, hosted_head_sha)

    def test_pr_body_write_infers_github_links_from_origin_and_head_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head_sha = configure_git_context(
                repo,
                remote_url="git@github.com:acme/sdf-cli.git",
                branch="feature/inferred-pr-body-links",
            )
            write_archive(repo, "inferred-github-pr-body")
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "inferred-github-pr-body")
            artifact = repo / ".sdf/handoffs/inferred-github-pr-body/pr-body.md"
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("not publication-ready", result.stdout)
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{head_sha}/.sdf/evidence/"
            "inferred-github-pr-body/evidence.md#acceptance--review-focus)",
            content,
        )
        self.assertNotIn("](.sdf/evidence/inferred-github-pr-body/", content)

    def test_pr_body_write_overwrite_keeps_inferred_github_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head_sha = configure_git_context(
                repo,
                remote_url="git@github.com:acme/sdf-cli.git",
                branch="feature/no-link-downgrade",
            )
            write_archive(repo, "no-link-downgrade")
            write_passing_verification(repo)

            first_result = run_pr_body_write(repo, "no-link-downgrade")
            second_result = run_pr_body_write(
                repo,
                "no-link-downgrade",
                overwrite=True,
            )
            check_result = run_pr_body_check(repo, "no-link-downgrade")
            artifact = repo / ".sdf/handoffs/no-link-downgrade/pr-body.md"
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(first_result.exit_code, 0)
        self.assertEqual(second_result.exit_code, 0)
        self.assertEqual(check_result.exit_code, 0)
        self.assertIn("status: overwritten", second_result.stdout)
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{head_sha}/.sdf/evidence/no-link-downgrade/"
            "evidence.md#acceptance--review-focus)",
            content,
        )
        self.assertNotIn("](.sdf/evidence/no-link-downgrade/", content)
        self.assertNotIn(
            "repo-relative evidence link in GitHub mode",
            check_result.stdout,
        )

    def test_pr_body_write_explicit_repo_relative_mode_keeps_local_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            configure_git_context(
                repo,
                remote_url="git@github.com:acme/sdf-cli.git",
                branch="feature/local-links",
            )
            write_archive(repo, "explicit-local-pr-body")
            write_passing_verification(repo)

            result = run_pr_body_write(
                repo,
                "explicit-local-pr-body",
                link_mode="repo-relative",
            )
            artifact = repo / ".sdf/handoffs/explicit-local-pr-body/pr-body.md"
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("warning:", result.stdout)
        self.assertIn(
            "[Evidence notes](.sdf/evidence/explicit-local-pr-body/"
            "evidence.md#acceptance--review-focus)",
            content,
        )
        self.assertNotIn("https://github.com/", content)

    def test_pr_body_check_infers_github_context_and_rejects_relative_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            configure_git_context(
                repo,
                remote_url="git@github.com:acme/sdf-cli.git",
                branch="feature/check-link-downgrade",
            )
            write_archive(repo, "relative-link-downgrade")
            write_pr_body_with_links(
                repo,
                "relative-link-downgrade",
                [
                    ".sdf/evidence/relative-link-downgrade/evidence.md",
                ],
            )

            result = run_pr_body_check(repo, "relative-link-downgrade")

        self.assertEqual(result.exit_code, 1)
        self.assertNotIn("warning:", result.stdout)
        self.assertIn(
            "repo-relative evidence link in GitHub mode: "
            ".sdf/evidence/relative-link-downgrade/evidence.md",
            result.stdout,
        )


def configure_git_context(repo: Path, *, remote_url: str, branch: str) -> str:
    run_git(repo, "init")
    run_git(repo, "checkout", "-b", branch)
    run_git(
        repo,
        "-c",
        "user.name=SDF Test",
        "-c",
        "user.email=sdf-test@example.invalid",
        "commit",
        "--allow-empty",
        "-m",
        "fixture head",
    )
    run_git(repo, "remote", "add", "origin", remote_url)
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def write_passing_verification(repo: Path) -> None:
    write_verification_config(
        repo,
        """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
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


if __name__ == "__main__":
    unittest.main()
