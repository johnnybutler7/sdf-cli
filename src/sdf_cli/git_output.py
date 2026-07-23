"""Small git command output helper."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_output(repo_path: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()
