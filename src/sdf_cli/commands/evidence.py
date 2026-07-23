"""Parser and dispatch helpers for evidence commands."""

from __future__ import annotations

import argparse
from pathlib import Path

from sdf_cli.evidence_archive_scaffold import (
    EvidenceArchiveScaffoldWriteError,
    render_evidence_archive_scaffold,
    scaffold_evidence_archive,
)
from sdf_cli.receiver_cli_identity import lifecycle_identity_preflight
from sdf_cli.run_context_writer_output import render_run_context_write_result


def register_start_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    start_parser = subparsers.add_parser(
        "start",
        prog="sdf start",
        help="Start a governed evidence archive.",
        description=(
            "Start the durable .sdf/evidence/<change-id>/ archive path for "
            "governed changes. It initializes run-context timing in the "
            "evidence.md machine record and records any supplied declared "
            "run-context values."
        ),
        epilog=(
            "Examples:\n"
            "  sdf start --change-id <change-id>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    start_parser.add_argument(
        "--repo",
        default=".",
        help="Repository path. Defaults to the current directory.",
    )
    start_parser.add_argument(
        "--change-id",
        required=True,
        help="Stable evidence archive identifier.",
    )
    start_parser.add_argument(
        "--surface",
        help=(
            "Optional declared execution surface; use literal unknown when "
            "genuinely unknown."
        ),
    )
    start_parser.add_argument(
        "--model",
        help=(
            "Optional declared model name; use literal unknown when genuinely "
            "unknown."
        ),
    )
    start_parser.add_argument(
        "--reasoning",
        help=(
            "Optional declared reasoning setting; use literal unknown when "
            "genuinely unknown."
        ),
    )
    start_parser.add_argument(
        "--speed",
        help=(
            "Optional declared speed setting; use literal unknown when "
            "genuinely unknown."
        ),
    )


def handle_start(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> int:
    identity_error = lifecycle_identity_preflight(Path(args.repo).expanduser())
    if identity_error is not None:
        parser.error(identity_error)
    try:
        result = scaffold_evidence_archive(
            repo=args.repo,
            change_id=args.change_id,
            surface=args.surface,
            model=args.model,
            reasoning=args.reasoning,
            speed=args.speed,
            command_label="start",
        )
    except EvidenceArchiveScaffoldWriteError as error:
        parser.error(str(error))
    if result.invalid_reason is not None:
        parser.error(result.invalid_reason)
    output = render_evidence_archive_scaffold(result)
    if result.run_context_write_result is not None:
        output = "\n".join(
            [
                output,
                render_run_context_write_result(result.run_context_write_result),
            ]
        )
    print(output)
    return result.exit_code
