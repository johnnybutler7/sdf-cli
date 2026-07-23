"""Verification lines for compact contract-5 PR bodies."""

from __future__ import annotations

from typing import Any

from sdf_cli.closeout_check import CloseoutCheckResult
from sdf_cli.closeout_verification_section import compact_verification_status
from sdf_cli.pr_body_contract_five_sections import machine_record
from sdf_cli.verification_formatting import format_duration, status_label


def verification_lines(result: CloseoutCheckResult) -> list[str]:
    archive_path = result.evidence_result.archive_path
    lines = [
        "- Full verification: "
        f"{compact_verification_status(result.verification_result)}",
    ]
    detail_lines = verification_detail_lines(result)
    if detail_lines:
        lines.extend(detail_lines)
    lines.append(f"- `{archive_path}/evidence.md`")
    return lines


def verification_detail_lines(result: CloseoutCheckResult) -> list[str]:
    verification = result.verification_result
    record = machine_record(result)
    lines: list[str] = []
    needs_detail = (
        verification.exit_code != 0
        or verification.status in ("skipped", "config_invalid", "focused_invalid")
        or any(command.status != "passed" for command in verification.command_results)
        or bool(record and record.final_pass_followed_earlier_failure)
    )
    if not needs_detail:
        return []

    if record and record.final_pass_followed_earlier_failure:
        lines.append(
            "- Verification history: final pass followed an earlier verification "
            f"failure ({record.failed_runs} failed of {record.total_runs} runs)."
        )
    if verification.error:
        lines.append(f"- Verification note: {verification.error}.")
    if verification.command_results:
        checks = "; ".join(
            _check_detail(command) for command in verification.command_results
        )
        lines.append(f"- Checks: {checks}.")
    return lines


def _check_detail(command: Any) -> str:
    details = [status_label(command)]
    if command.exit_code != 0:
        details.append(f"exit {command.exit_code}")
    if command.duration_seconds is not None:
        details.append(format_duration(command.duration_seconds))
    return f"`{command.name}` ({', '.join(details)})"
