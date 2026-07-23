"""Parse focused verification subsets from ``.sdf/verification.yml``."""

from __future__ import annotations

from sdf_cli.config.verification import FocusedVerificationSubset, VerificationCommand


def parse_focused_subsets(
    lines: list[str],
) -> tuple[tuple[FocusedVerificationSubset, ...], str | None]:
    focused_start = _top_level_section_start(lines, "focused")
    if _top_level_value(lines, "focused") == "[]":
        return (), None
    if focused_start is None:
        return (), None

    items, error = _parse_focused_items(lines, focused_start)
    if error is not None:
        return (), error
    return _build_focused_subsets(items)


def focused_visibility_issues(
    commands: tuple[VerificationCommand, ...],
    focused_subsets: tuple[FocusedVerificationSubset, ...],
) -> tuple[str, ...]:
    configured_names = {command.name for command in commands}
    issues: list[str] = []
    for subset in focused_subsets:
        for command_name in subset.commands:
            if command_name not in configured_names:
                issues.append(
                    "focused verification subset "
                    f"{subset.name} references unknown command: {command_name}"
                )
    return tuple(issues)


def _parse_focused_items(
    lines: list[str],
    focused_start: int,
) -> tuple[list[dict[str, object]], str | None]:
    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    collecting_commands = False
    for raw_line in lines[focused_start + 1 :]:
        if _is_top_level_line(raw_line):
            break
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if _starts_list_item(raw_line, indent=2):
            current = _finish_focused_item(items, current)
            current, error = _start_focused_item(stripped)
            if error is not None:
                return items, error
            collecting_commands = False
            continue
        if current is None:
            return items, "verification focused subsets must be a list"
        if collecting_commands and _starts_nested_list_item(raw_line, indent=4):
            command_names = current.setdefault("commands", [])
            if not isinstance(command_names, list):
                return items, "verification focused commands must be a list"
            command_names.append(_unquote(stripped[1:].strip()))
            continue
        key, separator, value = stripped.partition(":")
        if not separator:
            return items, f"invalid focused verification field: {stripped}"
        if key.strip() == "commands" and not value.strip():
            current["commands"] = []
            collecting_commands = True
            continue
        current[key.strip()] = _unquote(value.strip())
        collecting_commands = False
    _finish_focused_item(items, current)
    return items, None


def _start_focused_item(
    stripped: str,
) -> tuple[dict[str, object], str | None]:
    if stripped != "-" and not stripped.startswith("- "):
        return {}, f"invalid focused verification list item: {stripped}"
    item: dict[str, object] = {}
    remainder = stripped[1:].strip()
    if not remainder:
        return item, None
    key, separator, value = remainder.partition(":")
    if not separator:
        return item, f"invalid focused verification field: {remainder}"
    item[key.strip()] = _unquote(value.strip())
    return item, None


def _finish_focused_item(
    items: list[dict[str, object]],
    current: dict[str, object] | None,
) -> dict[str, object] | None:
    if current is not None:
        items.append(current)
    return None


def _build_focused_subsets(
    items: list[dict[str, object]],
) -> tuple[tuple[FocusedVerificationSubset, ...], str | None]:
    focused_subsets: list[FocusedVerificationSubset] = []
    for index, item in enumerate(items, start=1):
        name_value = item.get("name", "")
        commands_value = item.get("commands", [])
        name = name_value.strip() if isinstance(name_value, str) else ""
        if not name:
            return (), f"focused verification subset {index} must have a non-blank name"
        if not isinstance(commands_value, list):
            return (), f"focused verification subset {name} commands must be a list"
        command_names = tuple(
            command_name.strip()
            for command_name in commands_value
            if isinstance(command_name, str) and command_name.strip()
        )
        if not command_names:
            return (), f"focused verification subset {name} must list commands"
        focused_subsets.append(FocusedVerificationSubset(name, command_names))
    return tuple(focused_subsets), None


def _top_level_value(lines: list[str], key: str) -> str | None:
    prefix = f"{key}:"
    for raw_line in lines:
        if not _is_top_level_line(raw_line):
            continue
        stripped = raw_line.strip()
        if stripped == prefix:
            return ""
        if stripped.startswith(f"{prefix} "):
            return _unquote(stripped.removeprefix(prefix).strip())
    return None


def _top_level_section_start(lines: list[str], key: str) -> int | None:
    for index, raw_line in enumerate(lines):
        if _is_top_level_line(raw_line) and raw_line.strip() == f"{key}:":
            return index
    return None


def _is_top_level_line(raw_line: str) -> bool:
    return bool(raw_line.strip()) and not raw_line.startswith((" ", "\t"))


def _starts_list_item(raw_line: str, *, indent: int) -> bool:
    return _leading_spaces(raw_line) == indent and raw_line.strip().startswith("-")


def _starts_nested_list_item(raw_line: str, *, indent: int) -> bool:
    return _leading_spaces(raw_line) >= indent and raw_line.strip().startswith("-")


def _leading_spaces(raw_line: str) -> int:
    return len(raw_line) - len(raw_line.lstrip(" "))


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
