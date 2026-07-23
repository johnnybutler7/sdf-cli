"""Select and execute configured verification commands."""

from __future__ import annotations

import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import Protocol, TextIO

from sdf_cli.config.verification import VerificationCommand
from sdf_cli.verification_facts import structured_facts
from sdf_cli.verification_results import VerificationCommandResult, command_status


class CommandExecutor(Protocol):
    def __call__(self, command: str, repo_path: Path) -> CompletedProcess[str]:
        ...


class MonotonicClock(Protocol):
    def __call__(self) -> float:
        ...


def commands_to_run(
    commands: tuple[VerificationCommand, ...],
    focused_subsets,
    focused_name: str | None,
) -> tuple[tuple[VerificationCommand, ...], str | None]:
    """Select the full verification boundary or a named focused subset."""

    if focused_name is None:
        return commands, None

    subset = next(
        (candidate for candidate in focused_subsets if candidate.name == focused_name),
        None,
    )
    if subset is None:
        return (), f"unknown focused verification subset: {focused_name}"

    commands_by_name = {command.name: command for command in commands}
    selected_commands: list[VerificationCommand] = []
    for command_name in subset.commands:
        command = commands_by_name.get(command_name)
        if command is None:
            return (
                (),
                "focused verification subset "
                f"{focused_name} references unknown command: {command_name}",
            )
        selected_commands.append(command)
    return tuple(selected_commands), None


def run_command(
    command: VerificationCommand,
    repo_path: Path,
    executor: CommandExecutor,
    clock: MonotonicClock,
    stdout: TextIO,
    stderr: TextIO,
) -> VerificationCommandResult:
    """Run one configured command and return its structured result."""

    print(f"==> {command.name}: {command.command}", file=stdout, flush=True)
    started_at = clock()
    completed = executor(command.command, repo_path)
    duration_seconds = clock() - started_at
    write_completed_output(completed, stdout, stderr)

    result = VerificationCommandResult(
        name=command.name,
        command=command.command,
        required=command.required,
        exit_code=completed.returncode,
        status=command_status(
            required=command.required,
            exit_code=completed.returncode,
        ),
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration_seconds=duration_seconds,
        track_timing=command.track_timing,
        facts=structured_facts(completed),
    )
    if result.passed:
        print(f"PASS {result.name}", file=stdout, flush=True)
    elif result.required:
        print(f"FAIL {result.name}", file=stdout, flush=True)
    else:
        print(
            f"FAIL {result.name} (optional; execution continued)",
            file=stdout,
            flush=True,
        )
    return result


def run_shell_command(command: str, repo_path: Path) -> CompletedProcess[str]:
    """Run a configured shell command from the selected repository."""

    return subprocess.run(
        command,
        shell=True,
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )


def write_completed_output(
    completed: subprocess.CompletedProcess[str],
    stdout: TextIO,
    stderr: TextIO,
) -> None:
    """Forward captured command output while preserving terminal line endings."""

    if completed.stdout:
        stdout.write(completed.stdout)
        if not completed.stdout.endswith("\n"):
            stdout.write("\n")
        stdout.flush()
    if completed.stderr:
        stderr.write(completed.stderr)
        if not completed.stderr.endswith("\n"):
            stderr.write("\n")
        stderr.flush()
