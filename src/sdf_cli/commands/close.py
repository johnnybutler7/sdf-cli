"""Parser and dispatch helpers for the composed local close command."""

from __future__ import annotations

import argparse
import io
from pathlib import Path

from sdf_cli.closeout_handoff import render_closeout_handoff, run_closeout_handoff
from sdf_cli.commands.pr_body_link_arguments import (
    add_pr_body_link_arguments,
    validate_pr_body_link_args,
)
from sdf_cli.commands.repository_commands import REPO_HELP
from sdf_cli.pr_body_github_context import resolve_pr_body_link_options
from sdf_cli.pr_body_refresh import refresh_pr_body_handoff, render_pr_body_refresh
from sdf_cli.receiver_cli_identity import lifecycle_identity_preflight

SUCCESSFUL_CLOSE_COMPLETION_MARKER = (
    "SDF close complete: verification passed, evidence recorded, and local "
    "handoff checked."
)


def register_close_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparsers.add_parser(
        "close",
        prog="sdf close",
        help=(
            "Run verification, complete evidence closeout, and prepare local "
            "handoff."
        ),
        description=(
            "Run configured full verification, create the contract-5 evidence "
            "archive when it does not already exist, record compact verification "
            "facts and closed_at, and write and check the local PR-body handoff "
            "only after closeout passes. This command does not create PRs, "
            "mutate PR bodies, call GitHub, or run post-merge finalisation."
        ),
        epilog=(
            "Examples:\n"
            "  sdf close --change-id <change-id>\n"
            "  sdf close --change-id <change-id> "
            "--surface codex_local --model gpt-5.6 "
            "--reasoning medium --speed fast\n"
            "  # Commit the change and evidence before refreshing the handoff.\n"
            "  sdf close --change-id <change-id> --refresh-handoff\n"
            "  sdf close --change-id <change-id> "
            "--link-mode github --github-repo owner/name --github-ref "
            "<full-pr-head-sha>\n\n"
            "By default, close infers GitHub blob links from origin and the "
            "immutable current HEAD when possible; otherwise it keeps "
            "repo-relative links for local/offline review. GitHub evidence links "
            "require the full immutable PR head SHA. Declared run-context values "
            "complete unknown or unavailable machine-record fields only; close "
            "does not infer model identity or replace existing declared values. "
            "After evidence-only wording edits to a passing closeout, commit the "
            "final evidence and use --refresh-handoff; it reuses recorded passing "
            "verification without rerunning the configured boundary. It creates "
            "the authoritative publication-ready body; publish that checked file "
            "verbatim when it reports publication-ready."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", default=".", help=REPO_HELP)
    parser.add_argument(
        "--change-id",
        required=True,
        help="Stable evidence archive identifier.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "During a new full closeout, replace existing generated PR-body "
            "handoff text."
        ),
    )
    parser.add_argument(
        "--refresh-handoff",
        action="store_true",
        help=(
            "Regenerate only the checked handoff from recorded passing closeout "
            "evidence. GitHub mode requires the evidence archive at current HEAD."
        ),
    )
    parser.add_argument(
        "--surface",
        help=(
            "Optional declared agent surface for a late-created or incomplete "
            "run context; literal unknown is acceptable when genuinely unknown."
        ),
    )
    parser.add_argument(
        "--model",
        help=(
            "Optional declared model identity; not inferred from environment "
            "details, and literal unknown is acceptable when genuinely unknown."
        ),
    )
    parser.add_argument(
        "--reasoning",
        help=(
            "Optional declared reasoning setting; literal unknown is acceptable "
            "when genuinely unknown."
        ),
    )
    parser.add_argument(
        "--speed",
        help=(
            "Optional declared speed setting; literal unknown is acceptable "
            "when genuinely unknown."
        ),
    )
    add_pr_body_link_arguments(parser, default_link_mode=None)


def handle_close(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    identity_error = lifecycle_identity_preflight(Path(args.repo).expanduser())
    if identity_error is not None:
        parser.error(identity_error)
    link_options = resolve_pr_body_link_options(
        repo=args.repo,
        link_mode=args.link_mode,
        github_repo=args.github_repo,
        github_ref=args.github_ref,
        change_id=args.change_id,
    )
    args.link_mode = link_options.link_mode
    args.github_repo = link_options.github_repo
    args.github_ref = link_options.github_ref
    validate_pr_body_link_args(args, parser)
    if args.refresh_handoff:
        declared_context = (args.surface, args.model, args.reasoning, args.speed)
        if any(value is not None for value in declared_context):
            parser.error("--refresh-handoff cannot declare run context")
        result = refresh_pr_body_handoff(
            repo=args.repo,
            change_id=args.change_id,
            link_mode=args.link_mode,
            github_repo=args.github_repo,
            github_ref=args.github_ref,
        )
        print(render_pr_body_refresh(result))
        return result.exit_code
    captured_output = io.StringIO()
    result = run_closeout_handoff(
        repo=args.repo,
        change_id=args.change_id,
        overwrite=args.overwrite,
        surface=args.surface,
        model=args.model,
        reasoning=args.reasoning,
        speed=args.speed,
        link_mode=args.link_mode,
        github_repo=args.github_repo,
        github_ref=args.github_ref,
        stdout=captured_output,
        stderr=captured_output,
    )
    print(render_closeout_handoff(result))
    if result.exit_code == 0:
        print(SUCCESSFUL_CLOSE_COMPLETION_MARKER)
    return result.exit_code
