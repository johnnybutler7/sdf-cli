"""Scaffold placeholder detection for evidence archive readiness."""

from __future__ import annotations

from dataclasses import dataclass

from sdf_cli.evidence_archive_contract import CONTRACT_FIVE_JUDGEMENT_HEADINGS


@dataclass(frozen=True)
class EvidenceArchivePlaceholder:
    section: str
    marker: str


SCAFFOLD_PLACEHOLDER_MARKERS: dict[str, dict[str, tuple[str, ...]]] = {
    "evidence.md": {
        "## Request / Provenance": (
            "- Request: TBD.",
            "- Source/provenance: TBD.",
            "- Source/provenance: note the operator request",
            "- Reference precedent: note any reference runtime",
        ),
        "## Change Summary": (
            "- Change summary: TBD.",
            "- Changed surface: TBD.",
            "- Summarize the change in 1-4 reviewer-ready bullets.",
            "- Name the primary changed files",
        ),
        "## Acceptance / Review Focus": (
            "- Review focus: TBD.",
            "- Acceptance checks: TBD.",
            "- Deferred scope affecting review: TBD.",
            "- List concrete review targets or acceptance checks.",
            "- Call out wording, behavior, compatibility",
        ),
        "## Scope": ("- In scope: TBD.", "- Out of scope: TBD."),
        "## Boundaries / Non-Claims": ("- Slice-specific non-claims: TBD.",),
        "## Risk / Confidence / Limits": (
            "- Risk: TBD.",
            "- Confidence: TBD.",
            "- Limits: TBD.",
        ),
        "### Consulted": ("- Guidance consulted: TBD.",),
        "### Commands": (
            "- Command: not run yet.",
            "  - Status: not run yet.",
        ),
        "### Results": (
            "- Reviewer interpretation or material verification limitation: TBD.",
        ),
        "## Handoff / Reviewer Notes": (
            "- Reviewer notes: TBD.",
            "- Handoff links or follow-up: TBD.",
        ),
    },
}


def unresolved_scaffold_placeholders(
    filename: str,
    markdown: str,
    *,
    contract_version: int = 5,
) -> tuple[EvidenceArchivePlaceholder, ...]:
    if filename == "evidence.md" and contract_version >= 5:
        return unresolved_contract_five_judgement_fields(markdown)

    findings: list[EvidenceArchivePlaceholder] = []
    for section, markers in SCAFFOLD_PLACEHOLDER_MARKERS.get(filename, {}).items():
        section_text = markdown_section(markdown, section)
        for marker in markers:
            if marker in section_text:
                findings.append(
                    EvidenceArchivePlaceholder(section=section, marker=marker)
                )
    return tuple(findings)


def unresolved_contract_five_judgement_fields(
    markdown: str,
) -> tuple[EvidenceArchivePlaceholder, ...]:
    findings: list[EvidenceArchivePlaceholder] = []
    for heading in CONTRACT_FIVE_JUDGEMENT_HEADINGS:
        if _is_unresolved_judgement(markdown_section(markdown, heading)):
            findings.append(
                EvidenceArchivePlaceholder(
                    section=heading,
                    marker="needs judgement",
                )
            )
    return tuple(findings)


def markdown_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    section_lines: list[str] = []
    in_section = False

    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and _ends_section(line, heading):
            break
        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines)


def _is_unresolved_judgement(section: str) -> bool:
    meaningful = [
        line.strip()
        for line in section.splitlines()
        if line.strip() and not line.strip().startswith("<!--")
    ]
    if not meaningful:
        return True
    unresolved_values = {
        "tbd",
        "tbd.",
        "todo",
        "todo.",
        "unknown",
        "unknown.",
        "unavailable",
        "unavailable.",
        "not recorded",
        "not recorded.",
        "not recorded yet",
        "not recorded yet.",
    }
    return all(_plain_text(line).casefold() in unresolved_values for line in meaningful)


def _plain_text(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith(("- ", "* ")):
        stripped = stripped[2:].strip()
    return stripped


def _ends_section(line: str, heading: str) -> bool:
    return line.startswith("#") and len(line) - len(line.lstrip("#")) <= len(
        heading.split(" ", 1)[0]
    )
