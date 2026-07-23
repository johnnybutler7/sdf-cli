"""Read-only PR body artifact validation."""

from __future__ import annotations

import re
from pathlib import Path

from sdf_cli.evidence_archive_contract import CURRENT_NARRATIVE_FILENAME
from sdf_cli.pr_body_artifact import pr_body_artifact_path
from sdf_cli.pr_body_check_links import (
    absolute_evidence_links,
    broken_evidence_links,
    linked_archive_files,
)
from sdf_cli.pr_body_check_result import PrBodyCheckResult, render_pr_body_check
from sdf_cli.pr_body_links import (
    LINK_MODE_REPO_RELATIVE,
    github_context,
    github_ref_stability_warnings,
    repo_relative_evidence_links,
    wrong_github_evidence_links,
)
from sdf_cli.pr_body_recovery import recovery_commands

__all__ = [
    "EXPECTED_PR_BODY_SECTIONS",
    "PrBodyCheckResult",
    "check_pr_body_artifact",
    "check_pr_body_content",
    "render_pr_body_check",
]

EXPECTED_PR_BODY_SECTIONS: tuple[str, ...] = (
    "# What you are reviewing",
    "## Review focus",
    "## Run context",
    "## Guidance applied",
    "## Verification",
)



def check_pr_body_artifact(
    repo: str,
    change_id: str,
    *,
    link_mode: str = LINK_MODE_REPO_RELATIVE,
    github_repo: str | None = None,
    github_ref: str | None = None,
) -> PrBodyCheckResult:
    repo_path = Path(repo).expanduser()
    artifact_path = pr_body_artifact_path(change_id)
    target = repo_path / artifact_path
    warnings = github_ref_stability_warnings(
        link_mode=link_mode,
        github_ref=github_ref,
    )
    recovery_command, recheck_command = recovery_commands(
        repo,
        change_id,
        overwrite=target.is_file(),
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    if not target.is_file():
        return PrBodyCheckResult(
            change_id=change_id,
            artifact_path=artifact_path,
            exists=False,
            warnings=warnings,
            recovery_command=recovery_command,
            recheck_command=recheck_command,
        )

    content = target.read_text(encoding="utf-8")
    return check_pr_body_content(
        repo,
        change_id,
        content,
        artifact_path=artifact_path,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
        recovery_command=recovery_command,
        recheck_command=recheck_command,
    )


def check_pr_body_content(
    repo: str,
    change_id: str,
    content: str,
    *,
    artifact_path: str | None = None,
    link_mode: str = LINK_MODE_REPO_RELATIVE,
    github_repo: str | None = None,
    github_ref: str | None = None,
    recovery_command: str | None = None,
    recheck_command: str | None = None,
) -> PrBodyCheckResult:
    repo_path = Path(repo).expanduser()
    artifact_path = artifact_path or pr_body_artifact_path(change_id)
    warnings = github_ref_stability_warnings(
        link_mode=link_mode,
        github_ref=github_ref,
    )
    links = _markdown_links(content)
    archive_path = f".sdf/evidence/{change_id}"
    github_link_context = github_context(
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    linked_files = linked_archive_files(
        links,
        archive_path=archive_path,
        github_context=github_link_context,
    )
    required_link_files = [CURRENT_NARRATIVE_FILENAME]

    return PrBodyCheckResult(
        change_id=change_id,
        artifact_path=artifact_path,
        exists=True,
        missing_sections=tuple(
            section for section in EXPECTED_PR_BODY_SECTIONS if section not in content
        ),
        missing_evidence_links=tuple(
            filename
            for filename in required_link_files
            if filename not in linked_files
        ),
        broken_evidence_links=broken_evidence_links(
            repo_path,
            links,
            archive_path=archive_path,
            github_context=github_link_context,
        ),
        absolute_evidence_links=absolute_evidence_links(links),
        repo_relative_evidence_links=repo_relative_evidence_links(
            links,
            archive_path=archive_path,
            link_mode=link_mode,
        ),
        wrong_github_evidence_links=wrong_github_evidence_links(
            links,
            archive_path=archive_path,
            github_context=github_link_context,
        ),
        malformed_evidence_links=_malformed_evidence_links(links),
        warnings=warnings,
        recovery_command=recovery_command,
        recheck_command=recheck_command,
    )


def _markdown_links(markdown: str) -> tuple[str, ...]:
    return tuple(
        match.group(1).strip()
        for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)", markdown)
    )


def _malformed_evidence_links(links: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        link
        for link in links
        if ".sdf/evidence/" in link and ("`" in link or link != link.strip())
    )
