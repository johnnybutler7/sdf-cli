"""Terminal summary rendering for the closeout check workflow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sdf_cli.closeout_readiness_problems import readiness_problem_lines
from sdf_cli.evidence_archive_check import (
    EvidenceArchiveCheckResult,
    render_evidence_archive_check,
)
from sdf_cli.evidence_archive_contract import (
    CONTRACT_FIVE_JUDGEMENT_HEADINGS,
    verification_filename,
)
from sdf_cli.verification_formatting import format_duration
from sdf_cli.verification_results import VerificationRunResult
from sdf_cli.verification_timing import terminal_tracked_timing_lines

if TYPE_CHECKING:
    from sdf_cli.closeout_check import CloseoutCheckResult


def render_closeout_check_summary(result: CloseoutCheckResult) -> str:
    lines = [
        "SDF close summary",
        f"- Resolved repository path: {result.repo_path.resolve()}",
        f"- Evidence archive: {_evidence_status(result.evidence_result)}",
        f"- Full verification: {_verification_status(result.verification_result)}",
    ]
    lines.extend(_archive_readiness_detail_lines(result.evidence_result))
    lines.extend(
        readiness_problem_lines(result.evidence_result, result.verification_result)
    )
    lines.extend(_tracked_timing_lines(result.verification_result))
    lines.append(f"- Overall: {'passed' if result.exit_code == 0 else 'failed'}")
    lines.extend(_summary_next_step_lines(result))
    return "\n".join(lines)


def _evidence_status(result: EvidenceArchiveCheckResult) -> str:
    status = "ready" if result.passed else "not ready (contract 5 required)"
    if any(file.contract_version == 4 for file in result.files):
        status = "ready" if result.passed else "not ready (contract 4 archive)"
    return f"{status} ({result.archive_path})"


def _verification_status(result: VerificationRunResult) -> str:
    if result.status == "skipped":
        reason = result.error or "not run"
        return f"skipped ({reason}; 0 checks run)"
    if result.status == "recorded":
        if result.exit_code == 0:
            return "recorded pass reused (no new verification run)"
        reason = result.error or "recorded passing closeout evidence unavailable"
        return f"recorded evidence unavailable ({reason})"

    status = "passed" if result.exit_code == 0 else "failed"
    return f"{status} ({len(result.command_results)} checks run)"


def _tracked_timing_lines(result: VerificationRunResult) -> list[str]:
    tracked_lines = terminal_tracked_timing_lines(result.command_results)
    if tracked_lines:
        return tracked_lines

    durations = [
        command.duration_seconds
        for command in result.command_results
        if command.duration_seconds is not None
    ]
    if durations:
        return [f"- Verification total duration: {format_duration(sum(durations))}"]

    return ["- Tracked timings: not reported"]


def _archive_readiness_detail_lines(
    result: EvidenceArchiveCheckResult,
) -> list[str]:
    if result.exit_code == 0:
        return []

    return [
        "",
        "Evidence archive readiness:",
        *render_evidence_archive_check(result).splitlines(),
    ]


def _summary_next_step_lines(result: CloseoutCheckResult) -> list[str]:
    close_command = (
        f"sdf close --repo {result.repo_label} "
        f"--change-id {result.evidence_result.change_id}"
    )
    archive_dir = result.repo_path / result.evidence_result.archive_path
    verification_path = f"{result.evidence_result.archive_path}/"
    verification_path += verification_filename(archive_dir)
    if result.exit_code == 0:
        return [
            "",
            "Next:",
            "- `sdf close` records the final closeout result in:",
            f"  {verification_path}",
            "- It also writes and checks the local PR-body artifact.",
        ]

    if _is_expected_evidence_completion_stop(result):
        sections = ", ".join(
            heading.removeprefix("## ") for heading in CONTRACT_FIVE_JUDGEMENT_HEADINGS
        )
        return [
            "",
            "Expected first-close stop:",
            "- Configured verification passed; evidence completion is still required.",
            (
                "- This is an expected evidence-completion stop, not a "
                "verification failure."
            ),
            (
                f"- Edit `{result.evidence_result.archive_path}/evidence.md` "
                f"and complete: {sections}."
            ),
            "- Then rerun:",
            f"  {close_command}",
            "- A passing run records the final closeout result in:",
            f"  {verification_path}",
            "- It also writes and checks the local PR-body artifact.",
        ]

    return [
        "",
        "Next:",
        "- Fix closeout failures first, then rerun:",
        f"  {close_command}",
        "- A passing run records the final closeout result in:",
        f"  {verification_path}",
        "- It also writes and checks the local PR-body artifact.",
    ]


def _is_expected_evidence_completion_stop(result: CloseoutCheckResult) -> bool:
    evidence = result.evidence_result
    if result.verification_result.exit_code != 0 or evidence.invalid_reason is not None:
        return False

    unresolved_sections = set()
    for file in evidence.files:
        if (
            not file.exists
            or file.missing_headings
            or file.missing_verification_statuses
            or file.front_matter_error is not None
            or file.contract_version != 5
        ):
            return False
        unresolved_sections.update(
            placeholder.section for placeholder in file.unresolved_placeholders
        )

    return unresolved_sections == set(CONTRACT_FIVE_JUDGEMENT_HEADINGS)
