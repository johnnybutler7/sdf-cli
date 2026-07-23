"""Rendering for read-only evidence archive checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdf_cli.evidence_archive_check import EvidenceArchiveCheckResult


def render_evidence_archive_check(result: EvidenceArchiveCheckResult) -> str:
    lines = [
        f"Evidence archive check: {result.archive_path}",
        f"Resolved repository path: {result.repo_path.resolve()}",
        f"status: {_status(result)}",
    ]
    if result.invalid_reason is not None:
        lines.append(result.invalid_reason)
        return "\n".join(lines)
    if not result.archive_exists:
        lines.append(f"missing archive: {result.archive_path}")
        return "\n".join(lines)

    for file in result.files:
        if file.exists:
            lines.append(f"present: {file.filename}")
        else:
            lines.append(f"missing file: {file.filename}")
            continue
        if file.front_matter_error:
            lines.append(
                f"invalid machine record in {file.filename}: {file.front_matter_error}"
            )
        lines.extend(
            f"missing heading in {file.filename}: {heading}"
            for heading in file.missing_headings
        )
        lines.extend(
            "missing verification status in "
            f"{file.filename}: {missing_verification_status}"
            for missing_verification_status in file.missing_verification_statuses
        )
        lines.extend(
            "unresolved scaffold placeholder in "
            f"{file.filename} {placeholder.section}: {placeholder.marker}"
            for placeholder in file.unresolved_placeholders
        )

    if any(file.unresolved_placeholders for file in result.files):
        lines.append(
            "recovery: replace scaffold prompts with specific evidence; "
            "the checker is read-only and does not auto-fill evidence."
        )
    if _has_malformed_machine_record(result):
        lines.extend(
            [
                "recovery: ## Machine Record is tool-owned. Restore evidence.md "
                "from Git when possible.",
                "Otherwise preserve any human-authored sections, then move or "
                "remove the broken change archive before rerunning "
                f"sdf start --change-id {result.change_id}.",
            ]
        )
    return "\n".join(lines)


def _has_malformed_machine_record(result: EvidenceArchiveCheckResult) -> bool:
    return any(
        file.front_matter_error is not None
        and not file.front_matter_error.startswith("historical or unsupported")
        for file in result.files
    )


def _status(result: EvidenceArchiveCheckResult) -> str:
    if result.passed:
        return "ready"
    if result.historical:
        return "historical (unsupported by current commands)"
    return "not ready"
