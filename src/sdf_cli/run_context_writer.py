"""Write declared context into a supported contract-4 evidence record."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
    update_declared_run_context,
)


@dataclass(frozen=True)
class RunContextWriteResult:
    change_id: str
    artifact_path: str
    written: bool
    skipped_reason: str | None = None
    failed: bool = False

    @property
    def exit_code(self) -> int:
        return 1 if self.failed else 0


def write_run_context_artifact(
    *,
    repo: str,
    change_id: str,
    surface: str | None = None,
    model: str | None = None,
    reasoning: str | None = None,
    speed: str | None = None,
    clock=None,
) -> RunContextWriteResult:
    artifact_path = run_context_artifact_path(change_id)
    evidence_path = Path(repo).expanduser() / artifact_path
    try:
        record = load_evidence_machine_record(evidence_path, change_id=change_id)
    except (OSError, EvidenceFrontMatterError) as error:
        return RunContextWriteResult(
            change_id, artifact_path, False, str(error), failed=True
        )
    if record is None:
        return RunContextWriteResult(
            change_id,
            artifact_path,
            False,
            "evidence.md machine record is missing; run sdf start first",
            failed=True,
        )
    supplied = {
        field: value
        for field, value in {
            "surface": surface,
            "model": model,
            "reasoning": reasoning,
            "speed": speed,
        }.items()
        if value is not None
    }
    if not supplied:
        return RunContextWriteResult(
            change_id,
            artifact_path,
            False,
            "already exists; no declared run-context values supplied",
        )
    declared = {**record.declared, **supplied}
    try:
        update_declared_run_context(
            evidence_path, change_id=change_id, declared=declared
        )
    except (OSError, EvidenceFrontMatterError) as error:
        return RunContextWriteResult(
            change_id,
            artifact_path,
            False,
            f"evidence.md update failed safely: {error}",
            failed=True,
        )
    return RunContextWriteResult(change_id, artifact_path, True)


def run_context_artifact_path(change_id: str) -> str:
    return f".sdf/evidence/{change_id}/evidence.md"
