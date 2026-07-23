"""Markdown closeout summary rendering."""

from __future__ import annotations

from sdf_cli.closeout_check import (
    CloseoutCheckResult,
)
from sdf_cli.closeout_run_context import run_context_lines
from sdf_cli.closeout_summary_sections import (
    archive_reference,
    playbook_lines,
    review_focus_lines,
    what_reviewing_lines,
)
from sdf_cli.closeout_verification_section import verification_lines
from sdf_cli.evidence_archive_contract import CURRENT_NARRATIVE_FILENAME


def render_closeout_summary_markdown(result: CloseoutCheckResult) -> str:
    archive_path = result.evidence_result.archive_path
    narrative = CURRENT_NARRATIVE_FILENAME
    narrative_label = (
        "Review evidence" if narrative == "evidence.md" else "Review notes"
    )
    lines = [
        "# What you are reviewing",
        "",
        *what_reviewing_lines(result),
        "",
        "## Review focus",
        "",
        *review_focus_lines(result),
        f"- {narrative_label}: `{archive_reference(archive_path, narrative)}`",
        "",
        "## Run context",
        "",
        *run_context_lines(result),
        "",
        "## Guidance applied",
        "",
        *playbook_lines(result),
        "",
        "## Verification",
        "",
        *verification_lines(result),
    ]
    return "\n".join(lines)
