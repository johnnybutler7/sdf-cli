"""GitHub CLI boundary for merged PR-body finalisation."""

from __future__ import annotations

import json
import subprocess
import tempfile
from typing import Protocol


class GithubPrBoundary(Protocol):
    def read_pr_body(self, pr_number: str, github_repo: str) -> str:
        """Read the live GitHub PR body."""

    def update_pr_body(self, pr_number: str, github_repo: str, body: str) -> None:
        """Update the live GitHub PR body."""


class GhCliPrBoundary:
    def read_pr_body(self, pr_number: str, github_repo: str) -> str:
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--repo", github_repo, "--json", "body"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(result.stdout)
        return str(payload.get("body") or "")

    def update_pr_body(self, pr_number: str, github_repo: str, body: str) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as body_file:
            body_file.write(body)
            body_file.flush()
            subprocess.run(
                [
                    "gh",
                    "pr",
                    "edit",
                    pr_number,
                    "--repo",
                    github_repo,
                    "--body-file",
                    body_file.name,
                ],
                check=True,
            )
