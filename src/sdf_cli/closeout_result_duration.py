"""Duration helpers for structured closeout result records."""

from __future__ import annotations

from sdf_cli.closeout_check import CloseoutCheckResult


def optional_float_value(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return -1.0


def verification_total_duration(result: CloseoutCheckResult) -> float | None:
    durations = [
        command.duration_seconds
        for command in result.verification_result.command_results
        if command.duration_seconds is not None
    ]
    if not durations:
        return None
    return sum(durations)
