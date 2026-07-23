"""Version-aware helpers for evidence archive checks."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.evidence_archive_contract import (
    CONTRACT_FOUR_REQUIRED_ARCHIVE_HEADINGS,
    GUIDANCE_APPLIED_HEADINGS,
    REQUIRED_ARCHIVE_HEADINGS,
    VERIFICATION_HEADINGS,
)
from sdf_cli.evidence_front_matter import (
    EvidenceFrontMatterError,
    load_evidence_machine_record,
)


def required_headings_for(
    filename: str,
    *,
    contract_version: int | None,
    embedded_verification: bool,
) -> tuple[str, ...]:
    if filename != "evidence.md":
        return REQUIRED_ARCHIVE_HEADINGS[filename]
    if contract_version == 4:
        return CONTRACT_FOUR_REQUIRED_ARCHIVE_HEADINGS[filename]
    if contract_version == 5:
        return REQUIRED_ARCHIVE_HEADINGS[filename]
    return (
        *REQUIRED_ARCHIVE_HEADINGS[filename],
        *GUIDANCE_APPLIED_HEADINGS,
        *(VERIFICATION_HEADINGS if embedded_verification else ()),
    )


def front_matter_status(
    path: Path, filename: str, change_id: str
) -> tuple[str | None, int | None]:
    if filename != "evidence.md":
        return None, None
    try:
        record = load_evidence_machine_record(path, change_id=change_id)
    except (OSError, EvidenceFrontMatterError) as error:
        return str(error), None
    return None, record.contract_version if record else None
