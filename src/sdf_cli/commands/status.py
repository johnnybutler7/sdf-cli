"""Read-only repository readiness checks for ``sdf status``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.receiver_cli_identity import (
    ReceiverCliIdentityComparison,
    compare_receiver_cli_identity,
)
from sdf_cli.repo_selection import unreadable_repo_reason


@dataclass(frozen=True)
class StatusFile:
    label: str
    path: str
    present: bool


@dataclass(frozen=True)
class StatusResult:
    repo_label: str
    repo_path: Path
    files: tuple[StatusFile, ...]
    evidence_archive_count: int = 0
    identity_comparison: ReceiverCliIdentityComparison | None = None
    invalid_reason: str | None = None

    @property
    def ready(self) -> bool:
        return self.invalid_reason is None and all(file.present for file in self.files)

    @property
    def diagnosis(self) -> str:
        if self.invalid_reason is not None:
            return "invalid"
        if self.ready:
            return "ready"
        if any(file.present for file in self.files if file.path.startswith(".sdf/")):
            return "incomplete"
        return "uninstalled"

    @property
    def exit_code(self) -> int:
        return 0 if self.ready else 1


REQUIRED_FILES: tuple[tuple[str, str], ...] = (
    ("SDF config", ".sdf/config.yml"),
    ("SDF agent instructions", ".sdf/agent-instructions.md"),
    ("SDF verification config", ".sdf/verification.yml"),
    ("Root agent bridge", "AGENTS.md"),
)

def check_status(repo: str) -> StatusResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = unreadable_repo_reason(
        "status",
        repo_path,
        repo,
        headline="\n".join(
            (
                "status: could not inspect receiver repository at supplied "
                f"--repo path: {repo}",
                "The path does not exist or is not a readable directory.",
            )
        ),
    )
    if invalid_reason is not None:
        return StatusResult(
            repo_label=repo,
            repo_path=repo_path,
            files=(),
            invalid_reason=invalid_reason,
        )

    files = tuple(
        _status_file(repo_path, label, path)
        for label, path in REQUIRED_FILES
    )
    return StatusResult(
        repo_label=repo,
        repo_path=repo_path,
        files=files,
        evidence_archive_count=_evidence_archive_count(repo_path),
        identity_comparison=compare_receiver_cli_identity(repo_path),
    )


def _status_file(
    repo_path: Path,
    label: str,
    relative_path: str,
) -> StatusFile:
    return StatusFile(
        label=label,
        path=relative_path,
        present=(repo_path / relative_path).is_file(),
    )


def _evidence_archive_count(repo_path: Path) -> int:
    evidence_dir = repo_path / ".sdf" / "evidence"
    if not evidence_dir.is_dir():
        return 0
    return sum(
        1
        for candidate in evidence_dir.iterdir()
        if candidate.is_dir() and (candidate / "evidence.md").is_file()
    )
