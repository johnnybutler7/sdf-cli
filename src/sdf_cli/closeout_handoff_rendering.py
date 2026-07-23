"""Terminal rendering for the composed local closeout handoff."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sdf_cli.closeout_check import render_closeout_check_summary

if TYPE_CHECKING:
    from sdf_cli.closeout_check import CloseoutCheckResult
    from sdf_cli.closeout_handoff import CloseoutHandoffResult
    from sdf_cli.pr_body import PrBodyWriteResult
    from sdf_cli.pr_body_check import PrBodyCheckResult


def render_closeout_handoff(result: CloseoutHandoffResult) -> str:
    lines = [
        "SDF close",
        f"Resolved repository path: {result.closeout_result.repo_path.resolve()}",
        f"closeout check: {_closeout_status(result.closeout_result)}",
        f"closeout result record: {_record_status(result)}",
        f"pr-body write: {_write_status(result.write_result)}",
        f"pr-body check: {_check_status(result.check_result)}",
        "github: not mutated",
    ]
    lines.extend(_warning_lines(result))
    lines.extend(_detail_lines(result))
    return "\n".join(lines)


def _closeout_status(result: CloseoutCheckResult) -> str:
    return "passed" if result.exit_code == 0 else "failed"


def _record_status(result: CloseoutHandoffResult) -> str:
    if not result.closeout_record_written:
        return "skipped"
    return f"written (.sdf/evidence/{result.change_id}/evidence.md machine record)"


def _write_status(result: PrBodyWriteResult | None) -> str:
    if result is None:
        return "skipped"
    if result.written:
        status = "overwritten" if result.overwritten else "written"
        return f"{status} ({result.artifact_path})"
    if result.existing:
        return f"existing not regenerated ({result.artifact_path})"
    if result.closeout_result is not None and result.closeout_result.exit_code != 0:
        return "failed"
    return "skipped"


def _check_status(result: PrBodyCheckResult | None) -> str:
    if result is None:
        return "skipped"
    return "ready" if result.passed else "failed"


def _warning_lines(result: CloseoutHandoffResult) -> list[str]:
    warnings: list[str] = []
    if result.write_result is not None:
        warnings.extend(result.write_result.warnings)
    if result.check_result is not None:
        for warning in result.check_result.warnings:
            if warning not in warnings:
                warnings.append(warning)
    return warnings


def _detail_lines(result: CloseoutHandoffResult) -> list[str]:
    if result.closeout_result.exit_code != 0:
        return ["", *render_closeout_check_summary(result.closeout_result).splitlines()]
    if result.check_result is not None and result.check_result.exit_code != 0:
        return _check_failure_lines(result.check_result)
    if result.write_result is not None and result.write_result.existing:
        return [
            "after evidence-only wording edits: commit the implementation and "
            "final evidence, then run "
            f"sdf close --repo {result.closeout_result.repo_label} "
            f"--change-id {result.change_id} --refresh-handoff; refresh reuses "
            "the recorded passing verification without rerunning the configured "
            "boundary; publish the resulting handoff verbatim when it reports "
            "publication-ready"
        ]
    if result.write_result is not None and result.write_result.skipped_reason:
        return [result.write_result.skipped_reason]
    if result.exit_code == 0 and result.write_result is not None:
        return [
            "next: commit the change and evidence, then run "
            f"sdf close --repo {result.closeout_result.repo_label} "
            f"--change-id {result.change_id} --refresh-handoff; refresh reuses "
            "the recorded passing verification without rerunning the configured "
            "boundary; publish the resulting handoff verbatim when it reports "
            "publication-ready"
        ]
    return []


def _check_failure_lines(result: PrBodyCheckResult) -> list[str]:
    lines: list[str] = []
    for section in result.missing_sections:
        lines.append(f"missing section: {section}")
    for filename in result.missing_evidence_links:
        lines.append(f"missing evidence link: {filename}")
    for link in result.broken_evidence_links:
        lines.append(f"broken evidence link: {link}")
    for link in result.absolute_evidence_links:
        lines.append(f"absolute evidence link: {link}")
    for link in result.repo_relative_evidence_links:
        lines.append(f"repo-relative evidence link in GitHub mode: {link}")
    for link in result.wrong_github_evidence_links:
        lines.append(f"wrong GitHub evidence link: {link}")
    return lines
