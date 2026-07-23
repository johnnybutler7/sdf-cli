"""Compact contract-5 PR body rendering."""

from __future__ import annotations

from sdf_cli.closeout_check import CloseoutCheckResult
from sdf_cli.pr_body_contract_five_sections import (
    guidance_lines,
    intent_lines,
    material_limit_lines,
    review_focus_lines,
    run_context_lines,
)
from sdf_cli.pr_body_contract_five_verification import verification_lines


def render_contract_five_pr_body_markdown(result: CloseoutCheckResult) -> str:
    archive_path = result.evidence_result.archive_path
    lines = [
        "# What you are reviewing",
        "",
        *intent_lines(result),
        f"- `{archive_path}/evidence.md`",
        "",
        "## Review focus",
        "",
        *review_focus_lines(result),
        f"- `{archive_path}/evidence.md`",
    ]
    limit_lines = material_limit_lines(result)
    if limit_lines:
        lines.extend(["", "## Limits", "", *limit_lines])
    lines.extend(
        [
            "",
            "## Run context",
            "",
            *run_context_lines(result),
            "",
            "## Guidance applied",
            "",
            *guidance_lines(result),
            f"- `{archive_path}/evidence.md`",
            "",
            "## Verification",
            "",
            *verification_lines(result),
        ]
    )
    return "\n".join(lines)
