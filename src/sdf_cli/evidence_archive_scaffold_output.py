"""Render next steps for explicit evidence archive scaffolding."""

from __future__ import annotations


def next_step_lines(result: object) -> list[str]:
    repo_label = str(getattr(result, "repo_label"))
    change_id = str(getattr(result, "change_id"))
    close = f"sdf close --repo {repo_label} --change-id {change_id}"
    lines = ["", "Next:"]
    lines.extend(
        [
            "- After evidence is populated, close the governed change:",
            f"  {close}",
            "- When local GitHub context cannot be inferred, supply the "
            "immutable PR head SHA:",
            f"  {close} --link-mode github --github-repo owner/name "
            "--github-ref <full-pr-head-sha>",
        ]
    )
    return lines
