"""Reconstruct reviewer-handoff input from committed contract-5 closeout facts."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.closeout_check import CloseoutCheckResult
from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
)
from sdf_cli.verification_results import (
    VerificationCommandResult,
    VerificationRunResult,
)


def recorded_closeout_result(
    repo_path: Path,
    change_id: str,
    evidence_result,
    *,
    allow_failed: bool = False,
    include_checks: bool = False,
) -> CloseoutCheckResult | None:
    if not evidence_result.passed:
        return None
    evidence_path = repo_path / evidence_result.archive_path / "evidence.md"
    try:
        record = load_evidence_machine_record(evidence_path, change_id=change_id)
    except (OSError, EvidenceFrontMatterError):
        return None
    if record is None or not _completed_record(record, allow_failed=allow_failed):
        return None

    latest = record.latest_run
    assert latest is not None
    passed = record.closeout_status == "passed"
    checks = _recorded_checks(latest) if include_checks else ()
    verification = VerificationRunResult(
        repo_path=repo_path,
        config_path=repo_path / ".sdf" / "verification.yml",
        status="recorded",
        exit_code=0 if passed else 1,
        command_results=checks,
        recorded_check_count=len(latest["checks"]),
        recorded_duration_seconds=float(latest["total_duration_seconds"]),
    )
    return CloseoutCheckResult(
        repo_label=str(repo_path),
        repo_path=repo_path,
        evidence_result=evidence_result,
        verification_result=verification,
    )


def _completed_record(record, *, allow_failed: bool) -> bool:
    if record.contract_version not in {4, 5} or record.total_runs < 1:
        return False
    latest = record.latest_run
    if latest is None or not latest.get("checks"):
        return False
    if record.closeout_status == "passed":
        return record.closed_at is not None and latest.get("status") == "passed"
    return bool(
        allow_failed
        and record.contract_version == 5
        and record.closeout_status == "failed"
        and latest.get("status") in {"failed", "blocked", "skipped"}
    )


def _recorded_checks(
    latest: dict[str, object],
) -> tuple[VerificationCommandResult, ...]:
    checks = latest["checks"]
    assert isinstance(checks, list)
    return tuple(_recorded_check(check) for check in checks)


def _recorded_check(check: object) -> VerificationCommandResult:
    assert isinstance(check, dict)
    status = str(check["status"])
    return VerificationCommandResult(
        name=str(check["name"]),
        command="recorded in committed contract-5 evidence",
        required=status != "optional_failed",
        exit_code=0 if status == "passed" else 1,
        status=status,
        stdout="",
        stderr="",
        duration_seconds=check.get("duration_seconds"),  # type: ignore[arg-type]
        track_timing=check.get("duration_seconds") is not None,
    )
