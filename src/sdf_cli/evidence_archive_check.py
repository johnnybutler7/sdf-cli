"""Read-only evidence archive shape checking."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.evidence_archive_check_helpers import (
    front_matter_status,
    required_headings_for,
)
from sdf_cli.evidence_archive_check_rendering import (
    render_evidence_archive_check as _render_evidence_archive_check,
)
from sdf_cli.evidence_archive_contract import (
    REQUIRED_ARCHIVE_HEADINGS,
    archive_required_files,
)
from sdf_cli.evidence_archive_placeholders import (
    EvidenceArchivePlaceholder,
    unresolved_scaffold_placeholders,
)
from sdf_cli.evidence_archive_scaffold import validate_change_id
from sdf_cli.evidence_archive_verification_check import missing_verification_statuses


@dataclass(frozen=True)
class EvidenceArchiveFileCheck:
    filename: str
    exists: bool
    missing_headings: tuple[str, ...]
    missing_verification_statuses: tuple[str, ...] = ()
    unresolved_placeholders: tuple[EvidenceArchivePlaceholder, ...] = ()
    front_matter_error: str | None = None
    contract_version: int | None = None

    @property
    def passed(self) -> bool:
        return (
            self.exists
            and not self.missing_headings
            and not self.missing_verification_statuses
            and not self.unresolved_placeholders
            and self.front_matter_error is None
        )

@dataclass(frozen=True)
class EvidenceArchiveCheckResult:
    change_id: str
    repo_path: Path
    archive_exists: bool
    files: tuple[EvidenceArchiveFileCheck, ...]
    invalid_reason: str | None = None

    @property
    def archive_path(self) -> str:
        return f".sdf/evidence/{self.change_id}"

    @property
    def passed(self) -> bool:
        return (
            self.invalid_reason is None
            and self.archive_exists
            and all(file.passed for file in self.files)
        )

    @property
    def historical(self) -> bool:
        existing = tuple(file for file in self.files if file.exists)
        return bool(existing) and all(
            file.front_matter_error
            == (
                "historical or unsupported evidence machine record "
                "(contract 4 or 5 required)"
            )
            for file in existing
        )

    @property
    def exit_code(self) -> int:
        return 0 if self.passed or self.historical else 1


def check_evidence_archive(repo: str, change_id: str) -> EvidenceArchiveCheckResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = _invalid_repo_reason(repo_path, repo)
    if invalid_reason is None:
        invalid_reason = validate_change_id(
            change_id,
            command_label="evidence archive check",
        )
    if invalid_reason is not None:
        return EvidenceArchiveCheckResult(
            change_id=change_id,
            repo_path=repo_path,
            archive_exists=False,
            files=(),
            invalid_reason=invalid_reason,
        )

    archive_dir = repo_path / ".sdf" / "evidence" / change_id
    if not archive_dir.is_dir():
        return EvidenceArchiveCheckResult(
            change_id=change_id,
            repo_path=repo_path,
            archive_exists=False,
            files=(),
        )

    required_files, _ = archive_required_files(archive_dir)
    return EvidenceArchiveCheckResult(
        change_id=change_id,
        repo_path=repo_path,
        archive_exists=True,
        files=tuple(
            _check_file(
                archive_dir,
                filename,
                embedded_verification=True,
            )
            for filename in required_files
        ),
    )


def render_evidence_archive_check(result: EvidenceArchiveCheckResult) -> str:
    return _render_evidence_archive_check(result)


def _check_file(
    archive_dir: Path,
    filename: str,
    *,
    embedded_verification: bool = False,
) -> EvidenceArchiveFileCheck:
    path = archive_dir / filename
    required_headings = REQUIRED_ARCHIVE_HEADINGS[filename]
    if not path.is_file():
        return EvidenceArchiveFileCheck(
            filename=filename,
            exists=False,
            missing_headings=required_headings,
        )

    content = path.read_text(encoding="utf-8")
    headings = _heading_lines(content)
    front_matter_error, contract_version = front_matter_status(
        path, filename, archive_dir.name
    )
    malformed_machine_record = front_matter_error is not None and (
        not front_matter_error.startswith("historical or unsupported")
    )
    if filename == "evidence.md":
        required_headings = required_headings_for(
            filename,
            contract_version=contract_version,
            embedded_verification=embedded_verification,
        )
    if malformed_machine_record:
        required_headings = ()
    return EvidenceArchiveFileCheck(
        filename=filename,
        exists=True,
        missing_headings=tuple(
            heading for heading in required_headings if heading not in headings
        ),
        missing_verification_statuses=(
            ()
            if malformed_machine_record
            else missing_verification_statuses(
                filename,
                content,
                embedded_verification=embedded_verification,
                contract_version=contract_version or 5,
            )
        ),
        unresolved_placeholders=(
            ()
            if malformed_machine_record
            else unresolved_scaffold_placeholders(
                filename,
                content,
                contract_version=contract_version or 5,
            )
        ),
        front_matter_error=front_matter_error,
        contract_version=contract_version,
    )


def _heading_lines(markdown: str) -> set[str]:
    return {line.strip() for line in markdown.splitlines() if line.startswith("#")}


def _invalid_repo_reason(repo_path: Path, repo_label: str) -> str | None:
    message = (
        "evidence archive check: repo path is not a readable directory: "
        f"{repo_label}"
    )
    if not repo_path.is_dir():
        return message
    try:
        next(repo_path.iterdir(), None)
    except OSError:
        return message
    return None
