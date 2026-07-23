"""Receiver initialization support for starter SDF files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.receiver_git_attributes import (
    ensure_sdf_evidence_generated_attribute,
    has_sdf_evidence_generated_attribute,
)
from sdf_cli.receiver_gitignore import (
    ensure_sdf_handoffs_ignore_rule,
    has_sdf_handoffs_ignore_rule,
)
from sdf_cli.receiver_payload_manifest import scaffold_receiver_payload_entries
from sdf_cli.receiver_scaffold_content import starter_content
from sdf_cli.receiver_scaffold_inspection import ReceiverScaffoldInspectionResult
from sdf_cli.repo_selection import unreadable_repo_reason


@dataclass(frozen=True)
class ReceiverScaffoldFile:
    path: str
    present: bool
    created: bool = False
    updated: bool = False
    required_content_present: bool | None = None

    @property
    def missing_parent(self) -> str | None:
        parent = Path(self.path).parent
        if self.present or str(parent) == ".":
            return None
        return parent.as_posix()


@dataclass(frozen=True)
class ReceiverScaffoldResult:
    repo_label: str
    repo_path: Path
    files: tuple[ReceiverScaffoldFile, ...]
    invalid_reason: str | None = None

    @property
    def ready(self) -> bool:
        return self.invalid_reason is None and all(file.present for file in self.files)

    @property
    def exit_code(self) -> int:
        return 0


class ReceiverScaffoldWriteError(RuntimeError):
    """Raised when safe receiver initialization cannot write a missing file."""


def check_receiver_scaffold(repo: str) -> ReceiverScaffoldResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = _invalid_repo_reason(repo_path, repo)
    if invalid_reason is not None:
        return ReceiverScaffoldResult(
            repo_label=repo,
            repo_path=repo_path,
            files=(),
            invalid_reason=invalid_reason,
        )

    files = tuple(
        ReceiverScaffoldFile(
            path=relative_path,
            present=(repo_path / relative_path).is_file(),
            required_content_present=_required_content_present(
                repo_path / relative_path, relative_path
            ),
        )
        for entry in scaffold_receiver_payload_entries()
        for relative_path in (entry.path,)
    )
    return ReceiverScaffoldResult(repo_label=repo, repo_path=repo_path, files=files)


def write_receiver_scaffold(repo: str) -> ReceiverScaffoldResult:
    checked = check_receiver_scaffold(repo)
    if checked.invalid_reason is not None:
        return checked
    contents = _preflight_missing_file_contents(checked)
    created_paths: set[str] = set()
    updated_paths: set[str] = set()
    for entry, file in zip(scaffold_receiver_payload_entries(), checked.files):
        if entry.write_policy == "create-or-append-exact-rule":
            destination = checked.repo_path / file.path
            try:
                outcome = _ensure_shared_rule(file.path, destination)
            except OSError as error:
                raise ReceiverScaffoldWriteError(
                    "init: failed to update "
                    f"{file.path}: {error.strerror or error}"
                ) from error
            if outcome == "created":
                created_paths.add(file.path)
            elif outcome == "updated":
                updated_paths.add(file.path)
            continue
        if file.present:
            continue
        destination = checked.repo_path / file.path
        try:
            content = contents[file.path]
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except OSError as error:
            raise ReceiverScaffoldWriteError(
                "init: failed to create "
                f"{file.path}: {error.strerror or error}"
            ) from error
        created_paths.add(file.path)
    files = tuple(
        ReceiverScaffoldFile(
            path=relative_path,
            present=(checked.repo_path / relative_path).is_file(),
            created=relative_path in created_paths,
            updated=relative_path in updated_paths,
            required_content_present=_required_content_present(
                checked.repo_path / relative_path, relative_path
            ),
        )
        for entry in scaffold_receiver_payload_entries()
        for relative_path in (entry.path,)
    )
    return ReceiverScaffoldResult(
        repo_label=repo,
        repo_path=checked.repo_path,
        files=files,
    )


def _preflight_missing_file_contents(checked: ReceiverScaffoldResult) -> dict[str, str]:
    contents: dict[str, str] = {}
    for entry, file in zip(scaffold_receiver_payload_entries(), checked.files):
        if entry.write_policy == "create-or-append-exact-rule" or file.present:
            continue
        try:
            contents[file.path] = starter_content(file.path)
        except OSError as error:
            raise ReceiverScaffoldWriteError(
                "init: required packaged resource unavailable for "
                f"{file.path}: {error.strerror or error}"
            ) from error
    return contents


def render_receiver_scaffold(
    result: ReceiverScaffoldResult,
    *,
    inspection: ReceiverScaffoldInspectionResult,
) -> str:
    created_count = sum(file.created for file in result.files)
    updated_count = sum(file.updated for file in result.files)
    unchanged_count = len(result.files) - created_count - updated_count
    lines = [
        "SDF init",
        f"Repository: {result.repo_label}",
        (
            "Installed or left in place: "
            f"{created_count} created, {updated_count} shared rules updated, "
            f"{unchanged_count} existing files unchanged."
        ),
        (
            "Starter groups: assistant entry files; .sdf guidance, configuration, "
            "and contracts; Git evidence/handoff rules."
        ),
        (
            "Manifest: "
            f"{inspection.missing_count} missing, "
            f"{inspection.matching_count} matching, "
            f"{inspection.drifted_count} drifted."
        ),
        (
            "Assistant entry: start through AGENTS.md or CLAUDE.md, then read "
            ".sdf guidance."
        ),
        (
            "Ownership: repository files and configuration stay yours; SDF never "
            "overwrites existing files."
        ),
    ]
    if inspection.drifted_count:
        lines.append(
            "Attention: manual review required for "
            f"{_entry_count(inspection.drifted_count)}."
        )
        lines.extend(
            (
                (
                    "Next action: inspect and review with "
                    f"sdf init --repo {result.repo_label} --check."
                ),
                (
                    "After review: configure .sdf/verification.yml, then run "
                    f"sdf verify --repo {result.repo_label}."
                ),
            )
        )
    else:
        lines.extend(
            (
                (
                    "Required setup: configure .sdf/verification.yml with your "
                    "repository-trusted checks."
                ),
                f"Next action: sdf verify --repo {result.repo_label}",
            )
        )
    lines.append(
        "Then follow the close-first journey: make one ordinary change, run sdf "
        "close, complete evidence, run sdf close again, commit, refresh the "
        "handoff, and open a manually reviewed draft PR."
    )
    return "\n".join(lines)


def _entry_count(count: int) -> str:
    return f"{count} {'entry' if count == 1 else 'entries'}"


def _invalid_repo_reason(repo_path: Path, repo_label: str) -> str | None:
    return unreadable_repo_reason("init", repo_path, repo_label)


def _required_content_present(path: Path, relative_path: str) -> bool | None:
    if relative_path not in {".gitattributes", ".gitignore"} or not path.is_file():
        return None
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    if relative_path == ".gitattributes":
        return has_sdf_evidence_generated_attribute(content)
    return has_sdf_handoffs_ignore_rule(content)


def _ensure_shared_rule(relative_path: str, destination: Path) -> str:
    if relative_path == ".gitattributes":
        return ensure_sdf_evidence_generated_attribute(destination)
    if relative_path == ".gitignore":
        return ensure_sdf_handoffs_ignore_rule(destination)
    raise ValueError(f"unsupported shared receiver rule: {relative_path}")
