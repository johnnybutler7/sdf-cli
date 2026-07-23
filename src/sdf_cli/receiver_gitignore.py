"""Safe merging for the shared receiver ``.gitignore`` file."""

from __future__ import annotations

from pathlib import Path

SDF_HANDOFFS_IGNORE_RULE = ".sdf/handoffs/"
SDF_HANDOFFS_EQUIVALENT_RULES = {
    ".sdf/handoffs",
    ".sdf/handoffs/",
    ".sdf/handoffs/**",
    "/.sdf/handoffs",
    "/.sdf/handoffs/",
    "/.sdf/handoffs/**",
}


def has_sdf_handoffs_ignore_rule(content: str) -> bool:
    """Return whether an SDF handoffs ignore rule is already present."""
    return any(
        line.strip() in SDF_HANDOFFS_EQUIVALENT_RULES
        for line in content.splitlines()
    )


def merged_sdf_handoffs_ignore_rule(content: str) -> str:
    """Append the SDF handoffs ignore rule without changing receiver content."""
    if has_sdf_handoffs_ignore_rule(content):
        return content
    prefix = content if not content or content.endswith("\n") else f"{content}\n"
    return f"{prefix}{SDF_HANDOFFS_IGNORE_RULE}\n"


def ensure_sdf_handoffs_ignore_rule(path: Path) -> str:
    """Create, update, or preserve the shared ignore file safely."""
    if not path.exists():
        path.write_text(SDF_HANDOFFS_IGNORE_RULE + "\n", encoding="utf-8")
        return "created"

    content = path.read_text(encoding="utf-8")
    if has_sdf_handoffs_ignore_rule(content):
        return "current"

    path.write_text(merged_sdf_handoffs_ignore_rule(content), encoding="utf-8")
    return "updated"
