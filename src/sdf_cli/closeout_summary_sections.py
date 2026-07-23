"""Section helpers for closeout summary Markdown rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sdf_cli.evidence_archive_contract import narrative_filename

APPLIED_PLAYBOOK_LINE_LIMIT = 5
CONSULTED_PLAYBOOK_FALLBACK_LIMIT = 3

PLAYBOOK_TEMPLATE_PREFIXES = (
    "Exact guidance paths consulted, one per bullet.",
    "Use repo-relative paths such as ",
    "Mark source/reference artifacts separately from playbooks",
    "Playbook/guidance label - ",
    "Name what the playbook changed:",
    "Keep bullets concise enough to feed compact PR handoff ",
    "Guidance path - not applicable because TBD.",
    "Record playbooks considered but not materially shaping this slice.",
)
def what_reviewing_lines(result: Any) -> list[str]:
    filename = _narrative_filename(result)
    lines = archive_section_lines(result, filename, "## Change Summary")
    if not lines:
        lines = archive_section_lines(result, filename, "## Intent")
    if lines:
        return with_fallback_bullets(lines)

    return [
        f"- Change ID: `{result.evidence_result.change_id}`",
        f"- Change summary was not extracted from `{filename}`.",
    ]
def review_focus_lines(result: Any) -> list[str]:
    filename = _narrative_filename(result)
    focus_lines = archive_section_lines(
        result,
        filename,
        "## Acceptance / Review Focus",
    )
    if not focus_lines:
        focus_lines = archive_section_lines(result, filename, "## Review focus")
    lines: list[str] = []
    if focus_lines:
        lines.extend(with_fallback_bullets(focus_lines))
    else:
        lines.append(f"- Review focus was not extracted from `{filename}`.")

    lines.extend(slice_specific_non_claim_lines(result))
    return lines[:7]
def playbook_lines(result: Any) -> list[str]:
    lines = applied_playbook_lines(result)
    if not lines:
        lines = with_fallback_bullets(
            archive_section_lines(result, "evidence.md", "## Guidance applied")
        )
    if not lines:
        lines = consulted_playbook_fallback_lines(result)
    if not lines:
        lines.append("- Guidance details were not extracted from the evidence archive.")
    guidance_reference = archive_reference(
        result.evidence_result.archive_path,
        "evidence.md",
    )
    return truncate_with_required_line(
        lines,
        f"- Guidance evidence: `{guidance_reference}`",
        max_lines=APPLIED_PLAYBOOK_LINE_LIMIT + 1,
    )
def applied_playbook_lines(result: Any) -> list[str]:
    return prefixed_archive_section_lines(
        result,
        "evidence.md",
        (("Applied", "### Applied"),),
        limit=APPLIED_PLAYBOOK_LINE_LIMIT,
    )
def consulted_playbook_fallback_lines(result: Any) -> list[str]:
    return prefixed_archive_section_lines(
        result,
        "evidence.md",
        (("Consulted", "### Consulted"),),
        limit=CONSULTED_PLAYBOOK_FALLBACK_LIMIT,
    )
def truncate_with_required_line(
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
def boundary_lines(result: Any) -> list[str]:
    lines = archive_boundary_lines(result)
    if lines:
        return lines

    return [
        "- No archive boundary details were extracted.",
        "- Summary is read-only and does not create archives, repair evidence, "
        "mutate PR bodies, approve, merge, deploy, release, or infer change IDs.",
    ]
def slice_specific_non_claim_lines(result: Any) -> list[str]:
    return [
        line
        for line in with_fallback_bullets(archive_boundary_lines(result))
        if strip_list_marker(line).casefold().startswith(
            "slice-specific non-claims:"
        )
    ]
def prefixed_archive_section_lines(
    result: Any,
    filename: str,
    sections: tuple[tuple[str, str], ...],
    *,
    limit: int = 2,
) -> list[str]:
    lines: list[str] = []
    for label, heading in sections:
        section_lines = archive_section_lines(result, filename, heading)
        section_count = 0
        for line in section_lines:
            text = strip_list_marker(line)
            if text and not is_playbook_template_line(text):
                lines.append(f"- {label}: {text}")
                section_count += 1
            if section_count >= limit:
                break
    return lines
def is_playbook_template_line(text: str) -> bool:
    return text == "TBD." or any(
        text.startswith(prefix) for prefix in PLAYBOOK_TEMPLATE_PREFIXES
    )
def archive_section_lines(result: Any, filename: str, heading: str) -> list[str]:
    text = archive_file_text(result, filename)
    if text is None:
        return []

    section = markdown_section(text, heading)
    return concise_markdown_lines(section) if section else []


def archive_boundary_lines(result: Any) -> list[str]:
    narrative = archive_file_text(result, _narrative_filename(result))
    if narrative is None:
        return []

    section = markdown_section(narrative, "## Boundaries / Non-Claims")
    if not section:
        section = markdown_section(narrative, "## Limits")
    return concise_markdown_lines(section) if section else []


def archive_file_text(result: Any, filename: str) -> str | None:
    path = Path(result.repo_path) / result.evidence_result.archive_path / filename
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")
def _narrative_filename(result: Any) -> str:
    archive_dir = Path(result.repo_path) / result.evidence_result.archive_path
    return narrative_filename(archive_dir)
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

    return "\n".join(section_lines).strip()
def _ends_section(line: str, heading: str) -> bool:
    return line.startswith("#") and len(line) - len(line.lstrip("#")) <= len(
        heading.split(" ", 1)[0]
    )
def concise_markdown_lines(markdown: str) -> list[str]:
    """Return compact semantic items without splitting naturally wrapped prose.

    Evidence authors commonly wrap a long list item or paragraph at a pleasant
    display width.  The PR-body caps are reviewer-facing item caps, not source
    line caps, so join each uninterrupted continuation before callers apply
    their compact limits.
    """
    lines: list[str] = []
    can_continue = False
    for line in markdown.splitlines():
        text = line.strip()
        if not text or text == "TBD.":
            can_continue = False
            continue

        # Section labels are structure, not reviewer-facing evidence.  Reset
        # continuation state so prose below a nested heading cannot join the
        # preceding item.
        if text.startswith("#"):
            can_continue = False
            continue

        if _markdown_list_item(text) or not lines or not can_continue:
            lines.append(text)
        else:
            lines[-1] = f"{lines[-1]} {text}"
        can_continue = True

    return lines[:8]


def _markdown_list_item(text: str) -> bool:
    return text.startswith(("- ", "* ", "+ "))
def with_fallback_bullets(lines: list[str]) -> list[str]:
    bulleted: list[str] = []
    for line in lines:
        if line.lstrip().startswith(("-", "*")):
            bulleted.append(line)
        else:
            bulleted.append(f"- {line}")
    return bulleted
def strip_list_marker(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith(("- ", "* ")):
        return stripped[2:].strip()
    return stripped
def archive_reference(archive_path: str | Path, filename: str) -> str:
    return f"{archive_path}/{filename}"
