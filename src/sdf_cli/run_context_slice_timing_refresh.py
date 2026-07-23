"""Close the evidence lifecycle after successful closeout."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    close_evidence_machine_record,
    load_evidence_machine_record,
)


@dataclass(frozen=True)
class RunContextSliceTimingCloseResult:
    path: Path
    closed: bool
    skipped_reason: str | None = None


def close_run_context_slice_timing(
    *, repo: str, change_id: str, clock: Callable[[], datetime] | None = None
) -> RunContextSliceTimingCloseResult:
    path = Path(repo).expanduser() / ".sdf" / "evidence" / change_id / "evidence.md"
    try:
        record = load_evidence_machine_record(path, change_id=change_id)
        if record is None or not record.started_at:
            return RunContextSliceTimingCloseResult(
                path, False, "supported evidence machine record is missing"
            )
        now = (clock or (lambda: datetime.now(timezone.utc)))()
        close_evidence_machine_record(
            path,
            change_id=change_id,
            closed_at=now.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
        )
    except (OSError, EvidenceFrontMatterError):
        return RunContextSliceTimingCloseResult(
            path, False, "evidence lifecycle close failed"
        )
    return RunContextSliceTimingCloseResult(path, True)
