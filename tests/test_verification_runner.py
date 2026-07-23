import subprocess
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from sdf_cli.verification_runner import run_verification


class VerificationRunnerTest(unittest.TestCase):
    def test_passing_commands_exit_zero_in_configured_order(self):
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
""",
            )
            seen: list[str] = []

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor(seen),
                clock=stepping_clock([10.0, 10.25, 20.0, 21.5]),
            )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.status, "passed")
        self.assertEqual(result.repo_path, repo)
        self.assertEqual(result.config_path, repo / ".sdf" / "verification.yml")
        self.assertEqual(seen, ["first command", "second command"])
        self.assertEqual(
            tuple(command.name for command in result.command_results),
            ("first", "second"),
        )
        self.assertEqual(
            tuple(command.duration_seconds for command in result.command_results),
            (0.25, 1.5),
        )
        self.assertEqual(
            tuple(command.track_timing for command in result.command_results),
            (False, False),
        )

    def test_track_timing_metadata_is_preserved_on_results(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: tracked
    command: tracked command
    track_timing: true
  - name: incidental
    command: incidental command
""",
            )

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor([]),
            )

        self.assertEqual(
            tuple(command.track_timing for command in result.command_results),
            (True, False),
        )

    def test_focused_subsets_do_not_change_full_verification_run(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: full-boundary
    command: full command
focused:
  - name: fast-feedback
    commands:
      - full-boundary
      - not-a-runner-command
""",
            )
            seen: list[str] = []

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor(seen),
            )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(seen, ["full command"])
        self.assertEqual(
            tuple(command.name for command in result.command_results),
            ("full-boundary",),
        )

    def test_required_failure_stops_subsequent_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: fails
    command: fail
  - name: skipped
    command: skipped
""",
            )
            seen: list[str] = []

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor(seen),
            )

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.status, "failed")
        self.assertEqual(seen, ["fail"])
        self.assertEqual(result.command_results[0].status, "failed")
        self.assertEqual(
            result.error,
            "Required verification command failed; execution stopped: fails",
        )

    def test_optional_failure_continues_and_can_exit_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: optional-check
    command: fail
    required: false
  - name: required-check
    command: pass
""",
            )
            seen: list[str] = []

            result = run_verification(
                repo,
                stdout=StringIO(),
                stderr=StringIO(),
                executor=recording_executor(seen),
            )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.status, "passed")
        self.assertEqual(seen, ["fail", "pass"])
        self.assertEqual(result.command_results[0].status, "optional_failed")
        self.assertEqual(result.command_results[1].status, "passed")

    def test_missing_config_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_verification(Path(directory), stderr=StringIO())

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.status, "config_invalid")
        self.assertEqual(
            result.config_path,
            Path(directory) / ".sdf" / "verification.yml",
        )
        self.assertEqual(result.error, "verification config is missing")

    def test_invalid_config_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(repo, "version: 1\ncommands: []\n")

            result = run_verification(repo, stderr=StringIO())

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.status, "config_invalid")
        self.assertEqual(
            result.error,
            f"could not parse {result.config_path}: "
            "verification config commands must not be empty",
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
            returncode=1 if command == "fail" else 0,
            stdout="",
            stderr="",
        )

    return execute


def stepping_clock(times: list[float]):
    values = iter(times)

    def current_time() -> float:
        return next(values)

    return current_time

if __name__ == "__main__":
    unittest.main()
