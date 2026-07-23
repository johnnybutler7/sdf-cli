"""Shared parser helpers for local PR-body evidence links."""

from __future__ import annotations

import argparse

from sdf_cli.pr_body_links import (
    LINK_MODE_GITHUB,
    LINK_MODE_REPO_RELATIVE,
    validate_pr_body_link_options,
)


def add_pr_body_link_arguments(
    parser: argparse.ArgumentParser,
    *,
    default_link_mode: str | None = LINK_MODE_REPO_RELATIVE,
    require_immutable_ref: bool = True,
) -> None:
    parser.add_argument(
        "--link-mode",
        choices=(LINK_MODE_REPO_RELATIVE, LINK_MODE_GITHUB),
        default=default_link_mode,
        help=(
            "Evidence link target mode for pr-body.md. The command infers "
            "GitHub mode from origin and the immutable current HEAD when this is "
            "omitted."
            if default_link_mode is None
            else "Evidence link target mode for pr-body.md."
        ),
    )
    parser.add_argument("--github-repo", help="GitHub owner/name for GitHub link mode.")
    github_ref_help = (
        "Full 40-character immutable PR head SHA for link mode."
        if require_immutable_ref
        else "GitHub branch/SHA for link mode."
    )
    parser.add_argument("--github-ref", help=github_ref_help)


def validate_pr_body_link_args(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    *,
    require_immutable_ref: bool = True,
) -> None:
    errors = validate_pr_body_link_options(
        link_mode=args.link_mode,
        github_repo=args.github_repo,
        github_ref=args.github_ref,
        require_immutable_ref=require_immutable_ref,
    )
    if errors:
        parser.error("; ".join(errors))
