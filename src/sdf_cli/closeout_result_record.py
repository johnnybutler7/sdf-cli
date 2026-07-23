"""Write compact closeout facts into the active evidence archive."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from sdf_cli import __version__
from sdf_cli.closeout_check import CloseoutCheckResult
from sdf_cli.closeout_verification_execution import configured_verification_executed
from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
    update_evidence_machine_record,
)
from sdf_cli.evidence_machine_context import branch_context, repository_context
from sdf_cli.evidence_verification_summary import refresh_evidence_verification_summary


def closeout_result_record_path(change_id: str) -> str:
    return f".sdf/evidence/{change_id}/evidence.md"


def write_verification_result_record(
    *,
    repo: str,
    result: CloseoutCheckResult,
) -> bool:
    if not result.evidence_result.archive_exists:
        return False
    change_id = result.evidence_result.change_id
    path = Path(repo).expanduser() / closeout_result_record_path(change_id)
    try:
        record = load_evidence_machine_record(path, change_id=change_id)
    except (OSError, EvidenceFrontMatterError):
        return False
    if record is None:
        return False
    status = _verification_status(result)
    latest = record.latest_run
    total_runs = record.total_runs
    failed_runs = record.failed_runs
    final_pass_followed_earlier_failure = record.final_pass_followed_earlier_failure
    if configured_verification_executed(result):
        total_runs += 1
        failed_runs += status == "failed"
        final_pass_followed_earlier_failure = status == "passed" and failed_runs > 0
        latest = {
            "status": status,
            "total_duration_seconds": sum(
                command.duration_seconds or 0.0
                for command in result.verification_result.command_results
            ),
            "checks": [
                {
                    "name": command.name,
                    "status": command.status,
                    "duration_seconds": command.duration_seconds,
                }
                for command in result.verification_result.command_results
            ],
        }
    update_evidence_machine_record(
        path,
        change_id=change_id,
        record=replace(
            record,
            written_by=f"software-dark-factory {__version__}",
            repository=repository_context(Path(repo).expanduser()),
            branch=branch_context(Path(repo).expanduser()),
            total_runs=total_runs,
            failed_runs=failed_runs,
            final_pass_followed_earlier_failure=final_pass_followed_earlier_failure,
            latest_run=latest,
        ),
    )
    if configured_verification_executed(result):
        refresh_evidence_verification_summary(path, result.verification_result)
    return True


def write_closeout_status_record(
    *,
    repo: str,
    result: CloseoutCheckResult,
    clock: Callable[[], datetime] | None = None,
) -> bool:
    if not result.evidence_result.archive_exists:
        return False
    change_id = result.evidence_result.change_id
    path = Path(repo).expanduser() / closeout_result_record_path(change_id)
    try:
        record = load_evidence_machine_record(path, change_id=change_id)
    except (OSError, EvidenceFrontMatterError):
        return False
    if record is None:
        return False
    update_evidence_machine_record(
        path,
        change_id=change_id,
        record=replace(
            record,
            closeout_status="passed" if result.exit_code == 0 else "failed",
        ),
    )
    return True


def _verification_status(result: CloseoutCheckResult) -> str:
    verification = result.verification_result
    if verification.status == "skipped":
        return "skipped"
    if verification.status in ("config_invalid", "focused_invalid"):
        return "blocked"
    return "passed" if verification.exit_code == 0 else "failed"
