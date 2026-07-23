"""Result types for ``sdf guidance``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.config.receiver_playbooks import ReceiverPlaybook


@dataclass(frozen=True)
class GuidanceFile:
    label: str
    path: str
    present: bool


@dataclass(frozen=True)
class GuidanceResult:
    repo_label: str
    repo_path: Path
    required_files: tuple[GuidanceFile, ...]
    portable_playbooks: tuple[str, ...]
    receiver_playbooks: tuple[ReceiverPlaybook, ...]
    invalid_reason: str | None = None

    @property
    def ready(self) -> bool:
        return self.invalid_reason is None and all(
            file.present for file in self.required_files
        ) and all(playbook.present for playbook in self.receiver_playbooks)

    @property
    def has_routed_guidance(self) -> bool:
        return bool(self.portable_playbooks) or bool(self.receiver_playbooks)

    @property
    def exit_code(self) -> int:
        return 0 if self.ready else 1
