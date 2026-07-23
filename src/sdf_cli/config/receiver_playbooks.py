"""Parse receiver playbook declarations from SDF config files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReceiverPlaybookConfig:
    name: str
    path: str
    categories: tuple[str, ...]


@dataclass(frozen=True)
class ReceiverPlaybook:
    name: str
    path: str
    categories: tuple[str, ...]
    present: bool


def find_receiver_playbooks(repo_path: Path) -> tuple[ReceiverPlaybook, ...]:
    config_path = repo_path / ".sdf" / "config.yml"
    playbooks = parse_receiver_playbooks(config_path)
    return tuple(
        ReceiverPlaybook(
            name=playbook.name,
            path=playbook.path,
            categories=playbook.categories,
            present=(repo_path / playbook.path).is_file(),
        )
        for playbook in playbooks
    )


def parse_receiver_playbooks(config_path: Path) -> tuple[ReceiverPlaybookConfig, ...]:
    if not config_path.is_file():
        return ()

    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()

    start = _receiver_playbooks_start(lines)
    if start is None:
        return ()

    playbooks: list[ReceiverPlaybookConfig] = []
    current: dict[str, str | list[str]] | None = None
    in_categories = False

    for raw_line in lines[start + 1 :]:
        if raw_line and not raw_line.startswith(" "):
            break

        stripped = raw_line.strip()
        if not stripped:
            continue

        if stripped.startswith("- name: "):
            if current is not None:
                _append_playbook(playbooks, current)
            current = {
                "name": _unquote(stripped.removeprefix("- name: ").strip()),
                "path": "",
                "categories": [],
            }
            in_categories = False
            continue

        if current is None:
            continue

        if stripped.startswith("path: "):
            current["path"] = _unquote(stripped.removeprefix("path: ").strip())
            in_categories = False
            continue

        if stripped == "categories:":
            in_categories = True
            continue

        if in_categories and stripped.startswith("- "):
            categories = current["categories"]
            if isinstance(categories, list):
                categories.append(_unquote(stripped.removeprefix("- ").strip()))
            continue

        in_categories = False

    if current is not None:
        _append_playbook(playbooks, current)

    return tuple(playbooks)


def _receiver_playbooks_start(lines: list[str]) -> int | None:
    for index, line in enumerate(lines):
        if line.strip() == "receiver_playbooks:":
            return index
    return None


def _append_playbook(
    playbooks: list[ReceiverPlaybookConfig],
    raw_playbook: dict[str, str | list[str]],
) -> None:
    name = raw_playbook.get("name", "")
    path = raw_playbook.get("path", "")
    categories = raw_playbook.get("categories", [])

    if not isinstance(name, str) or not isinstance(path, str):
        return
    if not isinstance(categories, list):
        categories = []
    if not name or not path:
        return

    playbooks.append(
        ReceiverPlaybookConfig(
            name=name,
            path=path,
            categories=tuple(str(category) for category in categories),
        )
    )


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
