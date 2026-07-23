"""Rewrite archive path references in generated PR bodies."""

from __future__ import annotations

import re

from sdf_cli.pr_body_links import EVIDENCE_LINK_LABELS, EvidenceLinkTarget

CURRENT_ARCHIVE_LINK_ROLES = (
    "Review evidence",
    "Run-context evidence",
    "Guidance evidence",
    "Verification evidence",
)
DEFAULT_EVIDENCE_HEADINGS_BY_PR_SECTION: dict[tuple[str, str], str] = {
    ("## Review focus", "evidence.md"): "Acceptance / Review Focus",
    ("## Run context", "evidence.md"): "Machine Record",
    ("## Guidance applied", "evidence.md"): "Guidance Applied",
    ("## Verification", "evidence.md"): "Verification",
}


def link_archive_file_references(
    markdown: str,
    *,
    change_id: str,
    link_mode: str,
    github_repo: str | None = None,
    github_ref: str | None = None,
    evidence_headings_by_pr_section: dict[tuple[str, str], str] | None = None,
) -> str:
    archive_path = f".sdf/evidence/{change_id}"
    filenames = "|".join(re.escape(filename) for filename in EVIDENCE_LINK_LABELS)
    labels = "|".join(
        map(re.escape, (*EVIDENCE_LINK_LABELS.values(), *CURRENT_ARCHIVE_LINK_ROLES))
    )
    prefixed_pattern = re.compile(
        rf"(?m)^- ({labels}): `({re.escape(archive_path)}/({filenames}))`$"
    )
    pattern = re.compile(rf"`({re.escape(archive_path)}/({filenames}))`")
    target = EvidenceLinkTarget(
        change_id=change_id,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    heading_map = (
        evidence_headings_by_pr_section or DEFAULT_EVIDENCE_HEADINGS_BY_PR_SECTION
    )

    def evidence_link(
        filename: str,
        *,
        pr_body_section: str | None,
        label: str | None = None,
    ) -> str:
        label = label or EVIDENCE_LINK_LABELS[filename]
        heading = heading_map.get((pr_body_section or "", filename))
        return f"[{label}]({target.link_for(filename, heading=heading)})"

    def replace_prefixed(match: re.Match[str]) -> str:
        label = match.group(1)
        filename = match.group(3)
        if filename == "evidence.md":
            if label not in CURRENT_ARCHIVE_LINK_ROLES:
                return match.group(0)
            link_label = EVIDENCE_LINK_LABELS[filename]
        elif label != EVIDENCE_LINK_LABELS[filename]:
            return match.group(0)
        else:
            link_label = label
        pr_body_section = _pr_body_section_at(markdown, match.start())
        link = evidence_link(
            filename,
            pr_body_section=pr_body_section,
            label=link_label,
        )
        return f"- {link}"

    def replace(match: re.Match[str]) -> str:
        filename = match.group(2)
        return evidence_link(
            filename,
            pr_body_section=_pr_body_section_at(prefixed_markdown, match.start()),
        )

    prefixed_markdown = prefixed_pattern.sub(replace_prefixed, markdown)
    return pattern.sub(replace, prefixed_markdown)


def _pr_body_section_at(markdown: str, position: int) -> str | None:
    section: str | None = None
    for line in markdown[:position].splitlines():
        if line.startswith("## "):
            section = line
    return section
