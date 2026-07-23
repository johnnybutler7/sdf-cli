"""Read compact evidence verification facts for reviewer handoff text."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
)


def verification_history_line(result) -> str | None:
    if result.verification_result.exit_code != 0:
        return None
    archive = Path(result.repo_path) / result.evidence_result.archive_path
    try:
        record = load_evidence_machine_record(
            archive / "evidence.md", change_id=archive.name
        )
    except EvidenceFrontMatterError:
        return None
    if record is None or record.total_runs == 0:
        return None
    recovery = (
        "followed an earlier verification failure"
        if record.final_pass_followed_earlier_failure
        else "did not follow an earlier verification failure"
    )
    noun = "run" if record.total_runs == 1 else "runs"
    return f"- Verification history: {record.total_runs} {noun}; final pass {recovery}."
