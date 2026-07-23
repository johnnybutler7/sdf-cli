"""Small text transformations used by evidence machine-record writers."""

from __future__ import annotations


def indented_yaml(yaml_text: str) -> list[str]:
    lines = yaml_text.rstrip("\n").splitlines()
    return [f"    {line}" if line else "" for line in lines]


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
