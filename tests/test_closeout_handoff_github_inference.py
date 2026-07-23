import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_archive,
    write_run_context,
    write_verification_config,
)
from tests.pr_body_command_helpers import run_handoff

FULL_SHA = "1234567890abcdef1234567890abcdef12345678"


class CloseoutHandoffGithubInferenceTest(unittest.TestCase):
    def test_handoff_infers_github_blob_links_from_origin_and_head_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head_sha = configure_git_context(
                repo,
                remote_url="git@github.com:acme/sdf-cli.git",
                branch="feature/published-links",
            )
            write_archive(
                repo,
                "inferred-github-pr-body",
                playbook_applied_lines=["- Python CLI design playbook."],
            )
            write_run_context(repo, "inferred-github-pr-body")
            write_passing_verification(repo)

            result = run_handoff(repo, "inferred-github-pr-body")
            artifact = (
                repo
                / ".sdf"
                / "handoffs" / "inferred-github-pr-body" / "pr-body.md"
            )
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("not publication-ready", result.stdout)
        for fragment in (
            "#acceptance--review-focus",
            "#machine-record",
            "#guidance-applied",
            "#verification",
        ):
            self.assertIn(
                "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
                f"{head_sha}/.sdf/evidence/"
                f"inferred-github-pr-body/evidence.md{fragment})",
                content,
            )
        self.assertNotIn("](.sdf/evidence/", content)

    def test_handoff_keeps_relative_links_when_github_context_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "offline-pr-body")
            write_passing_verification(repo)

            result = run_handoff(repo, "offline-pr-body")
            artifact = repo / ".sdf" / "handoffs" / "offline-pr-body" / "pr-body.md"
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("not publication-ready", result.stdout)
        self.assertIn(
            "[Evidence notes](.sdf/evidence/offline-pr-body/"
            "evidence.md#acceptance--review-focus)",
            content,
        )
        self.assertNotIn("https://github.com/", content)

    def test_handoff_explicit_github_mode_uses_supplied_repo_and_ref(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            configure_git_context(
                repo,
                remote_url="git@github.com:ignored/repo.git",
                branch="ignored-branch",
            )
            write_archive(repo, "explicit-github-pr-body")
            write_passing_verification(repo)

            result = run_handoff(
                repo,
                "explicit-github-pr-body",
                link_mode="github",
                github_repo="acme/sdf-cli",
                github_ref=FULL_SHA,
            )
            artifact = (
                repo
                / ".sdf"
                / "handoffs" / "explicit-github-pr-body" / "pr-body.md"
            )
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("not publication-ready", result.stdout)
        self.assertIn(
            "[Evidence notes](https://github.com/acme/sdf-cli/blob/"
            f"{FULL_SHA}/.sdf/evidence/"
            "explicit-github-pr-body/evidence.md#acceptance--review-focus)",
            content,
        )
        self.assertNotIn("https://github.com/ignored/repo/blob/", content)


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


if __name__ == "__main__":
    unittest.main()
