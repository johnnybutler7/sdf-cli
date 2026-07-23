"""Predicates for distinguishing executed verification from closeout setup."""

from __future__ import annotations


def configured_verification_executed(result) -> bool:
    verification = result.verification_result
    return verification.status not in (
        "skipped",
        "config_invalid",
        "focused_invalid",
    ) and bool(verification.command_results)
