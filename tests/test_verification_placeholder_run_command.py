import io
import os
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.receiver_scaffold_content import (
    STARTER_VERIFICATION_PLACEHOLDER_COMMAND,
    STARTER_VERIFICATION_PLACEHOLDER_NAME,
)


class VerificationPlaceholderRunCommandTest(unittest.TestCase):
    def test_local_placeholder_failure_rerun_guidance_preserves_dot_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                f"""
version: 1
commands:
  - name: {STARTER_VERIFICATION_PLACEHOLDER_NAME}
    command: "{STARTER_VERIFICATION_PLACEHOLDER_COMMAND}"
    required: true
  - name: skipped
    command: python3 -c "print('skipped')"
""",
            )
            before_files = repo_files(repo)
            stdout = io.StringIO()
            stderr = io.StringIO()

            with chdir(repo), redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", "."])

            self.assertEqual(exit_code, 1)
            self.assertIn(
                f"FAIL {STARTER_VERIFICATION_PLACEHOLDER_NAME}",
                stdout.getvalue(),
            )
            self.assertNotIn("skipped", stdout.getvalue())
            self.assertIn(
                "Receiver verification placeholder failed intentionally:",
                stderr.getvalue(),
            )
            self.assertIn("  sdf verify --repo .", stderr.getvalue())
            self.assertIn(
                "Next: fix the failing check, then rerun "
                "`sdf verify --repo .`.",
                stdout.getvalue(),
            )
            self.assertEqual(before_files, repo_files(repo))
            self.assert_no_automation_outputs(repo)

    def test_external_placeholder_failure_rerun_guidance_preserves_repo_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                f"""
version: 1
commands:
  - name: {STARTER_VERIFICATION_PLACEHOLDER_NAME}
    command: "{STARTER_VERIFICATION_PLACEHOLDER_COMMAND}"
    required: true
  - name: skipped
    command: python3 -c "print('skipped')"
""",
            )
            before_files = repo_files(repo)
            stdout = io.StringIO()
            stderr = io.StringIO()
            repo_arg = str(repo)

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", repo_arg])

            self.assertEqual(exit_code, 1)
            self.assertIn(
                f"FAIL {STARTER_VERIFICATION_PLACEHOLDER_NAME}",
                stdout.getvalue(),
            )
            self.assertNotIn("skipped", stdout.getvalue())
            self.assertIn(
                "Receiver verification placeholder failed intentionally:",
                stderr.getvalue(),
            )
            self.assertIn(
                "- Replace it in .sdf/verification.yml with receiver-owned commands.",
                stderr.getvalue(),
            )
            self.assertIn(
                f"  sdf verify --repo {repo_arg}",
                stderr.getvalue(),
            )
            self.assertIn(
                f"  sdf verify --repo {repo_arg}\n\n"
                "Required verification command failed; execution stopped: "
                f"{STARTER_VERIFICATION_PLACEHOLDER_NAME}",
                stderr.getvalue(),
            )
            self.assertIn(
                "Next: fix the failing check, then rerun "
                f"`sdf verify --repo {repo_arg}`.",
                stdout.getvalue(),
            )
            self.assertIn(
                "Required verification command failed; execution stopped: "
                f"{STARTER_VERIFICATION_PLACEHOLDER_NAME}",
                stderr.getvalue(),
            )
            self.assertEqual(before_files, repo_files(repo))
            self.assert_no_automation_outputs(repo)

    def test_non_placeholder_required_failure_does_not_show_handoff_note(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                f"""
version: 1
commands:
  - name: {STARTER_VERIFICATION_PLACEHOLDER_NAME}
    command: python3 -c "import sys; sys.exit(1)"
""",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", str(repo)])

        self.assertEqual(exit_code, 1)
        self.assertNotIn(
            "Receiver verification placeholder failed intentionally:",
            stderr.getvalue(),
        )

    def assert_no_automation_outputs(self, repo: Path) -> None:
        self.assertFalse((repo / ".sdf" / "evidence").exists())
        self.assertFalse((repo / "PULL_REQUEST_BODY.md").exists())
        self.assertFalse((repo / ".github" / "pull_request_template.md").exists())


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


def repo_files(repo: Path) -> set[Path]:
    return {path.relative_to(repo) for path in repo.rglob("*") if path.is_file()}


@contextmanager
def chdir(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)
