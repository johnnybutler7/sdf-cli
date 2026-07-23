"""Narrow YAML-like parser for SDF verification config."""

from __future__ import annotations

from sdf_cli.config.verification import FocusedVerificationSubset, VerificationCommand
from sdf_cli.config.verification_focused_parser import (
    focused_visibility_issues,
    parse_focused_subsets,
)


def parse_verification_lines(
    lines: list[str],
) -> tuple[
    tuple[VerificationCommand, ...],
    tuple[FocusedVerificationSubset, ...],
    tuple[str, ...],
    str | None,
]:
    version = _top_level_value(lines, "version")
    if version is None:
        return (), (), (), "verification config must contain version: 1"
    if version != "1":
        return (), (), (), "verification config version must be 1"

    commands_start = _top_level_section_start(lines, "commands")
    if commands_start is None:
        if _top_level_value(lines, "commands") == "[]":
            return (), (), (), "verification config commands must not be empty"
        return (), (), (), "verification config must contain commands"

    items, error = _parse_command_items(lines, commands_start)
    if error is not None:
        return (), (), (), error
    commands, error = _build_commands(items)
    if error is not None:
        return (), (), (), error

    focused_subsets, error = parse_focused_subsets(lines)
    if error is not None:
        return (), (), (), error

    visibility_issues = focused_visibility_issues(commands, focused_subsets)
    return commands, focused_subsets, visibility_issues, None


def _parse_command_items(
    lines: list[str],
    commands_start: int,
) -> tuple[list[dict[str, str]], str | None]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in lines[commands_start + 1 :]:
        if _is_top_level_line(raw_line):
            break
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("-"):
            current, error = _start_command_item(items, current, stripped)
            if error is not None:
                return items, error
            continue
        if current is None:
            return items, "verification config commands must be a list"
        error = _add_field(current, stripped)
        if error is not None:
            return items, error
    if current is not None:
        items.append(current)
    return items, None


def _start_command_item(
    items: list[dict[str, str]],
    current: dict[str, str] | None,
    stripped: str,
) -> tuple[dict[str, str], str | None]:
    if stripped != "-" and not stripped.startswith("- "):
        return {}, f"invalid command list item: {stripped}"
    if current is not None:
        items.append(current)
    item: dict[str, str] = {}
    remainder = stripped[1:].strip()
    if remainder:
        error = _add_field(item, remainder)
        if error is not None:
            return item, error
    return item, None


def _build_commands(
    items: list[dict[str, str]],
) -> tuple[tuple[VerificationCommand, ...], str | None]:
    commands: list[VerificationCommand] = []
    for index, item in enumerate(items, start=1):
        name = item.get("name", "").strip()
        command = item.get("command", "").strip()
        required = item.get("required", "true").strip()
        track_timing = item.get("track_timing", "false").strip()
        error = _validate_command(index, name, command, required, track_timing)
        if error is not None:
            return (), error
        commands.append(
            VerificationCommand(
                name=name,
                command=command,
                required=required == "true",
                track_timing=track_timing == "true",
            )
        )
    if not commands:
        return (), "verification config commands must not be empty"
    return tuple(commands), None


def _validate_command(
    index: int,
    name: str,
    command: str,
    required: str,
    track_timing: str,
) -> str | None:
    if not name:
        return f"verification command {index} must have a non-blank name"
    if not command:
        return f"verification command {index} must have a non-blank command"
    if required not in ("true", "false"):
        return f"verification command {name} required must be true or false"
    if track_timing not in ("true", "false"):
        return f"verification command {name} track_timing must be true or false"
    return None


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


def _add_field(item: dict[str, str], stripped: str) -> str | None:
    key, separator, value = stripped.partition(":")
    if not separator:
        return f"invalid command field: {stripped}"
    item[key.strip()] = _unquote(value.strip())
    return None


def _is_top_level_line(raw_line: str) -> bool:
    return bool(raw_line.strip()) and not raw_line.startswith((" ", "\t"))


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
