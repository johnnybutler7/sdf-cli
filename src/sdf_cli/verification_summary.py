"""Render terminal summaries for verification runs."""

from __future__ import annotations

from sdf_cli.verification_formatting import format_duration, status_label
from sdf_cli.verification_results import (
    VerificationCommandResult,
    VerificationRunResult,
)
from sdf_cli.verification_timing import (
    duration_suffix,
    terminal_tracked_timing_lines,
)


def render_verification_summary(
    result: VerificationRunResult,
    *,
    governance_mode: str | None = None,
) -> str:
    command_results = result.command_results
    passed_count = sum(1 for command in command_results if command.passed)
    failed_count = len(command_results) - passed_count

    lines = [
        "SDF verify summary",
        f"Resolved repository path: {result.repo_path.resolve()}",
        *_focused_lines(result),
        "Commands:",
        *_command_lines(command_results),
        *terminal_tracked_timing_lines(command_results),
        "Results:",
        f"- Overall result: {_overall_result(result)}",
        f"- Checks run: {len(command_results)}",
        f"- Passed: {passed_count}",
        f"- Failed: {failed_count}",
    ]
    lines.extend(_total_duration_lines(command_results))
    lines.extend(_evidence_boundary_lines())
    lines.extend(_governance_mode_lines(result, governance_mode))
    lines.extend(
        [
            "Blockers:",
            *_blocker_lines(result),
            "Transient Notes:",
            *_transient_note_lines(command_results),
            "Boundary:",
            *_focused_boundary_lines(result),
            "This command does not approve, merge, repair, deploy, or release.",
            "",
        ]
    )
    return "\n".join(lines)


def _command_lines(
    command_results: tuple[VerificationCommandResult, ...],
) -> list[str]:
    if not command_results:
        return ["- None run."]
    return [
        f"- {command.command}: {_status_label(command)}"
        f"{duration_suffix(command)}"
        for command in command_results
    ]


def _focused_lines(result: VerificationRunResult) -> list[str]:
    if result.focused_name is None:
        return []
    return [
        f"Focused run: {result.focused_name}",
        (
            "Focused verification is supporting feedback only; it does not "
            "replace the full closeout gate."
        ),
        "Full closeout gate: sdf verify --repo PATH",
    ]


def _total_duration_lines(
    command_results: tuple[VerificationCommandResult, ...],
) -> list[str]:
    durations = [
        command.duration_seconds
        for command in command_results
        if command.duration_seconds is not None
    ]
    if not durations:
        return []
    return [f"- Total duration: {format_duration(sum(durations))}"]


def _blocker_lines(result: VerificationRunResult) -> list[str]:
    if result.status in ("config_invalid", "focused_invalid"):
        return [
            f"- Verification was not run: {result.error}",
            "  Next: fix verification configuration, then rerun "
            f"`sdf verify --repo {_repo_rerun_label(result)}`.",
        ]

    failed_required = [
        command
        for command in result.command_results
        if command.required and not command.passed
    ]
    if not failed_required:
        return ["None currently."]

    lines: list[str] = []
    for command in failed_required:
        lines.extend(
            [
                f"- Failed required check: {command.command}",
                "  Next: fix the failing check, then rerun "
                f"`sdf verify --repo {_repo_rerun_label(result)}`.",
            ]
        )
    return lines


def _repo_rerun_label(result: VerificationRunResult) -> str:
    if result.repo_label:
        return result.repo_label
    return str(result.repo_path)


def _transient_note_lines(
    command_results: tuple[VerificationCommandResult, ...],
) -> list[str]:
    optional_failures = [
        command
        for command in command_results
        if not command.required and not command.passed
    ]
    if not optional_failures:
        return ["None currently."]
    return [
        "- Optional check failed but did not block the overall result: "
        f"{command.command}"
        for command in optional_failures
    ]


def _evidence_boundary_lines() -> list[str]:
    return [
        "- No files were written.",
        "- No PR body was updated.",
        "- No evidence artifact was generated.",
    ]


def _governance_mode_lines(
    result: VerificationRunResult,
    governance_mode: str | None,
) -> list[str]:
    if governance_mode == "inactive":
        return [
            "Governance mode:",
            "- governance_mode: inactive detected in .sdf/config.yml.",
            (
                "- SDF Front Door is installed but governed closeout is not "
                "required for this run."
            ),
            (
                "- Preserve automatic_execution_permitted: false; no evidence "
                "archive or generated PR body is required by this mode."
            ),
        ]

    if governance_mode != "required":
        return []

    repo_label = _repo_rerun_label(result)
    return [
        "Governed closeout:",
        "- governance_mode: required detected in .sdf/config.yml.",
        (
            "- Normal next step: make the change, then close it with evidence:"
        ),
        f"  sdf close --repo {repo_label} --change-id <change-id>",
        (
            "- The first close creates evidence and may stop for evidence "
            "completion; complete it, then close again."
        ),
        "- Use the checked generated PR-body handoff as the default PR body, "
        "or record a manual-body exception.",
    ]


def _focused_boundary_lines(result: VerificationRunResult) -> list[str]:
    if result.focused_name is None:
        return []
    return [
        "Focused verification is supporting feedback only.",
        "Full closeout gate remains: sdf verify --repo PATH.",
    ]


def _overall_result(result: VerificationRunResult) -> str:
    if result.exit_code == 0:
        return "passed"
    return "failed"


def _status_label(command: VerificationCommandResult) -> str:
    return status_label(command)
