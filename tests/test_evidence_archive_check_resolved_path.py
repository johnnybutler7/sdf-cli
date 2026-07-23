import os
import tempfile
import unittest
from pathlib import Path

from tests.test_evidence_archive_check import (
    CommandResult,
    run_check,
    write_archive,
)


class EvidenceArchiveCheckResolvedPathTest(unittest.TestCase):
    def test_current_repo_reports_resolved_repository_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory).resolve()
            write_archive(repo, "current-repo-path")

            result = run_check_in_cwd(repo, Path("."), "current-repo-path")

            self.assertEqual(result.exit_code, 0)
            self.assertIn(f"Resolved repository path: {repo}", result.stdout)

    def test_relative_repo_reports_resolved_repository_path(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            repo = parent / "nested-repo"
            repo.mkdir()
            write_archive(repo, "relative-repo-path")

            result = run_check_in_cwd(parent, Path("nested-repo"), "relative-repo-path")

            self.assertEqual(result.exit_code, 0)
            self.assertIn(f"Resolved repository path: {repo}", result.stdout)


def run_check_in_cwd(cwd: Path, repo: Path, change_id: str) -> CommandResult:
    original_cwd = Path.cwd()
    os.chdir(cwd)
    try:
        return run_check(repo, change_id)
    finally:
        os.chdir(original_cwd)
