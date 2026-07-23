"""Embedded and standalone verification evidence validation helpers."""

from __future__ import annotations

from sdf_cli.evidence_archive_contract import VERIFICATION_COMMAND_STATUS_MARKER
from sdf_cli.evidence_archive_placeholders import markdown_section


def missing_verification_statuses(
    filename: str,
    content: str,
    *,
    embedded_verification: bool,
    contract_version: int = 5,
) -> tuple[str, ...]:
    """Return meaningful command blocks that lack a recorded status."""
    if contract_version >= 5:
        return ()
    if filename == "evidence.md" and not embedded_verification:
        return ()
    if filename != "evidence.md":
        return ()

    commands_heading = "### Commands"
    missing_statuses: list[str] = []
    for index, command_block in enumerate(
        command_blocks(content, commands_heading), start=1
    ):
        if (
            VERIFICATION_COMMAND_STATUS_MARKER.casefold()
            not in command_block.casefold()
        ):
            missing_statuses.append(
                f"command {index} missing {VERIFICATION_COMMAND_STATUS_MARKER}"
            )
    return tuple(missing_statuses)


def command_blocks(markdown: str, commands_heading: str) -> tuple[str, ...]:
    """Extract meaningful command bullets from a versioned verification section."""
    commands_section = markdown_section(markdown, commands_heading)
    blocks: list[list[str]] = []
    current_block: list[str] = []
    for line in commands_section.splitlines():
        if line.startswith("- "):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        elif current_block:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)
    return tuple(
        "\n".join(block)
        for block in blocks
        if is_meaningful_command_block("\n".join(block))
    )


def is_meaningful_command_block(block: str) -> bool:
    """Skip the scaffold's intentionally not-yet-run command placeholder."""
    first_line = block.splitlines()[0].casefold()
    if first_line.startswith("- command: not run yet"):
        return False
    return "`" in block or first_line.startswith("- command:")
