"""Verification config parsing for ``.sdf/verification.yml``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VerificationCommand:
    name: str
    command: str
    required: bool
    track_timing: bool = False


@dataclass(frozen=True)
class FocusedVerificationSubset:
    name: str
    commands: tuple[str, ...]


@dataclass(frozen=True)
class VerificationConfig:
    path: Path
    present: bool
    valid: bool
    commands: tuple[VerificationCommand, ...]
    focused_subsets: tuple[FocusedVerificationSubset, ...] = ()
    visibility_issues: tuple[str, ...] = ()
    error: str | None = None


def load_verification_config(path: Path) -> VerificationConfig:
    from sdf_cli.config.verification_parser import parse_verification_lines

    if not path.is_file():
        return VerificationConfig(
            path=path,
            present=False,
            valid=False,
            commands=(),
            error="verification config is missing",
        )

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return _invalid(path, f"verification config is unreadable: {error}")

    (
        commands,
        focused_subsets,
        visibility_issues,
        error,
    ) = parse_verification_lines(lines)
    if error is not None:
        return _invalid(path, f"could not parse {path}: {error}")
    return VerificationConfig(
        path=path,
        present=True,
        valid=True,
        commands=commands,
        focused_subsets=focused_subsets,
        visibility_issues=visibility_issues,
    )


def _invalid(path: Path, error: str) -> VerificationConfig:
    return VerificationConfig(
        path=path,
        present=True,
        valid=False,
        commands=(),
        error=error,
    )
