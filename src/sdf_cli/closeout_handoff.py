"""Composed local closeout handoff workflow."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TextIO

from sdf_cli.closeout_check import (
    CloseoutCheckResult,
    run_closeout_check,
    with_evidence_result,
)
from sdf_cli.closeout_handoff_rendering import render_closeout_handoff
from sdf_cli.closeout_result_record import (
    write_closeout_status_record,
    write_verification_result_record,
)
from sdf_cli.evidence_archive_check import check_evidence_archive
from sdf_cli.pr_body import (
    PrBodyWriteResult,
    write_pr_body_artifact,
)
from sdf_cli.pr_body_check import PrBodyCheckResult, check_pr_body_artifact
from sdf_cli.pr_body_links import LINK_MODE_REPO_RELATIVE
from sdf_cli.run_context_slice_timing_refresh import close_run_context_slice_timing
from sdf_cli.verification_runner import CommandExecutor, MonotonicClock

__all__ = (
    "CloseoutHandoffResult",
    "render_closeout_handoff",
    "run_closeout_handoff",
)


@dataclass(frozen=True)
class CloseoutHandoffResult:
    change_id: str
    closeout_result: CloseoutCheckResult
    write_result: PrBodyWriteResult | None = None
    check_result: PrBodyCheckResult | None = None
    closeout_record_written: bool = False
    @property
    def exit_code(self) -> int:
        if self.closeout_result.exit_code != 0:
            return 1
        if self.write_result is None:
            return 1
        if not self.write_result.written and not self.write_result.existing:
            return 1
        if self.check_result is None or self.check_result.exit_code != 0:
            return 1
        return 0


def run_closeout_handoff(
    repo: str,
    change_id: str,
    *,
    overwrite: bool = False,
    surface: str | None = None,
    model: str | None = None,
    reasoning: str | None = None,
    speed: str | None = None,
    link_mode: str = LINK_MODE_REPO_RELATIVE,
    github_repo: str | None = None,
    github_ref: str | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    executor: CommandExecutor | None = None,
    clock: MonotonicClock | None = None,
    slice_timing_clock: Callable[[], datetime] | None = None,
    verification_clock: Callable[[], datetime] | None = None,
) -> CloseoutHandoffResult:
    closeout_result = run_closeout_check(
        repo=repo,
        change_id=change_id,
        surface=surface,
        model=model,
        reasoning=reasoning,
        speed=speed,
        stdout=stdout,
        stderr=stderr,
        executor=executor,
        clock=clock,
        verification_clock=verification_clock,
    )
    verification_record_written = write_verification_result_record(
        repo=repo,
        result=closeout_result,
    )
    if verification_record_written:
        closeout_result = with_evidence_result(
            closeout_result,
            check_evidence_archive(repo=repo, change_id=change_id),
        )
    closeout_record_written = write_closeout_status_record(
        repo=repo,
        result=closeout_result,
        clock=slice_timing_clock,
    )
    if closeout_result.exit_code != 0:
        return CloseoutHandoffResult(
            change_id=change_id,
            closeout_result=closeout_result,
            closeout_record_written=closeout_record_written,
        )
    close_run_context_slice_timing(
        repo=repo,
        change_id=change_id,
        clock=slice_timing_clock,
    )
    write_result = write_pr_body_artifact(
        repo=repo,
        change_id=change_id,
        overwrite=overwrite,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
        closeout_result=closeout_result,
    )
    if write_result.exit_code != 0 and not write_result.existing:
        return CloseoutHandoffResult(
            change_id=change_id,
            closeout_result=closeout_result,
            write_result=write_result,
            closeout_record_written=closeout_record_written,
        )
    check_result = check_pr_body_artifact(
        repo=repo,
        change_id=change_id,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    return CloseoutHandoffResult(
        change_id=change_id,
        closeout_result=closeout_result,
        write_result=write_result,
        check_result=check_result,
        closeout_record_written=closeout_record_written,
    )
