import subprocess
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from sdf_cli.verification_runner import run_verification


class VerificationRunnerResultModelTest(unittest.TestCase):
    def test_successful_run_result_includes_paths_and_status(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: ok
""",
            )

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=output_executor(returncode=0),
            )

        self.assertEqual(result.repo_path, repo)
        self.assertEqual(result.config_path, repo / ".sdf" / "verification.yml")
        self.assertEqual(result.status, "passed")
        self.assertEqual(result.exit_code, 0)

    def test_command_result_includes_structured_execution_details(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: inspectable
    command: inspect
    required: false
""",
            )

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=output_executor(
                    returncode=0,
                    stdout="captured stdout\n",
                    stderr="captured stderr\n",
                ),
            )

        command_result = result.command_results[0]
        self.assertEqual(command_result.name, "inspectable")
        self.assertEqual(command_result.command, "inspect")
        self.assertFalse(command_result.required)
        self.assertEqual(command_result.exit_code, 0)
        self.assertEqual(command_result.status, "passed")
        self.assertEqual(command_result.stdout, "captured stdout\n")
        self.assertEqual(command_result.stderr, "captured stderr\n")


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir()
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


def output_executor(
    *,
    returncode: int,
    stdout: str = "",
    stderr: str = "",
):
    def execute(command: str, repo_path: Path):
        return subprocess.CompletedProcess(
            args=command,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )

    return execute


if __name__ == "__main__":
    unittest.main()
