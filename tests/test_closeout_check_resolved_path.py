import io
import os
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import Iterator

from tests.test_closeout_check_command import (
    run_closeout,
    write_archive,
    write_verification_config,
)


class CloseoutCheckResolvedPathTest(unittest.TestCase):
    def test_current_repo_reports_resolved_repository_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory).resolve()
            write_archive(repo, "current-repo-path")
            write_passing_verification_config(repo)
            stdout = io.StringIO()

            with chdir(repo), redirect_stdout(stdout):
                exit_code = run_closeout(Path("."), "current-repo-path")

        self.assertEqual(exit_code, 0)
        self.assertIn(f"- Resolved repository path: {repo}", stdout.getvalue())

    def test_relative_repo_reports_resolved_repository_path(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            repo = parent / "nested-repo"
            repo.mkdir()
            write_archive(repo, "relative-repo-path")
            write_passing_verification_config(repo)
            stdout = io.StringIO()

            with chdir(parent), redirect_stdout(stdout):
                exit_code = run_closeout(Path("nested-repo"), "relative-repo-path")

        self.assertEqual(exit_code, 0)
        self.assertIn(f"- Resolved repository path: {repo}", stdout.getvalue())


def write_passing_verification_config(repo: Path) -> None:
    write_verification_config(
        repo,
        """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
    )


@contextmanager
def chdir(path: Path) -> Iterator[None]:
    original_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
