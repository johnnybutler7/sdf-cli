"""Run-context section rendering for closeout summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sdf_cli.closeout_run_context_artifact import render_run_context_artifact_lines
from sdf_cli.run_context import (
    load_run_context,
)


def run_context_lines(result: Any) -> list[str]:
    archive_path = result.evidence_result.archive_path
    lines = [f"- Change ID: `{result.evidence_result.change_id}`"]
    run_context = load_run_context(Path(result.repo_path), archive_path)
    if run_context is not None:
        lines.extend(render_run_context_artifact_lines(run_context))
        return _truncate_with_required_line(
            lines,
            f"- Run-context evidence: `{archive_path}/evidence.md`",
            max_lines=8,
        )

    lines.extend(_review_context_lines(result))
    return _truncate_with_required_line(
        lines,
        f"- Evidence notes: `{archive_path}/evidence.md`",
        max_lines=8,
    )

def _review_context_lines(result: Any) -> list[str]:
    lines: list[str] = []
    context_lines = _archive_section_lines(
        result, "evidence.md", "## Run / Handoff Context"
    )
    for line in context_lines[:4]:
        text = _strip_list_marker(line)
        if text:
            lines.append(f"- Context: {text}")
    return lines


def _archive_section_lines(result: Any, filename: str, heading: str) -> list[str]:
    text = _archive_file_text(result, filename)
    if text is None:
        return []

    section = _markdown_section(text, heading)
    return _concise_markdown_lines(section) if section else []


def _archive_file_text(result: Any, filename: str) -> str | None:
    path = Path(result.repo_path) / result.evidence_result.archive_path / filename
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _markdown_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    section_lines: list[str] = []
    in_section = False

    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def _concise_markdown_lines(markdown: str) -> list[str]:
    lines: list[str] = []
    for line in markdown.splitlines():
        if not line.strip() or line.strip() == "TBD.":
            continue
        if line[:1].isspace() and lines:
            lines[-1] = f"{lines[-1]} {line.strip()}"
        else:
            lines.append(line.rstrip())

    return lines[:8]


def _truncate_with_required_line(
    lines: list[str],
    required_line: str,
    *,
    max_lines: int,
) -> list[str]:
    if max_lines <= 1:
        return [required_line]

    section_lines = [line for line in lines if line != required_line]
    if len(section_lines) >= max_lines:
        return section_lines[: max_lines - 1] + [required_line]

    return section_lines + [required_line]


def _strip_list_marker(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith(("- ", "* ")):
        return stripped[2:].strip()
    return stripped
