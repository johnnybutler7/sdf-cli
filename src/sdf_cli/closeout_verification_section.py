"""Verification section rendering for closeout summaries."""

from __future__ import annotations

from typing import Any

from sdf_cli.closeout_summary_sections import (
    archive_reference,
    archive_section_lines,
    strip_list_marker,
    truncate_with_required_line,
)
from sdf_cli.closeout_verification_handoff import verification_history_line
from sdf_cli.evidence_archive_contract import (
    verification_filename,
    verification_section_heading,
)
from sdf_cli.evidence_verification_summary import compact_check_summary
from sdf_cli.verification_formatting import format_duration
from sdf_cli.verification_results import VerificationRunResult


def verification_lines(result: Any) -> list[str]:
    archive_path = result.evidence_result.archive_path
    filename = verification_filename(result.repo_path / archive_path)
    lines = [
        "- Full verification: "
        f"{compact_verification_status(result.verification_result)}",
        f"- Overall closeout: {'passed' if result.exit_code == 0 else 'failed'}",
    ]
    checks = compact_check_summary(result.verification_result)
    if checks:
        lines.append(f"- Checks: {checks}.")
    history = verification_history_line(result)
    if history:
        lines.append(history)
    lines.extend(compact_verification_handoff_lines(result))
    return truncate_with_required_line(
        lines,
        f"- Verification evidence: "
        f"`{archive_reference(archive_path, filename)}`",
        max_lines=6,
    )


def compact_verification_status(result: VerificationRunResult) -> str:
    if result.status == "skipped":
        reason = result.error or "not run"
        return f"skipped ({reason}; 0 checks run)"
    if result.status == "recorded":
        return _recorded_verification_status(result)

    status = "passed" if result.exit_code == 0 else "failed"
    check_count = len(result.command_results)
    durations = [
        command.duration_seconds
        for command in result.command_results
        if command.duration_seconds is not None
    ]
    if durations and len(durations) == check_count:
        return (
            f"{status} ({check_count_label(check_count)}, "
            f"{format_duration(sum(durations))} total)"
        )

    return f"{status} ({check_count_label(check_count)})"


def _recorded_verification_status(result: VerificationRunResult) -> str:
    details = _recorded_verification_details(result)
    suffix = ""
    if details:
        suffix = f" ({', '.join(details)})"
    if result.exit_code != 0:
        return (
            f"recorded failed closeout evidence reused{suffix}; "
            "no new verification run"
        )
    evidence_label = "closeout evidence"
    if _recorded_from_structured_closeout(result):
        evidence_label = "embedded closeout evidence"
    if any(command.name == "embedded-closeout" for command in result.command_results):
        evidence_label = "embedded closeout evidence"
    return (
        f"recorded passing {evidence_label} reused"
        f"{suffix}; no new verification run"
    )


def _recorded_verification_details(result: VerificationRunResult) -> list[str]:
    details: list[str] = []
    if result.recorded_check_count is not None:
        details.append(check_count_label(result.recorded_check_count))
    if result.recorded_duration_seconds is not None:
        details.append(f"{format_duration(result.recorded_duration_seconds)} total")
    return details


def check_count_label(check_count: int) -> str:
    noun = "check" if check_count == 1 else "checks"
    return f"{check_count} {noun}"


def _recorded_from_structured_closeout(result: VerificationRunResult) -> bool:
    return any(
        command.name == "structured-closeout" for command in result.command_results
    )


def compact_verification_handoff_lines(result: Any) -> list[str]:
    filename = verification_filename(
        result.repo_path / result.evidence_result.archive_path
    )
    blocker_lines = archive_section_lines(
        result,
        filename,
        verification_section_heading(filename, "Blockers / Skips"),
    )
    for line in blocker_lines:
        text = strip_list_marker(line)
        if _is_meaningful_blocker_or_fix(text):
            return [f"- {text}"]

    result_lines = archive_section_lines(
        result,
        filename,
        verification_section_heading(filename, "Results"),
    )
    for line in result_lines:
        text = strip_list_marker(line)
        if _is_reviewer_result_summary(text):
            return [f"- {text}"]

    return []


def _is_meaningful_blocker_or_fix(text: str) -> bool:
    folded = text.casefold()
    if folded.startswith("failed-then-fixed attempts:"):
        return not any(
            marker in folded
            for marker in ("not recorded", "none currently", "none.")
        )
    if folded.startswith("blockers:"):
        return not any(
            marker in folded
            for marker in ("not recorded", "none currently", "none.")
        )
    return False


def _is_reviewer_result_summary(text: str) -> bool:
    folded = text.casefold()
    return folded.startswith(("reviewer-ready summary:", "result:", "blocker:"))
