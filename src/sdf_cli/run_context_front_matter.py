"""Compatibility-free access to supported contract-4 record storage."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
    update_evidence_machine_record,
)


def _evidence_path(repo_path: Path, change_id: str) -> Path:
    return repo_path / ".sdf" / "evidence" / change_id / "evidence.md"


def read_run_context_storage(*, repo_path: Path, change_id: str):
    path = _evidence_path(repo_path, change_id)
    try:
        return load_evidence_machine_record(path, change_id=change_id)
    except EvidenceFrontMatterError:
        return None


def write_run_context_storage(*, repo_path: Path, change_id: str, record) -> bool:
    path = _evidence_path(repo_path, change_id)
    try:
        update_evidence_machine_record(path, change_id=change_id, record=record)
    except EvidenceFrontMatterError:
        return False
    return True
