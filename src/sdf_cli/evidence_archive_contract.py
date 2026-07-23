"""Evidence archive file and heading contract."""

from __future__ import annotations

EVIDENCE_ARCHIVE_CONTRACT_VERSION = 5
CURRENT_NARRATIVE_FILENAME = "evidence.md"

ROUTINE_EVIDENCE_FILES: tuple[str, ...] = (
    CURRENT_NARRATIVE_FILENAME,
)
VERIFICATION_COMMAND_STATUS_MARKER = "Status:"
VERIFICATION_TIMING_STATUS_MARKER = "Timing:"
VERIFICATION_TRACKED_TIMINGS_MARKER = "Tracked timings:"

CONTRACT_FOUR_ARCHIVE_HEADINGS: tuple[str, ...] = (
    "# Evidence",
    "## Request / Provenance",
    "## Change Summary",
    "## Acceptance / Review Focus",
    "## Scope",
    "## Boundaries / Non-Claims",
    "## Risk / Confidence / Limits",
    "## Guidance Applied",
    "## Verification",
    "## Run / Handoff Context",
    "## Handoff / Reviewer Notes",
)

CONTRACT_FIVE_JUDGEMENT_HEADINGS: tuple[str, ...] = (
    "## Intent",
    "## Review focus",
    "## Limits",
    "## Guidance applied",
)

CONTRACT_FIVE_ARCHIVE_HEADINGS: tuple[str, ...] = (
    "# Evidence",
    *CONTRACT_FIVE_JUDGEMENT_HEADINGS,
    "## Machine Record",
)

GUIDANCE_APPLIED_HEADINGS: tuple[str, ...] = (
    "### Consulted",
    "### Applied",
    "### Not Applicable",
    "### Why This Mattered",
    "### Gaps / Learning",
)

VERIFICATION_HEADINGS: tuple[str, ...] = (
    "### Commands",
    "### Results",
    "### Blockers / Skips",
)

REQUIRED_ARCHIVE_HEADINGS: dict[str, tuple[str, ...]] = {
    "evidence.md": CONTRACT_FIVE_ARCHIVE_HEADINGS,
}

CONTRACT_FOUR_REQUIRED_ARCHIVE_HEADINGS: dict[str, tuple[str, ...]] = {
    "evidence.md": (
        *CONTRACT_FOUR_ARCHIVE_HEADINGS,
        *GUIDANCE_APPLIED_HEADINGS,
        *VERIFICATION_HEADINGS,
    ),
}

def verification_section_heading(filename: str, section: str) -> str:
    """Return the versioned Markdown heading for a verification subsection."""
    return f"### {section}"


def narrative_label(filename: str) -> str:
    labels = {
        "evidence.md": "Evidence notes",
    }
    return labels[filename]
