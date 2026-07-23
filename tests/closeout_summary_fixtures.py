"""Test fixtures for closeout handoff rendering tests."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from tests.evidence_archive_helpers import populated_template_for

from sdf_cli.evidence_archive_contract import CONTRACT_FOUR_ARCHIVE_HEADINGS
from sdf_cli.evidence_front_matter import (
    initialize_evidence_machine_record,
    update_declared_run_context,
)


def write_archive(
    repo: Path,
    change_id: str,
    *,
    change_summary_lines: Optional[list[str]] = None,
    focus_lines: Optional[list[str]] = None,
    boundary_lines: Optional[list[str]] = None,
    run_context_lines: Optional[list[str]] = None,
    branch_lines: Optional[list[str]] = None,
    verification_lines: Optional[list[str]] = None,
    command_lines: Optional[list[str]] = None,
    playbook_applied_lines: Optional[list[str]] = None,
    playbook_consulted_lines: Optional[list[str]] = None,
) -> None:
    archive = repo / ".sdf" / "evidence" / change_id
    archive.mkdir(parents=True)
    content = populated_template_for("evidence.md")
    content = replace_section(content, "## Change Summary", change_summary_lines)
    content = replace_section(content, "## Acceptance / Review Focus", focus_lines)
    content = replace_section(content, "## Boundaries / Non-Claims", boundary_lines)
    content = replace_section(content, "### Results", verification_lines)
    content = replace_section(content, "### Commands", command_lines)
    content = replace_section(content, "## Run / Handoff Context", run_context_lines)
    content = replace_section(content, "### Applied", playbook_applied_lines)
    content = replace_section(content, "### Consulted", playbook_consulted_lines)
    for heading in CONTRACT_FOUR_ARCHIVE_HEADINGS:
        assert heading in content
    evidence = archive / "evidence.md"
    evidence.write_text(content, encoding="utf-8")
    initialize_evidence_machine_record(
        evidence,
        change_id=change_id,
        started_at="2026-01-01T09:00:00+00:00",
        contract_version=4,
    )


def write_run_context(
    repo: Path,
    change_id: str,
    *,
    surface: str = "codex_local",
    model: str = "gpt-5.5",
    reasoning: str = "medium",
    speed: str = "fast",
    basis: str = "declared",
    provider: Optional[str] = None,
    provider_basis: Optional[str] = None,
    declared_by: Optional[str] = None,
    declared_fields: Optional[dict[str, str]] = None,
    unknowns: Optional[list[str]] = None,
    slice_timing_lines: Optional[list[str]] = None,
) -> None:
    archive = repo / ".sdf" / "evidence" / change_id
    archive.mkdir(parents=True, exist_ok=True)
    declared_values = declared_fields or {
        "surface": surface,
        "model": model,
        "reasoning": reasoning,
        "speed": speed,
    }
    evidence = archive / "evidence.md"
    if not evidence.is_file():
        evidence.write_text(populated_template_for("evidence.md"), encoding="utf-8")
    try:
        update_declared_run_context(
            evidence,
            change_id=change_id,
            declared={
                field: declared_values.get(field, "unknown")
                for field in ("surface", "model", "reasoning", "speed")
            },
        )
        return
    except ValueError:
        initialize_evidence_machine_record(
            evidence,
            change_id=change_id,
            started_at="2026-01-01T09:00:00+00:00",
            contract_version=4,
        )
    update_declared_run_context(
        evidence,
        change_id=change_id,
        declared={
            field: declared_values.get(field, "unknown")
            for field in ("surface", "model", "reasoning", "speed")
        },
    )


def replace_section(
    markdown: str,
    heading: str,
    lines: Optional[list[str]],
) -> str:
    if lines is None:
        return markdown

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


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


def write_sentinel_verification_config(repo: Path, sentinel: Path) -> None:
    write_verification_config(
        repo,
        f"""
version: 1
commands:
  - name: would-write-sentinel
    command: {sentinel_command(sentinel)}
""",
    )


def sentinel_command(sentinel: Path) -> str:
    return (
        "python3 -c "
        f"\"from pathlib import Path; Path({str(sentinel)!r}).write_text('ran')\""
    )


def write_verification_counter(repo: Path, marker: Path) -> None:
    command = (
        "from pathlib import Path; "
        f"path = Path({str(marker)!r}); "
        "count = int(path.read_text()) if path.exists() else 0; "
        "path.write_text(str(count + 1))"
    )
    write_verification_config(
        repo,
        f"""
version: 1
commands:
  - name: count-verification
    command: python3 -c "{command}"
""",
    )
