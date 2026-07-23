"""Parser and dispatch helpers for the top-level initialization command."""

from __future__ import annotations

import argparse

from sdf_cli.commands.repository_commands import REPO_HELP
from sdf_cli.receiver_scaffold import (
    ReceiverScaffoldWriteError,
    render_receiver_scaffold,
    write_receiver_scaffold,
)
from sdf_cli.receiver_scaffold_inspection import (
    inspect_receiver_scaffold,
    render_receiver_scaffold_inspection,
)


def register_init_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    init_parser = subparsers.add_parser(
        "init",
        prog="sdf init",
        help="Initialize missing receiver files or inspect their canonical manifest.",
    )
    init_parser.add_argument("--repo", default=".", help=REPO_HELP)
    init_parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Read-only canonical-manifest inspection; reports missing, matching, "
            "and drifted entries."
        ),
    )


def handle_init(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    if args.check:
        inspection = inspect_receiver_scaffold(args.repo)
        if inspection.invalid_reason is not None:
            parser.error(inspection.invalid_reason)
        print(render_receiver_scaffold_inspection(inspection))
        return inspection.exit_code

    try:
        result = write_receiver_scaffold(args.repo)
    except ReceiverScaffoldWriteError as error:
        parser.error(str(error))
    if result.invalid_reason is not None:
        parser.error(result.invalid_reason)

    inspection = inspect_receiver_scaffold(args.repo)
    print(render_receiver_scaffold(result, inspection=inspection))
    return result.exit_code
