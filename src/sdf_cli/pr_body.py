"""PR body artifact writing and rendering."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from sdf_cli.closeout_check import CloseoutCheckResult, run_closeout_check
from sdf_cli.closeout_summary import render_closeout_summary_markdown
from sdf_cli.pr_body_artifact import (
    LOCAL_HANDOFF_DIRECTORY,
    PR_BODY_FILENAME,
    PrBodyWriteResult,
    pr_body_artifact_path,
    render_pr_body_write_result,
)
from sdf_cli.pr_body_contract_five import render_contract_five_pr_body_markdown
from sdf_cli.pr_body_link_rewrite import link_archive_file_references
from sdf_cli.pr_body_links import (
    LINK_MODE_REPO_RELATIVE,
    github_ref_stability_warnings,
)
from sdf_cli.pr_body_publication import publication_readiness_warnings
from sdf_cli.verification_runner import CommandExecutor, MonotonicClock

__all__ = [
    "LOCAL_HANDOFF_DIRECTORY",
    "PR_BODY_FILENAME",
    "PrBodyWriteResult",
    "pr_body_artifact_path",
    "render_pr_body_markdown",
    "render_pr_body_write_result",
    "write_pr_body_artifact",
]

EVIDENCE_HEADINGS_BY_PR_SECTION: dict[tuple[str, str], str] = {
    ("## Review focus", "evidence.md"): "Acceptance / Review Focus",
    ("## Run context", "evidence.md"): "Machine Record",
    ("## Guidance applied", "evidence.md"): "Guidance Applied",
    ("## Verification", "evidence.md"): "Verification",
}
CONTRACT_FIVE_HEADINGS_BY_PR_SECTION: dict[tuple[str, str], str] = {
    ("## Review focus", "evidence.md"): "Review focus",
    ("## Run context", "evidence.md"): "Machine Record",
    ("## Guidance applied", "evidence.md"): "Guidance applied",
    ("## Verification", "evidence.md"): "Machine Record",
}


def write_pr_body_artifact(
    repo: str,
    change_id: str,
    *,
    overwrite: bool = False,
    link_mode: str = LINK_MODE_REPO_RELATIVE,
    github_repo: str | None = None,
    github_ref: str | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    executor: CommandExecutor | None = None,
    clock: MonotonicClock | None = None,
    closeout_result: CloseoutCheckResult | None = None,
) -> PrBodyWriteResult:
    repo_path = Path(repo).expanduser()
    artifact_path = pr_body_artifact_path(change_id)
    target = repo_path / artifact_path
    already_exists = target.exists()
    warnings = github_ref_stability_warnings(
        link_mode=link_mode,
        github_ref=github_ref,
    )
    warnings += publication_readiness_warnings(
        repo_path,
        change_id,
        link_mode=link_mode,
        github_ref=github_ref,
    )
    if already_exists and not overwrite:
        return PrBodyWriteResult(
            change_id=change_id,
            artifact_path=artifact_path,
            written=False,
            existing=True,
            skipped_reason=(
                "already exists; use --overwrite during a new full closeout to "
                "replace it"
            ),
            warnings=warnings,
        )

    result = closeout_result or run_closeout_check(
        repo=repo,
        change_id=change_id,
        stdout=stdout,
        stderr=stderr,
        executor=executor,
        clock=clock,
    )
    if result.exit_code != 0:
        return PrBodyWriteResult(
            change_id=change_id,
            artifact_path=artifact_path,
            written=False,
            skipped_reason="closeout check did not pass; pr-body.md was not written",
            closeout_result=result,
            warnings=warnings,
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_pr_body_markdown(
        result,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    target.write_text(f"{content}\n", encoding="utf-8")
    return PrBodyWriteResult(
        change_id=change_id,
        artifact_path=artifact_path,
        written=True,
        overwritten=already_exists and overwrite,
        closeout_result=result,
        warnings=warnings,
    )


def render_pr_body_markdown(
    result: CloseoutCheckResult,
    *,
    link_mode: str = LINK_MODE_REPO_RELATIVE,
    github_repo: str | None = None,
    github_ref: str | None = None,
) -> str:
    if _contract_version(result) == 5:
        markdown = render_contract_five_pr_body_markdown(result)
    else:
        markdown = render_closeout_summary_markdown(result)
    linked_markdown = link_archive_file_references(
        markdown,
        change_id=result.evidence_result.change_id,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
        evidence_headings_by_pr_section=_evidence_heading_map(result),
    )
    return linked_markdown


def _evidence_heading_map(
    result: CloseoutCheckResult,
) -> dict[tuple[str, str], str]:
    evidence_file = next(
        (
            file
            for file in result.evidence_result.files
            if file.filename == "evidence.md"
        ),
        None,
    )
    if evidence_file is not None and evidence_file.contract_version == 5:
        return CONTRACT_FIVE_HEADINGS_BY_PR_SECTION
    return EVIDENCE_HEADINGS_BY_PR_SECTION


def _contract_version(result: CloseoutCheckResult) -> int | None:
    evidence_file = next(
        (
            file
            for file in result.evidence_result.files
            if file.filename == "evidence.md"
        ),
        None,
    )
    return evidence_file.contract_version if evidence_file is not None else None
