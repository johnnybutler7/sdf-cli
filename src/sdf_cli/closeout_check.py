"""Closeout check workflow for governed changes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

from sdf_cli.closeout_check_rendering import render_closeout_check_summary
from sdf_cli.closeout_declared_context import complete_existing_declared_context
from sdf_cli.evidence_archive_check import (
    EvidenceArchiveCheckResult,
    check_evidence_archive,
)
from sdf_cli.evidence_archive_scaffold import scaffold_evidence_archive
from sdf_cli.verification_results import VerificationRunResult
from sdf_cli.verification_runner import (
    CommandExecutor,
    MonotonicClock,
    run_verification,
)

__all__ = (
    "CloseoutCheckResult",
    "render_closeout_check_summary",
    "run_closeout_check",
    "with_evidence_result",
)


@dataclass(frozen=True)
class CloseoutCheckResult:
    repo_label: str
    repo_path: Path
    evidence_result: EvidenceArchiveCheckResult
    verification_result: VerificationRunResult
    verification_started_at: datetime | None = None
    verification_completed_at: datetime | None = None

    @property
    def exit_code(self) -> int:
        if not self.evidence_result.passed:
            return 1
        if self.verification_result.exit_code != 0:
            return 1
        return 0


def run_closeout_check(
    repo: str,
    change_id: str,
    *,
    surface: str | None = None,
    model: str | None = None,
    reasoning: str | None = None,
    speed: str | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    executor: CommandExecutor | None = None,
    clock: MonotonicClock | None = None,
    verification_clock: Callable[[], datetime] | None = None,
) -> CloseoutCheckResult:
    repo_path = Path(repo).expanduser()
    evidence_result = check_evidence_archive(repo=repo, change_id=change_id)
    if _should_synthesize_late_archive(evidence_result):
        scaffold_evidence_archive(
            repo=repo,
            change_id=change_id,
            surface=surface,
            model=model,
            reasoning=reasoning,
            speed=speed,
            command_label="close",
            started_at="unavailable",
        )
        evidence_result = check_evidence_archive(repo=repo, change_id=change_id)
    elif any(value is not None for value in (surface, model, reasoning, speed)):
        complete_existing_declared_context(
            repo=repo,
            change_id=change_id,
            surface=surface,
            model=model,
            reasoning=reasoning,
            speed=speed,
        )
        evidence_result = check_evidence_archive(repo=repo, change_id=change_id)
    if not _recordable_archive(evidence_result):
        return CloseoutCheckResult(
            repo_label=repo,
            repo_path=repo_path,
            evidence_result=evidence_result,
            verification_result=_skipped_verification_result(
                repo_path,
                reason="evidence archive is not recordable",
            ),
        )

    wall_clock = verification_clock or (lambda: datetime.now(timezone.utc))
    verification_started_at = wall_clock()
    verification_result = run_verification(
        repo_path,
        stdout=stdout,
        stderr=stderr,
        executor=executor,
        clock=clock,
    )
    verification_completed_at = wall_clock()
    return CloseoutCheckResult(
        repo_label=repo,
        repo_path=repo_path,
        evidence_result=evidence_result,
        verification_result=verification_result,
        verification_started_at=verification_started_at,
        verification_completed_at=verification_completed_at,
    )


def with_evidence_result(
    result: CloseoutCheckResult,
    evidence_result: EvidenceArchiveCheckResult,
) -> CloseoutCheckResult:
    return replace(result, evidence_result=evidence_result)


def _recordable_archive(result: EvidenceArchiveCheckResult) -> bool:
    if result.invalid_reason is not None or not result.archive_exists:
        return False
    evidence_file = next(
        (file for file in result.files if file.filename == "evidence.md"),
        None,
    )
    return bool(
        evidence_file
        and evidence_file.exists
        and (evidence_file.front_matter_error is None)
    )


def _should_synthesize_late_archive(result: EvidenceArchiveCheckResult) -> bool:
    return result.invalid_reason is None and not result.archive_exists


def _skipped_verification_result(
    repo_path: Path,
    *,
    reason: str,
) -> VerificationRunResult:
    return VerificationRunResult(
        repo_path=repo_path,
        config_path=repo_path / ".sdf" / "verification.yml",
        status="skipped",
        exit_code=1,
        command_results=(),
        error=reason,
    )
