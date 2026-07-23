"""Read the small governance fields needed by command affordances."""

from __future__ import annotations

from pathlib import Path


def governance_mode(repo_path: Path) -> str | None:
    config_path = repo_path / ".sdf" / "config.yml"
    if not config_path.is_file():
        return None

    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None

    for raw_line in lines:
        if raw_line.startswith((" ", "\t")):
            continue
        key, separator, value = raw_line.partition(":")
        if not separator or key.strip() != "governance_mode":
            continue
        return _unquote(value.strip())
    return None


def governance_required(repo_path: Path) -> bool:
    return governance_mode(repo_path) == "required"


def governance_inactive(repo_path: Path) -> bool:
    return governance_mode(repo_path) == "inactive"


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
