"""Copyable recovery commands for absent or invalid PR-body handoffs."""

from __future__ import annotations

import shlex


def recovery_commands(
    repo: str,
    change_id: str,
    *,
    overwrite: bool,
    link_mode: str,
    github_repo: str | None,
    github_ref: str | None,
) -> tuple[str, str]:
    """Build full-closeout recovery commands; overwrite replaces an invalid body."""
    options = ["--link-mode", link_mode]
    if github_repo:
        options.extend(["--github-repo", github_repo])
    if github_ref:
        options.extend(["--github-ref", github_ref])
    close = [
        "sdf",
        "close",
        "--repo",
        repo,
        "--change-id",
        change_id,
    ]
    if overwrite:
        close.append("--overwrite")
    close.extend(options)
    return shlex.join(close), shlex.join(close)
