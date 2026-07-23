"""Workflow-only command for controlled open-PR body publication."""

from __future__ import annotations

import argparse
import tempfile

from sdf_cli.open_pr_body_publication import (
    OpenPrBodyPublicationOptions,
    publish_open_pr_body,
    render_open_pr_body_publication,
)
from sdf_cli.open_pr_github import GhOpenPrBoundary


def register_publish_open_pr_body_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparsers.add_parser(
        "publish-open-pr-body",
        help="Workflow/internal: standardize an eligible Cloud draft PR body.",
        description=(
            "Manually controlled workflow command. It observes the current GitHub "
            "PR, reads only its committed contract-5 evidence through the API, and "
            "updates only the body of an eligible open draft. It does not check out "
            "or execute PR-head code and is separate from post-merge finalization."
        ),
    )
    parser.add_argument("--pr-number", required=True, help="Open draft PR number.")
    parser.add_argument(
        "--github-repo", required=True, help="Target GitHub repository as owner/name."
    )
    parser.add_argument(
        "--base-branch",
        required=True,
        help="Trusted base branch the observed PR must target.",
    )


def handle_publish_open_pr_body(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="sdf-open-pr-evidence-") as directory:
        options = OpenPrBodyPublicationOptions(
            github_repo=args.github_repo,
            pr_number=args.pr_number,
            base_branch=args.base_branch,
            evidence_data_dir=directory,
        )
        result = publish_open_pr_body(options, github=GhOpenPrBoundary())
    print(render_open_pr_body_publication(result))
    return result.exit_code
