"""Categorize closeout readiness problems for terminal summaries."""

from __future__ import annotations

from sdf_cli.evidence_archive_check import EvidenceArchiveCheckResult
from sdf_cli.verification_results import VerificationRunResult


def readiness_problem_lines(
    evidence_result: EvidenceArchiveCheckResult,
    verification_result: VerificationRunResult,
) -> list[str]:
    if evidence_result.passed and verification_result.exit_code == 0:
        return []

    sections = (
        ("Unresolved judgement fields", _unresolved_judgement_fields(evidence_result)),
        ("Unavailable facts", _unavailable_facts(evidence_result)),
        ("Verification failure", _verification_failures(verification_result)),
        (
            "Genuine closeout blockers",
            _closeout_blockers(evidence_result, verification_result),
        ),
    )
    lines = ["", "Remaining readiness problems:"]
    for title, problems in sections:
        lines.append(f"- {title}:")
        if not problems:
            lines.append("  none")
            continue
        lines.extend(
            f"  {index}. {problem}" for index, problem in enumerate(problems, 1)
        )
    return lines


def _unresolved_judgement_fields(
    result: EvidenceArchiveCheckResult,
) -> list[str]:
    problems: list[str] = []
    for file in result.files:
        for placeholder in file.unresolved_placeholders:
            problems.append(
                f"{file.filename} {placeholder.section}: {placeholder.marker}"
            )
    return problems


def _unavailable_facts(result: EvidenceArchiveCheckResult) -> list[str]:
    problems: list[str] = []
    if result.invalid_reason is not None:
        problems.append(result.invalid_reason)
    if not result.archive_exists:
        problems.append(f"missing archive: {result.archive_path}")
    for file in result.files:
        if not file.exists:
            problems.append(f"missing file: {file.filename}")
            continue
        problems.extend(
            f"{file.filename} missing heading: {heading}"
            for heading in file.missing_headings
        )
        problems.extend(
            f"{file.filename} missing verification status: {status}"
            for status in file.missing_verification_statuses
        )
        if file.front_matter_error:
            problems.append(
                f"{file.filename} machine record unavailable: "
                f"{file.front_matter_error}"
            )
    return problems


def _verification_failures(result: VerificationRunResult) -> list[str]:
    if result.exit_code == 0 or result.status == "skipped":
        return []
    problems = [
        f"{command.name}: {command.status} (exit {command.exit_code})"
        for command in result.command_results
        if command.status in ("failed", "optional_failed")
    ]
    if result.error:
        problems.append(result.error)
    return problems


def _closeout_blockers(
    evidence_result: EvidenceArchiveCheckResult,
    verification_result: VerificationRunResult,
) -> list[str]:
    blockers: list[str] = []
    if not evidence_result.archive_exists:
        blockers.append("evidence archive is missing")
    elif not evidence_result.passed:
        blockers.append("evidence archive is not ready")
    if verification_result.exit_code != 0 and verification_result.status != "skipped":
        blockers.append("configured verification did not pass")
    return blockers
