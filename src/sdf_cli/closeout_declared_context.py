"""Close-only declared run-context completion policy."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    complete_declared_run_context,
)


def complete_existing_declared_context(
    *,
    repo: str,
    change_id: str,
    surface: str | None,
    model: str | None,
    reasoning: str | None,
    speed: str | None,
) -> None:
    evidence_path = Path(repo).expanduser() / ".sdf" / "evidence" / change_id
    evidence_path /= "evidence.md"
    try:
        complete_declared_run_context(
            evidence_path,
            change_id=change_id,
            supplied={
                "surface": surface,
                "model": model,
                "reasoning": reasoning,
                "speed": speed,
            },
        )
    except (OSError, EvidenceFrontMatterError):
        return
