"""Rendering for the read-only ``sdf verify --check`` report."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sdf_cli.config.verification import FocusedVerificationSubset, VerificationCommand

if TYPE_CHECKING:
    from sdf_cli.commands.verification import VerificationResult


def render_verification(result: VerificationResult) -> str:
    lines = [
        "SDF verify check",
        "",
        f"Repository: {result.repo_label}",
        _render_config_status(result.config_present),
        "",
        "Configured commands:",
    ]
    if result.commands:
        for command in result.commands:
            lines.extend(_render_command(command))
    else:
        lines.append("- none discovered")

    if result.starter_placeholder_detected:
        lines.extend(
            [
                "",
                "Receiver verification placeholder detected:",
                "- The scaffolded placeholder fails intentionally.",
                (
                    "- Replace it in .sdf/verification.yml with "
                    "receiver-owned commands."
                ),
                "- Then run:",
                "  sdf verify --repo <receiver>",
            ]
        )

    if result.config_error is not None:
        lines.extend(["", f"Config error: {result.config_error}"])

    lines.extend(["", "Focused verification:"])
    if result.focused_subsets:
        for subset in result.focused_subsets:
            lines.extend(_render_focused_subset(subset))
    else:
        lines.append("- not configured")

    lines.extend(
        [
            "Focused verification boundary:",
            "- Focused subsets are read-only visibility here.",
            "- They are supporting feedback during a slice.",
            (
                "- They do not replace `sdf verify --repo .` as the "
                "full closeout gate."
            ),
        ]
    )

    if result.visibility_issues:
        lines.extend(["", "Focused verification visibility issues:"])
        lines.extend(f"- {issue}" for issue in result.visibility_issues)

    if not result.config_present or (result.config_present and not result.commands):
        lines.extend(_render_recovery(result.repo_label, result.config_present))

    lines.extend(
        [
            "",
            "Execution boundary:",
            (
                "- `sdf verify` executes the configured commands "
                "from the selected repository."
            ),
            "- Required command failure fails the run.",
            "- Optional command failure is reported but does not fail the run.",
            "- This command does not write evidence files.",
            "- No PR body is updated.",
            (
                "- No approve, merge, repair, deploy, or release action is "
                "performed."
            ),
        ]
    )

    lines.extend(
        [
            "",
            f"Overall: {'ready' if result.ready else 'incomplete'}",
        ]
    )
    return "\n".join(lines)


def _render_command(command: VerificationCommand) -> list[str]:
    required = "yes" if command.required else "no"
    return [
        f"- {command.name}",
        f"  Command: {command.command}",
        f"  Required: {required}",
        f"  Track timing: {_yes_no(command.track_timing)}",
    ]


def _render_focused_subset(subset: FocusedVerificationSubset) -> list[str]:
    lines = [
        f"- {subset.name}",
        "  Commands:",
    ]
    lines.extend(f"  - {command_name}" for command_name in subset.commands)
    return lines


def _render_config_status(config_present: bool) -> str:
    status = "present" if config_present else "missing"
    return f"Config: .sdf/verification.yml ({status})"


def _render_recovery(repo_label: str, config_present: bool) -> list[str]:
    lines = [
        "",
        "Recovery:",
        (
            "- Confirm the selected checkout with "
            f"`sdf status --repo {repo_label}`."
        ),
    ]
    if config_present:
        lines.append(
            "- Add receiver-owned commands to `.sdf/verification.yml`, then "
            f"run `sdf verify --repo {repo_label}`."
        )
    else:
        lines.extend(
            (
                "- Initialize missing starter receiver files with "
                f"`sdf init --repo {repo_label}`.",
                "- Inspect the canonical manifest without writing with "
                f"`sdf init --repo {repo_label} --check`.",
            )
        )
    return lines


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
