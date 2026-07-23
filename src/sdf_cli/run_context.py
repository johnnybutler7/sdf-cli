"""Read declared context from supported evidence machine records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
)

UNKNOWN_VALUE = "unknown"
DECLARED_CONTEXT_FIELDS = ("surface", "model", "reasoning", "speed")


@dataclass(frozen=True)
class RunContextArtifact:
    path: Path
    change_id: str
    declared: dict[str, str]
    started_at: str | None
    closed_at: str | None
    valid: bool
    errors: tuple[str, ...] = ()

    def declared_value(self, field: str) -> str:
        return self.declared.get(field) or UNKNOWN_VALUE


def run_context_path(repo_path: Path, archive_path: str | Path) -> Path:
    return repo_path / archive_path / "evidence.md"


def load_run_context(
    repo_path: Path, archive_path: str | Path
) -> RunContextArtifact | None:
    path = run_context_path(repo_path, archive_path)
    if not path.is_file():
        return None
    try:
        record = load_evidence_machine_record(path, change_id=Path(archive_path).name)
    except (OSError, EvidenceFrontMatterError) as error:
        return RunContextArtifact(
            path=path,
            change_id="",
            declared={},
            started_at=None,
            closed_at=None,
            valid=False,
            errors=(str(error),),
        )
    if record is None:
        return None
    return RunContextArtifact(
        path=path,
        change_id=record.change_id,
        declared=record.declared,
        started_at=record.started_at,
        closed_at=record.closed_at,
        valid=True,
    )
