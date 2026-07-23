"""Terminal rendering for ``sdf status`` results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdf_cli.commands.status import StatusFile, StatusResult


STATUS_BOUNDARY: tuple[str, ...] = (
    "This command reports readiness/status visibility.",
    "It does not inspect copied portable file drift.",
    "It does not inspect or repair existing AGENTS.md bridge content.",
    (
        "Run sdf init --repo <receiver> --check to inspect "
        "canonical bridge presence and copied portable file drift."
    ),
)


def render_status(result: StatusResult) -> str:
    lines = [
        "SDF status",
        "",
        f"Repository: {result.repo_label}",
        f"Resolved repository path: {result.repo_path.resolve()}",
        *_identity_lines(result),
    ]
    lines.extend(_render_file(file) for file in result.files)
    lines.extend(
        [
            "",
            f"Overall: {result.diagnosis}",
        ]
    )
    if result.diagnosis == "uninstalled":
        lines.extend(_render_install_action(result.repo_label))
    elif result.diagnosis == "incomplete":
        lines.extend(_render_recovery(result.repo_label))
    elif result.evidence_archive_count == 0:
        lines.extend(_render_no_evidence_guidance(result.repo_label))
    lines.extend(["", "Boundary:"])
    lines.extend(f"- {item}" for item in _status_boundary(result))
    return "\n".join(lines)


def _render_no_evidence_guidance(repo_label: str) -> list[str]:
    return [
        "",
        "Evidence:",
        "- No governed change evidence has been recorded yet.",
        (
            "- This means the receiver is ready but no governed change archive "
            "exists for review."
        ),
        (
            "- Normal next step: make the change, then run "
            f"`sdf close --repo {repo_label} --change-id <change-id>`."
        ),
        "- The first close creates evidence and may stop for evidence completion.",
    ]


def _render_install_action(repo_label: str) -> list[str]:
    return [
        "",
        "Diagnosis:",
        "- SDF is not installed in this repository.",
        "",
        "Next action:",
        f"- To install the starter SDF files, run `sdf init --repo {repo_label}`.",
    ]


def _render_recovery(repo_label: str) -> list[str]:
    return [
        "",
        "Diagnosis:",
        "- SDF appears to be installed, but the installation is incomplete or broken.",
        "",
        "Recovery:",
        (
            "- If this is the wrong checkout, rerun with "
            "`sdf status --repo /path/to/receiver`."
        ),
        (
            "- To initialize missing starter receiver files for this checkout, run "
            f"`sdf init --repo {repo_label}`."
        ),
        (
            "- To inspect the canonical manifest without writing, run "
            f"`sdf init --repo {repo_label} --check`."
        ),
    ]


def _status_boundary(result: StatusResult) -> tuple[str, ...]:
    if result.diagnosis == "uninstalled":
        return STATUS_BOUNDARY[:-1]
    return STATUS_BOUNDARY


def _render_file(file: StatusFile) -> str:
    status = "present" if file.present else "missing"
    return f"{file.label}: {status} ({file.path})"


def _identity_lines(result: StatusResult) -> list[str]:
    comparison = result.identity_comparison
    if comparison is None:
        return []
    receiver_release = comparison.receiver_release or "unavailable"
    cli_version = comparison.cli_version or "unavailable"
    return [
        f"Receiver-declared Front Door release: {receiver_release}",
        f"Executing CLI version: {cli_version}",
        f"Receiver/operator identity: {comparison.result}",
    ]
