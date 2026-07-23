"""Structured results for verification command execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

VerificationFactValue = Union[str, int, float, bool]



@dataclass(frozen=True)
class VerificationCommandResult:
    name: str
    command: str
    required: bool
    exit_code: int
    status: str
    stdout: str
    stderr: str
    duration_seconds: float | None = None
    track_timing: bool = False
    facts: tuple[tuple[str, VerificationFactValue], ...] = ()

    @property
    def passed(self) -> bool:
        return self.status == "passed"


@dataclass(frozen=True)
class VerificationRunResult:
    repo_path: Path
    config_path: Path
    status: str
    exit_code: int
    command_results: tuple[VerificationCommandResult, ...]
    repo_label: str | None = None
    focused_name: str | None = None
    error: str | None = None
    recorded_check_count: int | None = None
    recorded_duration_seconds: float | None = None


def command_status(*, required: bool, exit_code: int) -> str:
    if exit_code == 0:
        return "passed"
    if required:
        return "failed"
    return "optional_failed"
