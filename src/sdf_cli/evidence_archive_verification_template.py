"""Embedded verification section template rendering."""

from __future__ import annotations

from typing import Any

from sdf_cli.evidence_archive_contract import VERIFICATION_COMMAND_STATUS_MARKER


def embedded_verification_template_lines(context: Any) -> list[str]:
    """Return the reusable v2 verification section scaffold."""
    return [
        "## Verification",
        "",
        "### Commands",
        "",
        "<!-- sdf:verification-summary:start -->",
        "- Command: not run yet.",
        f"  - {VERIFICATION_COMMAND_STATUS_MARKER} not run yet.",
        "<!-- sdf:verification-summary:end -->",
        "",
        "### Results",
        "",
        "- Reviewer interpretation or material verification limitation: TBD.",
        "",
        "### Blockers / Skips",
        "",
        "",
    ]
