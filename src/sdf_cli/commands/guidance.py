"""Read-only guidance routing checks for ``sdf guidance``."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.commands.guidance_rendering import render_guidance
from sdf_cli.commands.guidance_types import GuidanceFile, GuidanceResult
from sdf_cli.config.receiver_playbooks import ReceiverPlaybook, find_receiver_playbooks
from sdf_cli.repo_selection import unreadable_repo_reason

__all__ = ("GuidanceFile", "GuidanceResult", "check_guidance", "render_guidance")

REQUIRED_FILES: tuple[tuple[str, str], ...] = (
    ("SDF config", ".sdf/config.yml"),
    ("SDF agent instructions", ".sdf/agent-instructions.md"),
)


def check_guidance(repo: str) -> GuidanceResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = unreadable_repo_reason("guidance", repo_path, repo)
    if invalid_reason is not None:
        return GuidanceResult(
            repo_label=repo,
            repo_path=repo_path,
            required_files=(),
            portable_playbooks=(),
            receiver_playbooks=(),
            invalid_reason=invalid_reason,
        )

    required_files = tuple(
        GuidanceFile(
            label=label,
            path=relative_path,
            present=(repo_path / relative_path).is_file(),
        )
        for label, relative_path in REQUIRED_FILES
    )
    portable_playbooks = _find_portable_playbooks(repo_path)
    receiver_playbooks = _find_receiver_playbooks(repo_path)

    return GuidanceResult(
        repo_label=repo,
        repo_path=repo_path,
        required_files=required_files,
        portable_playbooks=portable_playbooks,
        receiver_playbooks=receiver_playbooks,
    )


def _find_portable_playbooks(repo_path: Path) -> tuple[str, ...]:
    playbooks_path = repo_path / ".sdf" / "playbooks"
    if not playbooks_path.is_dir():
        return ()

    paths = (
        path.relative_to(repo_path).as_posix()
        for path in playbooks_path.rglob("*.md")
        if path.is_file()
    )
    return tuple(sorted(paths))


def _find_receiver_playbooks(repo_path: Path) -> tuple[ReceiverPlaybook, ...]:
    return find_receiver_playbooks(repo_path)
