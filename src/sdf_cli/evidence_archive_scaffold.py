"""Explicit evidence archive scaffolding for governed changes."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sdf_cli.evidence_archive_contract import (
    ROUTINE_EVIDENCE_FILES,
)
from sdf_cli.evidence_archive_scaffold_output import next_step_lines
from sdf_cli.evidence_archive_templates import (
    EvidenceArchiveTemplateContext,
    template_for,
)
from sdf_cli.evidence_front_matter import initialize_evidence_machine_record
from sdf_cli.run_context_writer import (
    RunContextWriteResult,
    write_run_context_artifact,
)

CHANGE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class EvidenceArchiveFile:
    name: str
    created: bool
    @property
    def status(self) -> str:
        return "created" if self.created else "present"


@dataclass(frozen=True)
class EvidenceArchiveScaffoldResult:
    repo_label: str
    repo_path: Path
    change_id: str
    files: tuple[EvidenceArchiveFile, ...]
    run_context_timing_created: bool = False
    run_context_write_result: RunContextWriteResult | None = None
    invalid_reason: str | None = None
    @property
    def archive_path(self) -> str:
        return f".sdf/evidence/{self.change_id}"
    @property
    def exit_code(self) -> int:
        if (
            self.run_context_write_result is not None
            and not self.run_context_write_result.written
        ):
            return self.run_context_write_result.exit_code
        return 0


class EvidenceArchiveScaffoldWriteError(RuntimeError):
    """Raised when explicit evidence archive scaffolding fails."""


def validate_change_id(
    change_id: str,
    *,
    command_label: str = "start",
) -> str | None:
    if CHANGE_ID_PATTERN.fullmatch(change_id):
        return None
    return (
        f"{command_label}: change-id must use only letters, numbers, '.', "
        "'_', and '-', and must not contain path separators"
    )


def scaffold_evidence_archive(
    repo: str,
    change_id: str,
    *,
    surface: str | None = None,
    model: str | None = None,
    reasoning: str | None = None,
    speed: str | None = None,
    slice_timing_clock: Callable[[], datetime] | None = None,
    command_label: str = "start",
    started_at: str | None = None,
) -> EvidenceArchiveScaffoldResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = _invalid_repo_reason(repo_path, repo, command_label)
    if invalid_reason is not None:
        return EvidenceArchiveScaffoldResult(
            repo_label=repo,
            repo_path=repo_path,
            change_id=change_id,
            files=(),
            invalid_reason=invalid_reason,
        )
    invalid_reason = validate_change_id(change_id, command_label=command_label)
    if invalid_reason is not None:
        return EvidenceArchiveScaffoldResult(
            repo_label=repo,
            repo_path=repo_path,
            change_id=change_id,
            files=(),
            invalid_reason=invalid_reason,
        )
    archive_dir = repo_path / ".sdf" / "evidence" / change_id
    files = _scaffold_files(archive_dir)
    template_context = _template_context(
        repo_path=repo_path,
        archive_dir=archive_dir,
        change_id=change_id,
    )
    created_files: set[str] = set()
    for filename in files:
        destination = archive_dir / filename
        if destination.exists():
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("x", encoding="utf-8") as handle:
                handle.write(template_for(filename, template_context))
        except FileExistsError:
            continue
        except OSError as error:
            raise EvidenceArchiveScaffoldWriteError(
                f"{command_label}: failed to create "
                f"{destination.relative_to(repo_path).as_posix()}: "
                f"{error.strerror or error}"
            ) from error
        created_files.add(filename)
    run_context_timing_created = False
    if "evidence.md" in created_files:
        now = (slice_timing_clock or (lambda: datetime.now(timezone.utc)))()
        initialize_evidence_machine_record(
            archive_dir / "evidence.md",
            change_id=change_id,
            started_at=started_at
            or now.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
            repo_path=repo_path,
        )
        run_context_timing_created = True
    run_context_write_result = None
    if not run_context_timing_created or any(
        value is not None for value in (surface, model, reasoning, speed)
    ):
        run_context_write_result = write_run_context_artifact(
            repo=repo,
            change_id=change_id,
            surface=surface,
            model=model,
            reasoning=reasoning,
            speed=speed,
            clock=slice_timing_clock,
        )
    return EvidenceArchiveScaffoldResult(
        repo_label=repo,
        repo_path=repo_path,
        change_id=change_id,
        files=tuple(
            EvidenceArchiveFile(name=filename, created=filename in created_files)
            for filename in files
        ),
        run_context_timing_created=run_context_timing_created,
        run_context_write_result=run_context_write_result,
    )

def render_evidence_archive_scaffold(result: EvidenceArchiveScaffoldResult) -> str:
    lines = [f"Evidence archive: {result.archive_path}"]
    lines.extend(f"{file.status}: {file.name}" for file in result.files)
    timing_status = "created" if result.run_context_timing_created else "present"
    lines.append(
        f"run-context timing: {result.archive_path}/evidence.md machine record "
        f"({timing_status})"
    )
    if any(file.name == "evidence.md" and file.created for file in result.files):
        lines.append("versioned evidence machine record: initialized in evidence.md")
    lines.extend(next_step_lines(result))
    return "\n".join(lines)


def _template_context(
    *,
    repo_path: Path,
    archive_dir: Path,
    change_id: str,
) -> EvidenceArchiveTemplateContext:
    return EvidenceArchiveTemplateContext(
        change_id=change_id,
        repository=_repository_label(repo_path),
        branch="unknown",
        head_ref="unknown",
        narrative_filename="evidence.md",
    )


def _scaffold_files(archive_dir: Path) -> tuple[str, ...]:
    return ROUTINE_EVIDENCE_FILES


def _repository_label(repo_path: Path) -> str:
    return f"{repo_path.name} ({repo_path.resolve()})"


def _invalid_repo_reason(
    repo_path: Path,
    repo_label: str,
    command_label: str,
) -> str | None:
    if not repo_path.is_dir():
        return f"{command_label}: repo path is not a readable directory: {repo_label}"
    try:
        next(repo_path.iterdir(), None)
    except OSError:
        return f"{command_label}: repo path is not a readable directory: {repo_label}"
    return None
