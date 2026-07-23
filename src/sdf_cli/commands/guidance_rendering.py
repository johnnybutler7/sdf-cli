"""Rendering helpers for ``sdf guidance`` results."""

from __future__ import annotations

from sdf_cli.commands.guidance_types import GuidanceFile, GuidanceResult
from sdf_cli.config.receiver_playbooks import ReceiverPlaybook


def render_guidance(result: GuidanceResult) -> str:
    lines = [
        "SDF guidance",
        "",
        f"Repository: {result.repo_label}",
        f"Resolved repository path: {result.repo_path.resolve()}",
    ]
    lines.extend(_render_required_file(file) for file in result.required_files)
    lines.extend(
        [
            "",
            "Portable SDF playbooks:",
        ]
    )
    if result.portable_playbooks:
        lines.extend(f"- {path}" for path in result.portable_playbooks)
    else:
        lines.append("- none found")

    lines.extend(
        [
            "",
            "Receiver playbooks:",
        ]
    )
    if result.receiver_playbooks:
        lines.extend(
            _render_receiver_playbook(playbook)
            for playbook in result.receiver_playbooks
        )
    else:
        lines.append("- none configured")

    if not result.has_routed_guidance:
        lines.extend(
            [
                "",
                "No matching repository guidance was discovered.",
                "- No portable SDF playbooks or configured receiver playbooks "
                "were found for this repository.",
                "- Check the receiver's .sdf installation or the --repo path "
                "points at the intended receiver checkout.",
            ]
        )

    lines.extend(
        [
            "",
            "Boundary:",
            "- This command reports available routed guidance.",
            "- It does not decide which playbooks were applied to a slice.",
            "- Record slice-local playbook judgement manually in the PR body, "
            "run notes, or configured evidence surface.",
            "",
            f"Overall: {'ready' if result.ready else 'incomplete'}",
        ]
    )
    return "\n".join(lines)


def _render_required_file(file: GuidanceFile) -> str:
    status = "present" if file.present else "missing"
    return f"{file.label}: {status} ({file.path})"


def _render_receiver_playbook(playbook: ReceiverPlaybook) -> str:
    status = "present" if playbook.present else "missing"
    categories = ", ".join(playbook.categories)
    suffix = f" [{categories}]" if categories else ""
    return f"- {playbook.name}: {status} ({playbook.path}){suffix}"
