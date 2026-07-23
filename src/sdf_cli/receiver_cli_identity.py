"""Compare a receiver's declared Front Door release with this CLI."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sdf_cli import __version__
from sdf_cli.front_door_version import read_receiver_front_door_config

MATCH = "match"
MISMATCH = "mismatch"
RECEIVER_IDENTITY_UNAVAILABLE = "receiver identity unavailable"
CLI_IDENTITY_UNAVAILABLE = "CLI identity unavailable or unparsable"

_IDENTITY_PATTERN = re.compile(
    r"^(?:software-dark-factory )?v?(?P<version>[0-9]+(?:\.[0-9]+)*"
    r"(?:(?:a|b|rc|post|dev)[0-9]+)?)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReceiverCliIdentityComparison:
    receiver_release: str | None
    cli_version: str | None
    result: str

    @property
    def matches(self) -> bool:
        return self.result == MATCH

    @property
    def mismatches(self) -> bool:
        return self.result == MISMATCH


def compare_receiver_cli_identity(
    repo_path: Path,
    *,
    cli_version: str | None = None,
) -> ReceiverCliIdentityComparison:
    """Return the one canonical receiver/operator identity comparison."""
    receiver_release = read_receiver_front_door_config(repo_path).get(
        "front_door_release"
    )
    active_cli_version = __version__ if cli_version is None else cli_version
    return compare_identity_values(receiver_release, active_cli_version)


def compare_identity_values(
    receiver_release: str | None,
    cli_version: str | None,
) -> ReceiverCliIdentityComparison:
    """Compare explicit identity values, preserving unavailable states."""
    normalized_receiver = _receiver_version(receiver_release)
    normalized_cli = _cli_version(cli_version)
    if normalized_receiver is None:
        return ReceiverCliIdentityComparison(
            receiver_release=_display_value(receiver_release),
            cli_version=_display_value(cli_version),
            result=RECEIVER_IDENTITY_UNAVAILABLE,
        )
    if normalized_cli is None:
        return ReceiverCliIdentityComparison(
            receiver_release=_display_value(receiver_release),
            cli_version=_display_value(cli_version),
            result=CLI_IDENTITY_UNAVAILABLE,
        )
    return ReceiverCliIdentityComparison(
        receiver_release=receiver_release.strip(),
        cli_version=cli_version.strip(),
        result=MATCH if normalized_receiver == normalized_cli else MISMATCH,
    )


def lifecycle_identity_preflight(repo_path: Path) -> str | None:
    """Return a blocking message only for a known version mismatch."""
    comparison = compare_receiver_cli_identity(repo_path)
    if not comparison.mismatches:
        return None
    return (
        "receiver/operator identity mismatch: receiver declares Front Door "
        f"release {comparison.receiver_release}; executing CLI version is "
        f"{comparison.cli_version}. Align the operator CLI with the receiver "
        "before starting or closing lifecycle work."
    )


def _receiver_version(value: str | None) -> str | None:
    return _normalized_identity(value)


def _cli_version(value: str | None) -> str | None:
    return _normalized_identity(value)


def _normalized_identity(value: str | None) -> str | None:
    if value is None:
        return None
    match = _IDENTITY_PATTERN.fullmatch(value.strip())
    if match is None:
        return None
    return match.group("version").lower()


def _display_value(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None
