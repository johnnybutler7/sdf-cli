"""Shared receiver repository selection guidance for CLI commands."""

from __future__ import annotations

from pathlib import Path

REPO_HELP = (
    "Local receiver repository path. Defaults to the current directory for "
    "front-door commands; use --repo /path/to/receiver when the selected "
    "checkout is elsewhere."
)

# Help text for the read-only front-door inspection commands (`status` and
# `guidance`) that default `--repo` to the current directory. It spells out that
# the option names the receiver repository being inspected and that omitting it
# inspects the current directory.
INSPECT_REPO_HELP = (
    "Receiver repository to inspect. Identifies which local receiver checkout "
    "this command reads; defaults to the current directory when --repo is "
    "omitted, or pass --repo /path/to/receiver to inspect a checkout elsewhere."
)


def unreadable_repo_reason(
    command: str,
    repo_path: Path,
    repo_label: str,
    headline: str | None = None,
) -> str | None:
    if repo_path.is_dir():
        try:
            next(repo_path.iterdir(), None)
        except OSError:
            pass
        else:
            return None

    default_headline = (
        f"{command}: repo path is not a readable directory: {repo_label}"
    )
    return "\n".join(
        (
            headline if headline is not None else default_headline,
            "",
            "Recovery:",
            "- Select an existing local receiver checkout with "
            "--repo /path/to/receiver, or run from the receiver root and use "
            "--repo .",
            "- SDF does not create the repository directory; use "
            "`sdf init --repo <receiver>` only after the "
            "checkout directory already exists.",
        )
    )
