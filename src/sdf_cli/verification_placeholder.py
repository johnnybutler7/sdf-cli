"""Starter receiver verification placeholder detection."""

from __future__ import annotations

from sdf_cli.config.verification import VerificationCommand
from sdf_cli.receiver_scaffold_content import (
    STARTER_VERIFICATION_PLACEHOLDER_COMMAND,
    STARTER_VERIFICATION_PLACEHOLDER_NAME,
)


def is_starter_verification_placeholder(command: VerificationCommand) -> bool:
    return (
        command.name == STARTER_VERIFICATION_PLACEHOLDER_NAME
        and command.command == STARTER_VERIFICATION_PLACEHOLDER_COMMAND
        and command.required
    )
