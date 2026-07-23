"""Supplied-wheel inspection helpers for the test-only lifecycle rehearsal."""

from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path


class LifecycleRehearsalError(RuntimeError):
    """Raised when a supplied wheel does not produce its expected identity."""


@dataclass(frozen=True)
class WheelArtifact:
    path: Path
    version: str
    sha256: str


def inspect_wheel(value: str | Path) -> WheelArtifact:
    path = Path(value).expanduser()
    if path.suffix != ".whl" or not path.is_file():
        raise LifecycleRehearsalError(
            f"Supplied wheel must be a local .whl file: {value}"
        )
    path = path.resolve()
    try:
        with zipfile.ZipFile(path) as archive:
            metadata_names = [
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_names) != 1:
                raise LifecycleRehearsalError(
                    f"Supplied wheel has {len(metadata_names)} METADATA files: {path}"
                )
            metadata = archive.read(metadata_names[0]).decode("utf-8")
    except zipfile.BadZipFile as error:
        raise LifecycleRehearsalError(
            f"Supplied wheel is not a valid wheel archive: {path}"
        ) from error
    values = key_values(metadata)
    if values.get("Name") != "software-dark-factory" or not values.get("Version"):
        raise LifecycleRehearsalError(
            "Supplied wheel is not a software-dark-factory wheel with a version: "
            f"{path}"
        )
    return WheelArtifact(path, values["Version"], sha256(path))


def key_values(text: str) -> dict[str, str]:
    return dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)


def yaml_value(contents: str, key: str) -> str | None:
    prefix = f"{key}: "
    for line in contents.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip().strip('"')
    return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
    except ValueError:
        return False
    return True
