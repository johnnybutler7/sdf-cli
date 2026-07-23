"""Parser and dispatch helpers for repository inspection commands."""

from __future__ import annotations

import argparse

from sdf_cli.commands.guidance import check_guidance, render_guidance
from sdf_cli.commands.status import check_status
from sdf_cli.commands.status_rendering import render_status
from sdf_cli.repo_selection import INSPECT_REPO_HELP
from sdf_cli.repo_selection import REPO_HELP as SHARED_REPO_HELP

# Compatibility alias for command modules that import the shared help text from
# this parser module.
REPO_HELP = SHARED_REPO_HELP


def register_repository_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    status_parser = subparsers.add_parser(
        "status",
        prog="sdf status",
        help="Inspect minimal SDF receiver readiness.",
    )
    status_parser.add_argument("--repo", default=".", help=INSPECT_REPO_HELP)

    guidance_parser = subparsers.add_parser(
        "guidance",
        prog="sdf guidance",
        help="Inspect SDF and receiver-local guidance routing.",
    )
    guidance_parser.add_argument("--repo", default=".", help=INSPECT_REPO_HELP)


def handle_status(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    result = check_status(args.repo)
    if result.invalid_reason is not None:
        parser.error(result.invalid_reason)
    print(render_status(result))
    return result.exit_code


def handle_guidance(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    result = check_guidance(args.repo)
    if result.invalid_reason is not None:
        parser.error(result.invalid_reason)
    print(render_guidance(result))
    return result.exit_code
