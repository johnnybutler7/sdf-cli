"""Read-only canonical-manifest inspection for receiver initialization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.receiver_git_attributes import has_sdf_evidence_generated_attribute
from sdf_cli.receiver_gitignore import has_sdf_handoffs_ignore_rule
from sdf_cli.receiver_payload_manifest import (
    CORE_RECEIVER_PAYLOAD_MANIFEST_NAME,
    ReceiverPayloadEntry,
    inspection_receiver_payload_entries,
)
from sdf_cli.receiver_scaffold_content import starter_content
from sdf_cli.repo_selection import unreadable_repo_reason

BRIDGE_MARKERS: tuple[str, ...] = (
    "<!-- SDF Front Door: start -->",
    "- `.sdf/agent-instructions.md`",
    "<!-- SDF Front Door: end -->",
)

CLAUDE_BRIDGE_MARKERS: tuple[str, ...] = (
    "This repository uses SDF guidance for governed AI-assisted delivery.",
    "Before making changes, read:",
    "- `.sdf/agent-instructions.md`",
    "SDF-specific operating guidance lives under `.sdf/`.",
)


@dataclass(frozen=True)
class ReceiverScaffoldInspection:
    entry: ReceiverPayloadEntry
    status: str
    action: str


@dataclass(frozen=True)
class ReceiverScaffoldInspectionResult:
    repo_label: str
    repo_path: Path
    inspections: tuple[ReceiverScaffoldInspection, ...]
    invalid_reason: str | None = None

    @property
    def exit_code(self) -> int:
        return (
            1
            if any(item.status in {"missing", "drifted"} for item in self.inspections)
            else 0
        )

    @property
    def drifted_count(self) -> int:
        return sum(1 for item in self.inspections if item.status == "drifted")

    @property
    def missing_count(self) -> int:
        return sum(1 for item in self.inspections if item.status == "missing")

    @property
    def matching_count(self) -> int:
        return sum(1 for item in self.inspections if item.status == "matching")


def inspect_receiver_scaffold(repo: str) -> ReceiverScaffoldInspectionResult:
    repo_path = Path(repo).expanduser()
    invalid_reason = _invalid_repo_reason(repo_path, repo)
    if invalid_reason is not None:
        return ReceiverScaffoldInspectionResult(
            repo_label=repo,
            repo_path=repo_path,
            inspections=(),
            invalid_reason=invalid_reason,
        )

    inspections = tuple(
        _inspect_entry(repo_path, entry)
        for entry in inspection_receiver_payload_entries()
    )
    return ReceiverScaffoldInspectionResult(
        repo_label=repo,
        repo_path=repo_path,
        inspections=inspections,
    )


def render_receiver_scaffold_inspection(
    result: ReceiverScaffoldInspectionResult,
) -> str:
    lines = [
        "SDF init check",
        f"Repository: {result.repo_label}",
        f"Manifest: {CORE_RECEIVER_PAYLOAD_MANIFEST_NAME}",
        "Entries:",
    ]
    for inspection in result.inspections:
        entry = inspection.entry
        lines.append(
            "- "
            f"{entry.path} | "
            f"class: {', '.join(entry.classes)} | "
            f"source: {entry.source} | "
            f"status: {inspection.status} | "
            f"action: {inspection.action}"
        )
    lines.extend(
        (
            "Boundary:",
            "- This command is read-only.",
            (
                "- It reports each canonical manifest entry as missing, matching, "
                "or drifted."
            ),
            (
                "- It compares copied portable sources and required bridge or "
                "generated-file markers when those entries are present."
            ),
            "- It does not create directories or files.",
            "- It does not overwrite, repair, migrate, install packages, run "
            "verification, mutate PRs, approve, merge, deploy, or release.",
            "Summary:",
            f"- missing: {result.missing_count}",
            f"- matching: {result.matching_count}",
            f"- drifted: {result.drifted_count}",
        )
    )
    return "\n".join(lines)


def _inspect_entry(
    repo_path: Path, entry: ReceiverPayloadEntry
) -> ReceiverScaffoldInspection:
    path = repo_path / entry.path
    if not path.is_file():
        return ReceiverScaffoldInspection(
            entry,
            entry.fresh_receiver_status,
            entry.fresh_receiver_action,
        )

    if entry.comparison_kind == "exact":
        try:
            current = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ReceiverScaffoldInspection(entry, "drifted", "manual-review")
        if current == starter_content(entry.path):
            return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")
        return ReceiverScaffoldInspection(entry, "drifted", "manual-review")

    if entry.comparison_kind in {"bridge", "claude-bridge"}:
        try:
            current = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ReceiverScaffoldInspection(entry, "drifted", "manual-review")
        markers = (
            BRIDGE_MARKERS
            if entry.comparison_kind == "bridge"
            else CLAUDE_BRIDGE_MARKERS
        )
        if all(marker in current for marker in markers):
            return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")
        return ReceiverScaffoldInspection(entry, "drifted", "manual-review")

    if entry.comparison_kind == "config":
        try:
            current = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ReceiverScaffoldInspection(entry, "drifted", "manual-review")
        if "automatic_execution_permitted: false" in current:
            return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")
        return ReceiverScaffoldInspection(entry, "drifted", "manual-review")

    if entry.comparison_kind == "gitattributes":
        try:
            current = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ReceiverScaffoldInspection(entry, "drifted", "manual-review")
        if has_sdf_evidence_generated_attribute(current):
            return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")
        return ReceiverScaffoldInspection(entry, "drifted", "manual-review")

    if entry.comparison_kind == "gitignore":
        try:
            current = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ReceiverScaffoldInspection(entry, "drifted", "manual-review")
        if has_sdf_handoffs_ignore_rule(current):
            return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")
        return ReceiverScaffoldInspection(entry, "drifted", "manual-review")

    if entry.comparison_kind == "shape-only":
        return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")

    return ReceiverScaffoldInspection(entry, "matching", "leave-unchanged")


def _invalid_repo_reason(repo_path: Path, repo_label: str) -> str | None:
    return unreadable_repo_reason("init check", repo_path, repo_label)
