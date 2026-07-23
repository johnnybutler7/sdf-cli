"""Starter content for safe receiver initialization."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

from sdf_cli.front_door_version import generated_config_version_lines
from sdf_cli.receiver_payload_manifest import (
    RECEIVER_PAYLOAD_MANIFEST,
    receiver_payload_entry,
)

_CONFIG_VERSION_LINES = generated_config_version_lines()

PORTABLE_SOURCE_FILES: tuple[str, ...] = tuple(
    entry.path
    for entry in RECEIVER_PAYLOAD_MANIFEST
    if entry.content_kind == "portable"
)

STARTER_VERIFICATION_PLACEHOLDER_NAME = "configure-receiver-verification"
STARTER_VERIFICATION_PLACEHOLDER_COMMAND = (
    "echo 'Configure receiver-owned verification commands in "
    ".sdf/verification.yml' && exit 1"
)

GENERATED_STARTER_CONTENT: dict[str, str] = {
    ".sdf/config.yml": (
        "governance_mode: required\n"
        "automatic_execution_permitted: false\n"
        f"{_CONFIG_VERSION_LINES[0]}\n"
        f"{_CONFIG_VERSION_LINES[1]}\n"
    ),
    ".sdf/verification.yml": (
        "version: 1\n"
        "commands:\n"
        f"  - name: {STARTER_VERIFICATION_PLACEHOLDER_NAME}\n"
        f"    command: \"{STARTER_VERIFICATION_PLACEHOLDER_COMMAND}\"\n"
        "    required: true\n"
    ),
    "AGENTS.md": (
        "<!-- SDF Front Door: start -->\n"
        "This repository uses SDF guidance for governed AI-assisted delivery.\n"
        "\n"
        "Start here before repo-specific orientation guidance. The installed\n"
        "receiver front door is:\n"
        "\n"
        "- `.sdf/agent-instructions.md`\n"
        "\n"
        "SDF-specific operating guidance lives under `.sdf/`.\n"
        "<!-- SDF Front Door: end -->\n"
    ),
    "CLAUDE.md": (
        "# Claude guidance\n"
        "\n"
        "This repository uses SDF guidance for governed AI-assisted delivery.\n"
        "\n"
        "Before making changes, read:\n"
        "\n"
        "- `.sdf/agent-instructions.md`\n"
        "\n"
        "SDF-specific operating guidance lives under `.sdf/`.\n"
    ),
}

_PORTABLE_RESOURCE_ROOT = "resources/portable_sdf"


def starter_content(relative_path: str) -> str:
    if relative_path in GENERATED_STARTER_CONTENT:
        return GENERATED_STARTER_CONTENT[relative_path]
    if relative_path in PORTABLE_SOURCE_FILES:
        return portable_resource(relative_path).read_text(encoding="utf-8")
    raise KeyError(relative_path)


def portable_resource(relative_path: str) -> Any:
    if relative_path not in PORTABLE_SOURCE_FILES:
        raise KeyError(relative_path)
    resource_path = _portable_resource_path(relative_path)
    return files("sdf_cli").joinpath(_PORTABLE_RESOURCE_ROOT, resource_path)


def starter_source_classification(relative_path: str) -> str:
    entry = receiver_payload_entry(relative_path)
    if entry.content_kind == "portable":
        return "portable"
    if entry.content_kind == "generated":
        return "generated"
    if entry.content_kind == "shared":
        return "shared receiver-owned"
    raise ValueError(entry.content_kind)


def _portable_resource_path(relative_path: str) -> str:
    if relative_path.startswith(".sdf/"):
        return "sdf/" + relative_path.removeprefix(".sdf/")
    raise KeyError(relative_path)
