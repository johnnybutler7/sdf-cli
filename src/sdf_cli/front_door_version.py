"""Front Door release/version identity helpers."""

from __future__ import annotations

from pathlib import Path

from sdf_cli import __version__

FRONT_DOOR_PACKAGE = "software-dark-factory"
FRONT_DOOR_RELEASE = f"v{__version__}"
FRONT_DOOR_VERSION = __version__
UNKNOWN_FRONT_DOOR_RELEASE = "not recorded"


def front_door_package_label() -> str:
    return f"{FRONT_DOOR_PACKAGE} {FRONT_DOOR_VERSION}"


def generated_config_version_lines() -> tuple[str, ...]:
    return (
        f'front_door_release: "{FRONT_DOOR_RELEASE}"',
        f'front_door_package: "{front_door_package_label()}"',
    )


def read_receiver_front_door_config(repo_path: Path) -> dict[str, str]:
    config_path = repo_path / ".sdf" / "config.yml"
    if not config_path.is_file():
        return {}

    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    values: dict[str, str] = {}
    for line in lines:
        key, separator, value = line.partition(":")
        if not separator:
            continue
        key = key.strip()
        if key not in ("front_door_release", "front_door_package"):
            continue
        values[key] = _unquote(value.strip())
    return values


def receiver_front_door_release(repo_path: Path) -> str:
    values = read_receiver_front_door_config(repo_path)
    return values.get("front_door_release") or UNKNOWN_FRONT_DOOR_RELEASE


def receiver_front_door_package(repo_path: Path) -> str:
    values = read_receiver_front_door_config(repo_path)
    return values.get("front_door_package") or front_door_package_label()


def observed_front_door_context(repo_path: Path) -> dict[str, str]:
    values = read_receiver_front_door_config(repo_path)
    release_from_config = values.get("front_door_release")
    return {
        "front_door_release": release_from_config or FRONT_DOOR_RELEASE,
        "front_door_package": (
            values.get("front_door_package") or front_door_package_label()
        ),
        "front_door_release_source": (
            "receiver_config" if release_from_config else "running_sdf_cli"
        ),
    }


def front_door_summary_from_observed(observed: dict[str, str]) -> str:
    release = observed.get("front_door_release", "").strip()
    if not release:
        return ""
    package = observed.get("front_door_package", "").strip()
    source = observed.get("front_door_release_source", "").strip()
    package_part = f" ({package})" if package else ""
    source_part = f", source {source}" if source else ""
    return f"release {release}{package_part}{source_part}"


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
