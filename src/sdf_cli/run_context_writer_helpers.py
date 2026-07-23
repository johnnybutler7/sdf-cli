"""Formatting and local-observation helpers for run-context writing."""

from __future__ import annotations


def yaml_scalar(value: str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def mapping_lines(mapping: dict[str, str]) -> list[str]:
    return [f"  {key}: {yaml_scalar(value)}" for key, value in mapping.items()]
