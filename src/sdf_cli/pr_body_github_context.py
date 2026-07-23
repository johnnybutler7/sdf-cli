"""Best-effort local GitHub context inference for PR body links."""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from sdf_cli.pr_body_links import (
    LINK_MODE_GITHUB,
    LINK_MODE_REPO_RELATIVE,
    is_full_commit_sha,
    is_valid_github_repo,
)


@dataclass(frozen=True)
class PrBodyLinkOptions:
    link_mode: str
    github_repo: str | None = None
    github_ref: str | None = None


def resolve_pr_body_link_options(
    *,
    repo: str,
    link_mode: str | None,
    github_repo: str | None,
    github_ref: str | None,
    allow_branch_fallback: bool = False,
) -> PrBodyLinkOptions:
    """Resolve PR-body link options without requiring network access."""

    inferred_repo = github_repo or infer_github_repo(repo)
    inferred_ref = github_ref or infer_current_pr_ref(repo)
    if inferred_ref is None and allow_branch_fallback:
        inferred_ref = infer_current_branch(repo)

    if link_mode == LINK_MODE_GITHUB:
        return PrBodyLinkOptions(
            link_mode=LINK_MODE_GITHUB,
            github_repo=inferred_repo,
            github_ref=inferred_ref,
        )

    if link_mode == LINK_MODE_REPO_RELATIVE:
        return PrBodyLinkOptions(
            link_mode=LINK_MODE_REPO_RELATIVE,
            github_repo=github_repo,
            github_ref=github_ref,
        )

    if (
        inferred_repo
        and inferred_ref
        and (github_repo or is_valid_github_repo(inferred_repo))
    ):
        return PrBodyLinkOptions(
            link_mode=LINK_MODE_GITHUB,
            github_repo=inferred_repo,
            github_ref=inferred_ref,
        )

    return PrBodyLinkOptions(
        link_mode=LINK_MODE_REPO_RELATIVE,
        github_repo=github_repo,
        github_ref=github_ref,
    )


def infer_github_repo(repo: str) -> str | None:
    remote_url = _git_output(repo, "remote", "get-url", "origin")
    if remote_url is None:
        return None
    return _github_repo_from_remote_url(remote_url)


def infer_current_branch(repo: str) -> str | None:
    return _git_output(repo, "branch", "--show-current")


def infer_current_pr_ref(repo: str) -> str | None:
    """Return the immutable local PR-head candidate when it is available."""
    head_sha = _git_output(repo, "rev-parse", "HEAD")
    if head_sha and is_full_commit_sha(head_sha):
        return head_sha
    hosted_pr_head_sha = os.environ.get("GITHUB_PR_HEAD_SHA", "").strip()
    if is_full_commit_sha(hosted_pr_head_sha):
        return hosted_pr_head_sha
    return None


def _git_output(repo: str, *args: str) -> str | None:
    repo_path = Path(repo).expanduser()
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_path), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def _github_repo_from_remote_url(remote_url: str) -> str | None:
    patterns = (
        r"^git@github\.com:(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^https://github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^http://github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote_url)
        if match is None:
            continue
        candidate = match.group("repo")
        if is_valid_github_repo(candidate):
            return candidate
    return None
