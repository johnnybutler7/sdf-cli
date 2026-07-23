"""Section-line rendering for compact contract-5 PR bodies."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sdf_cli.closeout_check import CloseoutCheckResult
from sdf_cli.closeout_summary_sections import (
    archive_section_lines,
    strip_list_marker,
    with_fallback_bullets,
)
from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
)


def intent_lines(result: CloseoutCheckResult) -> list[str]:
    lines = with_fallback_bullets(
        archive_section_lines(result, "evidence.md", "## Intent")
    )
    if lines:
        return lines[:4]
    return [
        f"- Change ID: `{result.evidence_result.change_id}`",
        "- Intent was not extracted from the evidence archive.",
    ]


def review_focus_lines(result: CloseoutCheckResult) -> list[str]:
    lines = with_fallback_bullets(
        archive_section_lines(result, "evidence.md", "## Review focus")
    )
    if lines:
        return lines[:5]
    return ["- Review focus was not extracted from the evidence archive."]


def material_limit_lines(result: CloseoutCheckResult) -> list[str]:
    material_lines: list[str] = []
    for line in with_fallback_bullets(
        archive_section_lines(result, "evidence.md", "## Limits")
    ):
        text = strip_list_marker(line)
        if text and not _routine_or_empty_limit(text):
            material_lines.append(f"- {text}")
    return material_lines[:5]


def guidance_lines(result: CloseoutCheckResult) -> list[str]:
    material_lines: list[str] = []
    for line in with_fallback_bullets(
        archive_section_lines(result, "evidence.md", "## Guidance applied")
    ):
        text = strip_list_marker(line)
        if text and not _routine_or_empty_guidance(text):
            material_lines.append(f"- {text}")
    if material_lines:
        return material_lines[:3]
    return ["- No material guidance was recorded."]


def run_context_lines(result: CloseoutCheckResult) -> list[str]:
    archive_path = result.evidence_result.archive_path
    lines = [f"- Change ID: `{result.evidence_result.change_id}`"]
    record = machine_record(result)
    if record is None:
        return [
            *lines,
            "- Run context: unavailable in the machine record.",
            f"- `{archive_path}/evidence.md`",
        ]

    declared = record.declared
    known = [
        f"{field}={declared[field]}"
        for field in ("surface", "model", "reasoning", "speed")
        if declared.get(field) not in (None, "", "unknown", "unavailable")
    ]
    unknown = [
        field
        for field in ("surface", "model", "reasoning", "speed")
        if declared.get(field) in (None, "", "unknown", "unavailable")
    ]
    if known:
        lines.append(f"- Run context: {', '.join(known)}.")
    if unknown:
        lines.append(f"- Unknown run-context fields: {', '.join(unknown)}.")
    if not known and not unknown:
        lines.append("- Run context: no declared fields were recorded.")
    lines.append(f"- `{archive_path}/evidence.md`")
    return lines


def machine_record(result: CloseoutCheckResult) -> Any:
    evidence_path = (
        Path(result.repo_path) / result.evidence_result.archive_path / "evidence.md"
    )
    try:
        return load_evidence_machine_record(
            evidence_path,
            change_id=result.evidence_result.change_id,
        )
    except (OSError, EvidenceFrontMatterError):
        return None


def _routine_or_empty_limit(text: str) -> bool:
    folded = text.casefold().strip()
    if folded.startswith("standard sdf non-claims:"):
        return True
    return folded in {
        "none",
        "none.",
        "none material",
        "none material.",
        "no material limits",
        "no material limits.",
        "nothing slice-specific",
        "nothing slice-specific.",
        "not applicable",
        "not applicable.",
    }


def _routine_or_empty_guidance(text: str) -> bool:
    return text.casefold().strip() in {
        "none",
        "none.",
        "none material",
        "none material.",
        "no material guidance",
        "no material guidance.",
        "not applicable",
        "not applicable.",
    }
