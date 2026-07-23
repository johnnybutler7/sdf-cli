"""Execute configured SDF verification commands."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import TextIO

from sdf_cli.config.verification import load_verification_config
from sdf_cli.verification_command_execution import (
    CommandExecutor,
    MonotonicClock,
    commands_to_run,
    run_command,
    run_shell_command,
)
from sdf_cli.verification_placeholder import is_starter_verification_placeholder
from sdf_cli.verification_results import (
    VerificationCommandResult,
    VerificationRunResult,
)


def run_verification(
    repo_path: Path,
    *,
    repo_label: str | None = None,
    focused_name: str | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    executor: CommandExecutor | None = None,
    clock: MonotonicClock | None = None,
) -> VerificationRunResult:
    output = stdout if stdout is not None else sys.stdout
    error_output = stderr if stderr is not None else sys.stderr
    command_executor = executor if executor is not None else run_shell_command
    monotonic_clock = clock if clock is not None else time.monotonic
    config_path = repo_path / ".sdf" / "verification.yml"
    config = load_verification_config(config_path)

    if not config.valid:
        error = config.error or "verification config is invalid"
        print(f"Verification was not run: {error}", file=error_output)
        return VerificationRunResult(
            repo_path=repo_path,
            config_path=config_path,
            status="config_invalid",
            exit_code=1,
            command_results=(),
            repo_label=repo_label,
            focused_name=focused_name,
            error=error,
        )

    commands, error = commands_to_run(
        config.commands,
        config.focused_subsets,
        focused_name,
    )
    if error is not None:
        print(f"Verification was not run: {error}", file=error_output)
        return VerificationRunResult(
            repo_path=repo_path,
            config_path=config_path,
            status="focused_invalid",
            exit_code=1,
            command_results=(),
            repo_label=repo_label,
            focused_name=focused_name,
            error=error,
        )

    if focused_name is not None:
        print(
            f"Focused verification run: {focused_name}",
            file=output,
            flush=True,
        )
        print(
            "Focused verification is supporting feedback only; full closeout "
            "gate remains: sdf verify --repo PATH",
            file=output,
            flush=True,
        )

    results: list[VerificationCommandResult] = []
    for command in commands:
        result = run_command(
            command,
            repo_path,
            command_executor,
            monotonic_clock,
            output,
            error_output,
        )
        results.append(result)
        if not result.passed and result.required:
            if is_starter_verification_placeholder(command):
                _print_starter_placeholder_failure_note(
                    error_output,
                    repo_label or str(repo_path),
                )
            message = (
                "Required verification command failed; execution stopped: "
                f"{result.name}"
            )
            print(message, file=error_output)
            return VerificationRunResult(
                repo_path=repo_path,
                config_path=config_path,
                status="failed",
                exit_code=1,
                command_results=tuple(results),
                repo_label=repo_label,
                focused_name=focused_name,
                error=message,
            )

    return VerificationRunResult(
        repo_path=repo_path,
        config_path=config_path,
        status="passed",
        exit_code=0,
        command_results=tuple(results),
        repo_label=repo_label,
        focused_name=focused_name,
    )


def _print_starter_placeholder_failure_note(stderr: TextIO, repo_label: str) -> None:
    print(
        "\n".join(
            (
                "Receiver verification placeholder failed intentionally:",
                "- Replace it in .sdf/verification.yml with receiver-owned commands.",
                "- Then rerun:",
                f"  sdf verify --repo {repo_label}",
            )
        ),
        file=stderr,
        end="\n\n",
    )
