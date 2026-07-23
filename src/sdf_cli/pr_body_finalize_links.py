"""Merged PR-body evidence link finalisation helpers."""

from __future__ import annotations

import re

from sdf_cli.pr_body_links import EVIDENCE_LINK_LABELS

KNOWN_EVIDENCE_FILES = tuple(EVIDENCE_LINK_LABELS)


def finalize_body_links(
    body: str,
    *,
    github_repo: str,
    merge_sha: str,
) -> str:
    github_body = _replace_github_evidence_links(
        body,
        github_repo=github_repo,
        merge_sha=merge_sha,
    )
    return _replace_repo_relative_evidence_links(
        github_body,
        github_repo=github_repo,
        merge_sha=merge_sha,
    )


def _replace_github_evidence_links(
    body: str,
    *,
    github_repo: str,
    merge_sha: str,
) -> str:
    filenames = "|".join(re.escape(filename) for filename in KNOWN_EVIDENCE_FILES)
    pattern = re.compile(
        rf"https://github\.com/{re.escape(github_repo)}/blob/"
        rf"[^)\s]+/\.sdf/evidence/([^/\s)]+)/({filenames})"
    )

    def replace(match: re.Match[str]) -> str:
        return _github_blob_url(
            match.group(1), match.group(2), github_repo, merge_sha
        )

    return pattern.sub(replace, body)


def _replace_repo_relative_evidence_links(
    body: str,
    *,
    github_repo: str,
    merge_sha: str,
) -> str:
    filenames = "|".join(re.escape(filename) for filename in KNOWN_EVIDENCE_FILES)
    pattern = re.compile(
        rf"(?<![\w/])\.sdf/evidence/([^/\s)]+)/({filenames})"
    )

    def replace(match: re.Match[str]) -> str:
        return _github_blob_url(
            match.group(1), match.group(2), github_repo, merge_sha
        )

    return pattern.sub(replace, body)


def _github_blob_url(
    change_id: str, filename: str, github_repo: str, merge_sha: str
) -> str:
    return (
        f"https://github.com/{github_repo}/blob/{merge_sha}/"
        f".sdf/evidence/{change_id}/{filename}"
    )
