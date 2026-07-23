from __future__ import annotations

from pathlib import Path

from tests.closeout_summary_fixtures import replace_section, write_verification_config

from sdf_cli.evidence_archive_templates import template_for
from sdf_cli.evidence_front_matter import (
    initialize_evidence_machine_record,
    update_declared_run_context,
)


def write_contract_five_archive(
    repo: Path,
    change_id: str,
    *,
    intent: list[str] | None = None,
    review_focus: list[str] | None = None,
    limits: list[str] | None = None,
    guidance: list[str] | None = None,
    declared: dict[str, str] | None = None,
) -> None:
    archive = repo / ".sdf" / "evidence" / change_id
    archive.mkdir(parents=True)
    content = template_for("evidence.md")
    content = replace_section(
        content,
        "## Intent",
        intent or ["- Exercise contract-5 reviewer handoff generation."],
    )
    content = replace_section(
        content,
        "## Review focus",
        review_focus or ["- Review the generated PR body projection."],
    )
    content = replace_section(
        content,
        "## Limits",
        limits or ["- None material."],
    )
    content = replace_section(
        content,
        "## Guidance applied",
        guidance or ["- None material for this fixture."],
    )
    evidence = archive / "evidence.md"
    evidence.write_text(content, encoding="utf-8")
    initialize_evidence_machine_record(
        evidence,
        change_id=change_id,
        started_at="unavailable",
        contract_version=5,
        repo_path=repo,
    )
    if declared is not None:
        update_declared_run_context(evidence, change_id=change_id, declared=declared)


def known_context() -> dict[str, str]:
    return {
        "surface": "codex_local",
        "model": "gpt-5.5",
        "reasoning": "medium",
        "speed": "fast",
    }


def write_passing_verification(repo: Path, *, check_count: int = 1) -> None:
    commands = []
    for index in range(1, check_count + 1):
        commands.extend(
            [
                f"  - name: check-{index}",
                "    command: python3 -c \"print('ok')\"",
            ]
        )
    write_verification_config(repo, "version: 1\ncommands:\n" + "\n".join(commands))
