"""Timing rendering helpers for verification output."""

from __future__ import annotations

from sdf_cli.verification_formatting import format_duration
from sdf_cli.verification_results import VerificationCommandResult


def duration_suffix(command: VerificationCommandResult) -> str:
    if command.duration_seconds is None:
        return ""
    suffix = f" in {format_duration(command.duration_seconds)}"
    if command.track_timing:
        suffix = f"{suffix} (tracked timing)"
    return suffix


def terminal_tracked_timing_lines(
    command_results: tuple[VerificationCommandResult, ...],
) -> list[str]:
    tracked = _tracked_commands(command_results)
    if not tracked:
        return []
    return ["Tracked timings:", *[_timing_line(command, "") for command in tracked]]


def markdown_tracked_timing_lines(
    command_results: tuple[VerificationCommandResult, ...],
) -> list[str]:
    tracked = _tracked_commands(command_results)
    if not tracked:
        return []
    return [
        "",
        "## Tracked Timings",
        "",
        *[_timing_line(command, ".") for command in tracked],
    ]


def _tracked_commands(
    command_results: tuple[VerificationCommandResult, ...],
) -> list[VerificationCommandResult]:
    return [command for command in command_results if command.track_timing]


def _timing_line(command: VerificationCommandResult, ending: str) -> str:
    if command.duration_seconds is None:
        return f"- {command.name}: not measured{ending}"
    return f"- {command.name}: {format_duration(command.duration_seconds)}{ending}"
