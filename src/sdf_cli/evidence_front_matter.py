"""Safe read and update support for evidence machine records."""

from __future__ import annotations

import os
import tempfile
from dataclasses import replace
from pathlib import Path

from sdf_cli import __version__
from sdf_cli.evidence_contract import (
    DECLARED_FIELDS,
    EVIDENCE_ARCHIVE_CONTRACT,
    MACHINE_RECORD_HEADING,
    EvidenceMachineRecord,
    EvidenceMachineRecordError,
    read_machine_record,
    render_machine_record,
)
from sdf_cli.evidence_machine_context import branch_context, repository_context

EvidenceFrontMatterError = EvidenceMachineRecordError


def initialize_evidence_machine_record(
    path: Path,
    *,
    change_id: str,
    started_at: str,
    contract_version: int = EVIDENCE_ARCHIVE_CONTRACT,
    repo_path: Path | None = None,
) -> None:
    """Append the owned record to a newly scaffolded document only."""
    original = path.read_bytes()
    if MACHINE_RECORD_HEADING.encode() in original:
        read_machine_record(original, change_id=change_id)
        return
    record = EvidenceMachineRecord(
        contract_version=contract_version,
        change_id=change_id,
        written_by=f"software-dark-factory {__version__}",
        repository=repository_context(repo_path),
        branch=branch_context(repo_path),
        declared={field: "unknown" for field in DECLARED_FIELDS},
        started_at=started_at,
        closed_at=None,
        closeout_status="open",
        total_runs=0,
        failed_runs=0,
        final_pass_followed_earlier_failure=False,
        latest_run=None,
        body=original,
        yaml_start=0,
        yaml_end=0,
    )
    suffix = "\n" if original and not original.endswith(b"\n") else ""
    suffix += (
        f"{MACHINE_RECORD_HEADING}\n\n```yaml\n{render_machine_record(record)}```\n"
    )
    _atomic_replace(path, original + suffix.encode("utf-8"))


def load_evidence_machine_record(
    path: Path, *, change_id: str
) -> EvidenceMachineRecord | None:
    return (
        read_machine_record(path.read_bytes(), change_id=change_id)
        if path.is_file()
        else None
    )


def update_evidence_machine_record(
    path: Path, *, change_id: str, record: EvidenceMachineRecord
) -> None:
    original = path.read_bytes()
    document = read_machine_record(original, change_id=change_id)
    updated = (
        original[: document.yaml_start]
        + render_machine_record(record).encode("utf-8")
        + original[document.yaml_end :]
    )
    _atomic_replace(path, updated)
    if (
        read_machine_record(path.read_bytes(), change_id=change_id).body
        != document.body
    ):
        raise EvidenceFrontMatterError(
            "evidence.md narrative changed during machine-record update"
        )


def update_declared_run_context(
    path: Path, *, change_id: str, declared: dict[str, str]
) -> None:
    record = load_evidence_machine_record(path, change_id=change_id)
    if record is None:
        raise EvidenceFrontMatterError("evidence.md machine record is missing")
    update_evidence_machine_record(
        path,
        change_id=change_id,
        record=replace(
            record, declared={field: declared[field] for field in DECLARED_FIELDS}
        ),
    )


def complete_declared_run_context(
    path: Path, *, change_id: str, supplied: dict[str, str | None]
) -> bool:
    record = load_evidence_machine_record(path, change_id=change_id)
    if record is None:
        raise EvidenceFrontMatterError("evidence.md machine record is missing")
    declared = dict(record.declared)
    changed = False
    for field in DECLARED_FIELDS:
        value = supplied.get(field)
        if value is None or declared.get(field) not in ("unknown", "unavailable"):
            continue
        declared[field] = value
        changed = True
    if not changed:
        return False
    update_evidence_machine_record(
        path,
        change_id=change_id,
        record=replace(record, declared=declared),
    )
    return True


def close_evidence_machine_record(
    path: Path, *, change_id: str, closed_at: str
) -> None:
    record = load_evidence_machine_record(path, change_id=change_id)
    if record is None:
        raise EvidenceFrontMatterError("evidence.md machine record is missing")
    update_evidence_machine_record(
        path, change_id=change_id, record=replace(record, closed_at=closed_at)
    )


def _atomic_replace(path: Path, data: bytes) -> None:
    if not path.parent.is_dir():
        raise EvidenceFrontMatterError("evidence.md parent directory is missing")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise EvidenceFrontMatterError(
            f"could not atomically update evidence.md: {error}"
        ) from error
