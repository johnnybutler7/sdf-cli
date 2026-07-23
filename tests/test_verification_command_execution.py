import tempfile
import unittest
from pathlib import Path

from sdf_cli.verification_command_execution import run_shell_command


class VerificationCommandExecutionTest(unittest.TestCase):
    def test_shell_command_uses_selected_repo_and_captures_output(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "repo-marker.txt").write_text("present", encoding="utf-8")

            completed = run_shell_command(
                "python3 -c \"import pathlib, sys; "
                "print(pathlib.Path('repo-marker.txt').read_text()); "
                "print('warning', file=sys.stderr)\"",
                repo,
            )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "present\n")
        self.assertEqual(completed.stderr, "warning\n")


if __name__ == "__main__":
    unittest.main()
