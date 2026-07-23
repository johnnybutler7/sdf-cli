"""Helpers for writing archive fixtures that represent populated evidence."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.evidence_archive_templates import contract_four_template_for, template_for
from sdf_cli.evidence_front_matter import initialize_evidence_machine_record

POPULATED_SECTIONS: dict[str, dict[str, list[str]]] = {
    "evidence.md": {
        "## Request / Provenance": [
            "- Request: exercise archive readiness fixture.",
            "- Source/provenance: local test fixture.",
            "- Reference precedent: not consulted for this fixture.",
        ],
        "## Change Summary": [
            "- Populated archive fixture records concrete review evidence.",
        ],
        "## Acceptance / Review Focus": [
            "- Confirm archive readiness accepts populated evidence.",
        ],
        "## Scope": [
            "- In scope: archive readiness fixture.",
            "- Out of scope: production behavior beyond this fixture.",
        ],
        "## Boundaries / Non-Claims": [
            "- Standard SDF non-claims: see `.sdf/standard-sdf-non-claims.md`.",
            "- Slice-specific non-claims: fixture does not prove correctness.",
        ],
        "## Risk / Confidence / Limits": [
            "- Risk: low fixture risk.",
            "- Confidence: sufficient for command tests.",
            "- Limits: fixture content is intentionally compact.",
        ],
        "### Consulted": [
            "- `.sdf/playbooks/governed-change-loop.md`",
        ],
        "### Applied": [
            "- Governed change loop - kept fixture evidence explicit and populated.",
        ],
        "### Not Applicable": ["- None."],
        "### Why This Mattered": [
            "- Fixture distinguishes populated evidence from scaffold prompts.",
        ],
        "### Gaps / Learning": [
            "- Gaps: none for fixture.",
            "- Learning: fixture supports archive readiness tests.",
        ],
        "### Commands": [
            "- Command: `python3 -m unittest tests.fixture`",
            "  - Status: passed.",
        ],
        "### Results": [
            "- Final closeout result: populated fixture ready.",
            "- Reviewer-ready summary: fixture command status was recorded.",
            "- Verification limits: fixture does not run product verification.",
        ],
        "### Blockers / Skips": [
            "- Skips: none.",
            "- Blockers: none.",
            "- Failed-then-fixed attempts: none.",
        ],
        "### Evidence Output": [
            "- Evidence artifacts: populated archive fixture.",
            "- Output summary: fixture output only.",
        ],
        "## Run / Handoff Context": [
            "- Repository / branch context: fixture context is recorded.",
            "- Material execution or handoff notes: fixture archive was populated.",
            "- Unknowns: fixture has no material unknowns.",
        ],
        "## Handoff / Reviewer Notes": [
            "- Reviewer notes: populated fixture.",
            "- Handoff links or follow-up: none.",
        ],
    },
}


def populated_template_for(filename: str) -> str:
    content = contract_four_template_for(filename)
    for heading, lines in POPULATED_SECTIONS[filename].items():
        content = replace_section(content, heading, lines)
    return content


def write_current_archive(repo: Path, change_id: str) -> None:
    archive = repo / ".sdf" / "evidence" / change_id
    archive.mkdir(parents=True)
    evidence = archive / "evidence.md"
    evidence.write_text(populated_template_for("evidence.md"), encoding="utf-8")
    initialize_evidence_machine_record(
        evidence,
        change_id=change_id,
        started_at="2026-01-01T09:00:00+00:00",
        contract_version=4,
    )


def current_template_for(filename: str) -> str:
    return template_for(filename)


def replace_section(markdown: str, heading: str, lines: list[str]) -> str:
    original_lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    while index < len(original_lines):
        line = original_lines[index]
        output.append(line)
        index += 1
        if line != heading:
            continue

        if index < len(original_lines) and original_lines[index] == "":
            output.append("")
            index += 1
        output.extend(lines)
        heading_level = len(heading.split(" ", 1)[0])
        while index < len(original_lines) and not (
            original_lines[index].startswith("#")
            and len(original_lines[index]) - len(original_lines[index].lstrip("#"))
            <= heading_level
        ):
            index += 1

    return "\n".join(output) + "\n"
