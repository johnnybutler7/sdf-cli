import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive, write_verification_config

from sdf_cli.main import main


class RepositoryDefaultsTest(unittest.TestCase):
    def test_init_defaults_to_current_directory_and_keeps_external_repo_support(self):
        with tempfile.TemporaryDirectory() as directory:
            current_repo, external_repo = self._repos(directory)

            current_exit_code = self._run_in(current_repo, ["init"])
            with redirect_stdout(io.StringIO()):
                external_exit_code = main(["init", "--repo", str(external_repo)])

            self.assertEqual(current_exit_code, 0)
            self.assertEqual(external_exit_code, 0)
            self.assertTrue((current_repo / ".sdf").is_dir())
            self.assertTrue((external_repo / ".sdf").is_dir())

    def test_start_defaults_to_current_directory_and_keeps_external_repo_support(self):
        with tempfile.TemporaryDirectory() as directory:
            current_repo, external_repo = self._repos(directory)

            current_exit_code = self._run_in(
                current_repo, ["start", "--change-id", "current-repo"]
            )
            with redirect_stdout(io.StringIO()):
                external_exit_code = main(
                    [
                        "start",
                        "--repo",
                        str(external_repo),
                        "--change-id",
                        "external-repo",
                    ]
                )

            self.assertEqual(current_exit_code, 0)
            self.assertEqual(external_exit_code, 0)
            self.assertTrue(
                (current_repo / ".sdf" / "evidence" / "current-repo").is_dir()
            )
            self.assertTrue(
                (external_repo / ".sdf" / "evidence" / "external-repo").is_dir()
            )

    def test_close_defaults_to_current_directory_and_keeps_external_repo_support(self):
        with tempfile.TemporaryDirectory() as directory:
            current_repo, external_repo = self._repos(directory)
            self._run_in(current_repo, ["init"])
            with redirect_stdout(io.StringIO()):
                main(["init", "--repo", str(external_repo)])
            for repo, change_id in (
                (current_repo, "current-repo"),
                (external_repo, "external-repo"),
            ):
                write_archive(repo, change_id)
                write_verification_config(
                    repo,
                    """
version: 1
commands:
  - name: ok
    command: python3 -c \"print('ok')\"
""",
                )

            current_exit_code = self._run_in(
                current_repo, ["close", "--change-id", "current-repo"]
            )
            with redirect_stdout(io.StringIO()):
                external_exit_code = main(
                    [
                        "close",
                        "--repo",
                        str(external_repo),
                        "--change-id",
                        "external-repo",
                    ]
                )

            self.assertEqual(current_exit_code, 0)
            self.assertEqual(external_exit_code, 0)
            self.assertTrue(
                (
                    current_repo
                    / ".sdf"
                    / "handoffs"
                    / "current-repo"
                    / "pr-body.md"
                ).is_file()
            )
            self.assertTrue(
                (
                    external_repo
                    / ".sdf"
                    / "handoffs"
                    / "external-repo"
                    / "pr-body.md"
                ).is_file()
            )

    def test_close_help_is_safe_and_keeps_advanced_options_discoverable(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["close", "--help"])

        self.assertEqual(raised.exception.code, 0)
        help_text = stdout.getvalue()
        normalized_help = " ".join(help_text.split())
        self.assertIn("usage: sdf close", help_text)
        self.assertIn("sdf close --change-id <change-id>", help_text)
        self.assertIn("Defaults to the current directory", normalized_help)
        self.assertIn("Optional declared model identity", help_text)
        self.assertIn(
            "literal unknown is acceptable when genuinely unknown",
            normalized_help,
        )
        self.assertNotIn("git add <change and evidence>", help_text)
        self.assertIn("Commit the change and evidence before refreshing", help_text)
        self.assertIn("--overwrite", help_text)
        self.assertIn("--refresh-handoff", help_text)
        self.assertIn("--link-mode", help_text)
        self.assertIn("--github-ref", help_text)

    def _repos(self, directory: str) -> tuple[Path, Path]:
        current_repo = Path(directory) / "current"
        external_repo = Path(directory) / "external"
        current_repo.mkdir()
        external_repo.mkdir()
        return current_repo, external_repo

    def _run_in(self, repo: Path, argv: list[str]) -> int:
        original_cwd = Path.cwd()
        try:
            os.chdir(repo)
            with redirect_stdout(io.StringIO()):
                return main(argv)
        finally:
            os.chdir(original_cwd)
