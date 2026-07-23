"""Command-line entrypoint for the SDF CLI package."""

from __future__ import annotations

import argparse
import sys
import textwrap

from sdf_cli import __version__
from sdf_cli.commands.close import handle_close, register_close_command
from sdf_cli.commands.evidence import handle_start, register_start_command
from sdf_cli.commands.finalize_merged import (
    handle_finalize_merged,
    register_finalize_merged_command,
)
from sdf_cli.commands.publish_open_pr_body import (
    handle_publish_open_pr_body,
    register_publish_open_pr_body_command,
)
from sdf_cli.commands.receiver import handle_init, register_init_command
from sdf_cli.commands.repository_commands import (
    handle_guidance,
    handle_status,
    register_repository_commands,
)
from sdf_cli.commands.verification_command import (
    handle_verification,
    register_verification_commands,
)
from sdf_cli.identity import render_identity

_COMMAND_HELP_GROUPS = (
    (
        "Local commands",
        ("init", "status", "guidance", "verify", "start", "close"),
    ),
    (
        "Workflow/CI-only commands",
        ("publish-open-pr-body", "finalize-merged"),
    ),
)

_FIRST_USE_ORIENTATION = (
    "First use with the installed sdf command:\n"
    "  From the repository root:\n"
    "  1. sdf init\n"
    "  2. Configure and run sdf verify\n"
    "  3. Make the normal change, then run sdf close "
    "--change-id <change-id>\n"
    "     (the first close creates evidence and may stop for completion).\n"
    "  Use --repo /path/to/receiver only for another checkout.\n"
    "Use the repository's documentation and release notes for additional guidance."
)


class SdfHelpFormatter(argparse.HelpFormatter):
    """Group the top-level command list by customer surface tier."""

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        """Preserve the intentional first-use line breaks in top-level help."""
        del width
        return "".join(f"{indent}{line}\n" for line in text.splitlines())

    def _format_action(self, action: argparse.Action) -> str:
        if isinstance(action, argparse._SubParsersAction):
            grouped_help = self._format_grouped_subcommands(action)
            if grouped_help is not None:
                return grouped_help
        return super()._format_action(action)

    def _format_grouped_subcommands(
        self,
        action: argparse._SubParsersAction[argparse.ArgumentParser],
    ) -> str | None:
        choices = {choice.dest: choice for choice in action._choices_actions}
        grouped_names = {
            name for _title, names in _COMMAND_HELP_GROUPS for name in names
        }
        if not grouped_names.issubset(choices):
            return None

        lines: list[str] = []
        command_width = min(28, max(18, max(len(name) for name in choices) + 2))
        for title, names in _COMMAND_HELP_GROUPS:
            lines.append(f"{' ' * self._current_indent}{title}:")
            for name in names:
                lines.extend(
                    self._format_command_help(name, choices[name], command_width)
                )
            lines.append("")
        return "\n".join(lines)

    def _format_command_help(
        self,
        name: str,
        choice: argparse.Action,
        command_width: int,
    ) -> list[str]:
        command_indent = " " * (self._current_indent + 2)
        help_indent = " " * (self._current_indent + 2 + command_width)
        help_text = choice.help or ""
        wrapped = textwrap.wrap(
            help_text,
            width=max(20, self._width - len(help_indent)),
        )
        if not wrapped:
            return [f"{command_indent}{name}"]
        return [
            f"{command_indent}{name:<{command_width}}{wrapped[0]}",
            *(f"{help_indent}{line}" for line in wrapped[1:]),
        ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdf",
        usage=(
            "sdf [-h] [--version] [--identity] "
            "{init,status,guidance,verify,start,close,publish-open-pr-body,"
            "finalize-merged} ..."
        ),
        description=(
            "SDF CLI for governed AI-assisted delivery.\n\n"
            f"{_FIRST_USE_ORIENTATION}"
        ),
        formatter_class=SdfHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"software-dark-factory {__version__}",
    )
    parser.add_argument(
        "--identity",
        action="store_true",
        help="Report the executing implementation identity for diagnosis.",
    )
    subparsers = parser.add_subparsers(dest="command")

    register_init_command(subparsers)
    register_repository_commands(subparsers)
    register_verification_commands(subparsers)
    register_start_command(subparsers)
    register_close_command(subparsers)
    register_publish_open_pr_body_command(subparsers)
    register_finalize_merged_command(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.identity:
        print(render_identity())
        return 0

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "status":
        return handle_status(args, parser)

    if args.command == "guidance":
        return handle_guidance(args, parser)

    if args.command == "init":
        return handle_init(args, parser)

    if args.command == "verify":
        return handle_verification(args, parser)

    if args.command == "start":
        return handle_start(args, parser)

    if args.command == "close":
        return handle_close(args, parser)

    if args.command == "finalize-merged":
        return handle_finalize_merged(args, parser)

    if args.command == "publish-open-pr-body":
        return handle_publish_open_pr_body(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
