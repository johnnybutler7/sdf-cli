import subprocess
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from sdf_cli.verification_runner import run_verification


class VerificationFocusedRunnerTest(unittest.TestCase):
    def test_focused_subset_runs_referenced_commands_in_subset_order(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: first
    command: first command
  - name: second
    command: second command
focused:
  - name: fast-feedback
    commands:
      - second
      - first
""",
            )
            seen: list[str] = []

            result = run_verification(
                repo,
                focused_name="fast-feedback",
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor(seen),
            )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.focused_name, "fast-feedback")
        self.assertEqual(seen, ["second command", "first command"])
        self.assertEqual(
            tuple(command.name for command in result.command_results),
            ("second", "first"),
        )

    def test_unknown_focused_subset_exits_one_without_running_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: unit
    command: unit command
""",
            )
            seen: list[str] = []
            stderr = StringIO()

            result = run_verification(
                repo,
                focused_name="missing",
                stdout=StringIO(),
                stderr=stderr,
                executor=recording_executor(seen),
            )

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.status, "focused_invalid")
        self.assertEqual(seen, [])
        self.assertEqual(result.error, "unknown focused verification subset: missing")
        self.assertIn("Verification was not run", stderr.getvalue())

    def test_unknown_focused_command_reference_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: unit
    command: unit command
focused:
  - name: fast-feedback
    commands:
      - missing-command
""",
            )
            seen: list[str] = []

            result = run_verification(
                repo,
                focused_name="fast-feedback",
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor(seen),
            )

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(seen, [])
        self.assertEqual(
            result.error,
            "focused verification subset fast-feedback references unknown "
            "command: missing-command",
        )


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir()
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


def recording_executor(commands: list[str]):
    def execute(command: str, repo_path: Path):
        commands.append(command)
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    return execute


if __name__ == "__main__":
    unittest.main()
