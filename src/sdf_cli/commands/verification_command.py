"""Parser and dispatch helpers for verification commands."""

from __future__ import annotations

import argparse

from sdf_cli.commands.repository_commands import REPO_HELP
from sdf_cli.commands.verification import check_verification
from sdf_cli.config.governance import governance_mode
from sdf_cli.verification_check_rendering import render_verification
from sdf_cli.verification_runner import run_verification
from sdf_cli.verification_summary import render_verification_summary


def register_verification_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    verification_parser = subparsers.add_parser(
        "verify",
        prog="sdf verify",
        help="Run configured receiver verification, or inspect it with --check.",
        description=(
            "Execute configured receiver verification. Use --check to display "
            "the boundary without running commands."
        ),
    )
    verification_parser.add_argument("--repo", default=".", help=REPO_HELP)
    action_group = verification_parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--check",
        action="store_true",
        help="Display the configured verification boundary without running commands.",
    )
    action_group.add_argument(
        "--focused",
        metavar="NAME",
        help=(
            "Run one named focused verification subset from .sdf/verification.yml. "
            "Focused runs are supporting feedback only."
        ),
    )
    verification_parser.epilog = (
        "Examples:\n"
        "  sdf verify\n"
        "  sdf verify --focused <name>\n"
        "  sdf verify --check  # list configured focused verification names"
    )
    verification_parser.formatter_class = argparse.RawDescriptionHelpFormatter


def handle_verification(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    if not args.check:
        result = check_verification(args.repo)
        if result.invalid_reason is not None:
            parser.error(result.invalid_reason)
        run_result = run_verification(
            result.repo_path,
            repo_label=result.repo_label,
            focused_name=args.focused,
        )
        print(
            render_verification_summary(
                run_result,
                governance_mode=governance_mode(result.repo_path),
            )
        )
        return run_result.exit_code

    result = check_verification(args.repo)
    if result.invalid_reason is not None:
        parser.error(result.invalid_reason)
    print(render_verification(result))
    return result.exit_code
