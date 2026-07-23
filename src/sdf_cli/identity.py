"""Read-only runtime identity reporting for the executing SDF CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from urllib.parse import unquote, urlparse

import sdf_cli
from sdf_cli import __version__
from sdf_cli.evidence_archive_contract import EVIDENCE_ARCHIVE_CONTRACT_VERSION

UNKNOWN = "unknown"
UNAVAILABLE = "unavailable"


def render_identity() -> str:
    """Render deterministic facts about the currently imported implementation."""
    package_file = Path(sdf_cli.__file__).resolve()
    package_location = package_file.parent
    installation_mode, editable_location = _installation_identity(package_location)
    repository_root, commit = _git_identity(package_location)
    values = (
        ("package_version", __version__),
        ("executable_location", str(Path(sys.argv[0]).resolve())),
        ("imported_package_location", str(package_location)),
        ("installation_mode", installation_mode),
        ("editable_project_location", editable_location),
        ("evidence_contract_version", str(EVIDENCE_ARCHIVE_CONTRACT_VERSION)),
        ("git_repository_root", repository_root),
        ("git_commit", commit),
    )
    return _render_identity(values)


def _render_identity(values: tuple[tuple[str, str], ...]) -> str:
    lines = ("SDF CLI identity", *(f"{key}: {value}" for key, value in values))
    return "\n".join(lines)


def _installation_identity(
    package_location: Path | None = None,
) -> tuple[str, str]:
    try:
        distribution = metadata.distribution("software-dark-factory")
    except metadata.PackageNotFoundError:
        return "source-checkout", UNAVAILABLE

    direct_url = distribution.read_text("direct_url.json")
    if direct_url is None:
        differs_from_import = (
            package_location is not None
            and _distribution_location(distribution) != package_location
        )
        if differs_from_import:
            return "source-checkout", UNAVAILABLE
        return "installed", UNAVAILABLE
    try:
        payload = json.loads(direct_url)
    except json.JSONDecodeError:
        return UNKNOWN, UNAVAILABLE
    if not payload.get("dir_info", {}).get("editable"):
        return "installed", UNAVAILABLE
    location = _file_url_path(payload.get("url"))
    return "editable", str(location) if location is not None else UNKNOWN


def _distribution_location(distribution: metadata.Distribution) -> Path | None:
    try:
        return Path(distribution.locate_file("sdf_cli")).resolve()
    except (AttributeError, TypeError):
        return None


def _file_url_path(value: object) -> Path | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    if parsed.scheme != "file":
        return None
    return Path(unquote(parsed.path)).resolve()


def _git_identity(package_location: Path) -> tuple[str, str]:
    repository_root = _git_output(package_location, "rev-parse", "--show-toplevel")
    if repository_root is None:
        return UNAVAILABLE, UNAVAILABLE
    commit = _git_output(package_location, "rev-parse", "HEAD")
    return repository_root, commit or UNAVAILABLE


def _git_output(location: Path, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ("git", "-C", str(location), *arguments),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None
