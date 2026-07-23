"""Read-only verification boundary checks for ``sdf verify --check``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.config.verification import (
    FocusedVerificationSubset,
    VerificationCommand,
    load_verification_config,
)
from sdf_cli.repo_selection import unreadable_repo_reason
from sdf_cli.verification_placeholder import is_starter_verification_placeholder

CONFIG_RELATIVE_PATH = ".sdf/verification.yml"


@dataclass(frozen=True)
class VerificationResult:
    repo_label: str
    repo_path: Path
    config_present: bool
    commands: tuple[VerificationCommand, ...]
    focused_subsets: tuple[FocusedVerificationSubset, ...] = ()
    visibility_issues: tuple[str, ...] = ()
    config_error: str | None = None
    invalid_reason: str | None = None

    @property
    def starter_placeholder_detected(self) -> bool:
        return any(
            is_starter_verification_placeholder(command) for command in self.commands
        )

    @property
    def ready(self) -> bool:
        return (
            self.invalid_reason is None
            and self.config_error is None
            and self.config_present
            and len(self.commands) > 0
        )

    @property
    def exit_code(self) -> int:
        return 0 if self.ready else 1


def check_verification(repo: str) -> VerificationResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = unreadable_repo_reason("verification", repo_path, repo)
    if invalid_reason is not None:
        return VerificationResult(
            repo_label=repo,
            repo_path=repo_path,
            config_present=False,
            commands=(),
            config_error=None,
            invalid_reason=invalid_reason,
        )

    config_path = repo_path / CONFIG_RELATIVE_PATH
    if not config_path.is_file():
        return VerificationResult(
            repo_label=repo,
            repo_path=repo_path,
            config_present=False,
            commands=(),
            config_error=None,
        )

    config = load_verification_config(config_path)
    return VerificationResult(
        repo_label=repo,
        repo_path=repo_path,
        config_present=config.present,
        commands=config.commands,
        focused_subsets=config.focused_subsets,
        visibility_issues=config.visibility_issues,
        config_error=config.error if config.present and not config.valid else None,
    )
