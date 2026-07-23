"""Shared formatting helpers for verification result renderers."""

from __future__ import annotations

from sdf_cli.verification_results import VerificationCommandResult


def format_duration(duration_seconds: float) -> str:
    if duration_seconds < 60:
        return f"{duration_seconds:.2f}s"
    minutes = int(duration_seconds // 60)
    seconds = duration_seconds - (minutes * 60)
    return f"{minutes}m {seconds:.2f}s"


def status_label(command: VerificationCommandResult) -> str:
    if command.status == "optional_failed":
        return "optional failed"
    return command.status
