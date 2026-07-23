"""Parser and dispatch helpers for CI-only merged PR-body finalisation."""

from __future__ import annotations

import argparse

from sdf_cli.pr_body_finalize_merged import (
    FinalizeMergedPrBodyOptions,
    finalize_merged_pr_body,
    render_finalize_merged_pr_body_result,
    validate_finalize_merged_pr_body_options,
)


def register_finalize_merged_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparsers.add_parser(
        "finalize-merged",
        help="Workflow/CI-only: finalize merged live PR-body evidence links.",
        description=(
            "Workflow/internal command for explicit workflow/CI use. Finalize "
            "a merged live GitHub PR body so SDF evidence links point at a "
            "durable commit SHA. This command mutates the live GitHub PR body "
            "through gh pr edit and is not part of normal local closeout."
        ),
        epilog=(
            "Examples:\n"
            "  sdf finalize-merged --pr-number <number> "
            "--github-repo owner/name --merge-sha <40-character-commit-sha>\n\n"
            "Skip behavior: exits successfully without updating GitHub when "
            "the live PR body has no eligible SDF evidence links that need a "
            "merge-SHA rewrite."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--pr-number", required=True, help="GitHub PR number.")
    parser.add_argument("--github-repo", required=True, help="GitHub owner/name.")
    parser.add_argument(
        "--merge-sha",
        required=True,
        help="Full 40-character merge commit SHA for durable evidence links.",
    )


def handle_finalize_merged(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    options = FinalizeMergedPrBodyOptions(
        pr_number=args.pr_number,
        github_repo=args.github_repo,
        merge_sha=args.merge_sha,
    )
    validate_finalize_merged_args(options, parser)
    result = finalize_merged_pr_body(options)
    print(render_finalize_merged_pr_body_result(result))
    return result.exit_code


def validate_finalize_merged_args(
    options: FinalizeMergedPrBodyOptions,
    parser: argparse.ArgumentParser,
) -> None:
    errors = validate_finalize_merged_pr_body_options(options)
    if errors:
        parser.error("; ".join(errors))
