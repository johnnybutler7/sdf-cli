"""Evidence-link helpers for PR-body validation."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.pr_body_links import (
    GithubLinkContext,
    github_evidence_filename,
    is_local_absolute_evidence_link,
    local_target_for_evidence_link,
)


def linked_archive_files(
    links: tuple[str, ...],
    *,
    archive_path: str,
    github_context: GithubLinkContext | None = None,
) -> set[str]:
    linked: set[str] = set()
    for link in links:
        prefix = f"{archive_path}/"
        if link.startswith(prefix):
            linked.add(link.removeprefix(prefix).partition("#")[0])
            continue
        github_filename = github_evidence_filename(
            link,
            archive_path=archive_path,
            github_context=github_context,
        )
        if github_filename is not None:
            linked.add(github_filename)
    return linked


def broken_evidence_links(
    repo_path: Path,
    links: tuple[str, ...],
    *,
    archive_path: str,
    github_context: GithubLinkContext | None = None,
) -> tuple[str, ...]:
    broken: list[str] = []
    for link in links:
        target = local_target_for_evidence_link(
            repo_path,
            link,
            archive_path=archive_path,
            github_context=github_context,
        )
        if target is not None and not target.is_file():
            broken.append(link)
    return tuple(broken)


def absolute_evidence_links(links: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(link for link in links if is_local_absolute_evidence_link(link))
