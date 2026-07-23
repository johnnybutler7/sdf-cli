"""Safe merging for the shared receiver ``.gitattributes`` file."""

from __future__ import annotations

from pathlib import Path

SDF_EVIDENCE_GENERATED_ATTRIBUTE = ".sdf/evidence/** linguist-generated=true"


def has_sdf_evidence_generated_attribute(content: str) -> bool:
    """Return whether the exact SDF evidence attribute is already present."""
    return SDF_EVIDENCE_GENERATED_ATTRIBUTE in content.splitlines()


def merged_sdf_evidence_generated_attribute(content: str) -> str:
    """Append the SDF attribute without changing unrelated receiver content."""
    if has_sdf_evidence_generated_attribute(content):
        return content
    prefix = content if not content or content.endswith("\n") else f"{content}\n"
    return f"{prefix}{SDF_EVIDENCE_GENERATED_ATTRIBUTE}\n"


def ensure_sdf_evidence_generated_attribute(path: Path) -> str:
    """Create, update, or preserve the shared attributes file safely."""
    if not path.exists():
        path.write_text(SDF_EVIDENCE_GENERATED_ATTRIBUTE + "\n", encoding="utf-8")
        return "created"

    content = path.read_text(encoding="utf-8")
    if has_sdf_evidence_generated_attribute(content):
        return "current"

    path.write_text(
        merged_sdf_evidence_generated_attribute(content), encoding="utf-8"
    )
    return "updated"
