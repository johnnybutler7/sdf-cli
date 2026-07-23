"""Best-effort local machine facts for evidence records."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

UNAVAILABLE = "unavailable"


def repository_context(repo_path: Path | None) -> dict[str, str]:
    if repo_path is None:
        return {
            "name": UNAVAILABLE,
            "path": UNAVAILABLE,
            "github": UNAVAILABLE,
        }
    path = repo_path.expanduser()
    resolved = _resolved_path(path)
    return {
        "name": Path(resolved).name if resolved != UNAVAILABLE else UNAVAILABLE,
        "path": ".",
        "github": _github_repo_from_remote(
            _git_output(path, "remote", "get-url", "origin")
        ),
    }


def branch_context(repo_path: Path | None) -> dict[str, str]:
    if repo_path is None:
        return {"name": UNAVAILABLE, "head": UNAVAILABLE}
    path = repo_path.expanduser()
    return {
        "name": _git_output(path, "branch", "--show-current") or UNAVAILABLE,
        "head": _git_output(path, "rev-parse", "HEAD") or UNAVAILABLE,
    }


def _resolved_path(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return UNAVAILABLE


def _git_output(repo_path: Path, *args: str) -> str | None:
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


def _github_repo_from_remote(remote_url: str | None) -> str:
    if remote_url is None:
        return UNAVAILABLE
    patterns = (
        r"^git@github\.com:(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^https://github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^http://github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote_url)
        if match is not None:
            return match.group("repo")
    return UNAVAILABLE
