"""Refresh a checked PR-body handoff from recorded closeout evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.evidence_archive_check import check_evidence_archive
from sdf_cli.pr_body import (
    pr_body_artifact_path,
    write_pr_body_artifact,
)
from sdf_cli.pr_body_check import check_pr_body_artifact
from sdf_cli.pr_body_links import LINK_MODE_GITHUB
from sdf_cli.pr_body_publication import committed_evidence_error
from sdf_cli.pr_body_recorded_closeout import recorded_closeout_result


@dataclass(frozen=True)
class PrBodyRefreshResult:
    change_id: str
    artifact_path: str
    refreshed: bool
    publication_ready: bool
    message: str

    @property
    def exit_code(self) -> int:
        return 0 if self.refreshed else 1


def refresh_pr_body_handoff(
    repo: str,
    change_id: str,
    *,
    link_mode: str,
    github_repo: str | None = None,
    github_ref: str | None = None,
) -> PrBodyRefreshResult:
    """Render a handoff without rerunning closeout or changing evidence."""
    repo_path = Path(repo).expanduser()
    artifact_path = pr_body_artifact_path(change_id)
    evidence_result = check_evidence_archive(repo, change_id)
    recorded = _recorded_closeout_result(repo_path, change_id, evidence_result)
    if recorded is None:
        return _not_ready(
            change_id,
            "recorded passing closeout evidence is required; run sdf close first",
        )

    if link_mode == LINK_MODE_GITHUB:
        committed_error = committed_evidence_error(repo_path, change_id, github_ref)
        if committed_error:
            return _not_ready(change_id, committed_error)

    write_result = write_pr_body_artifact(
        repo=repo,
        change_id=change_id,
        overwrite=True,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
        closeout_result=recorded,
    )
    if not write_result.written:
        reason = write_result.skipped_reason or "handoff was not written"
        return _not_ready(change_id, reason)
    check_result = check_pr_body_artifact(
        repo,
        change_id,
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    if not check_result.passed:
        return _not_ready(change_id, "refreshed handoff did not pass its check")

    if link_mode == LINK_MODE_GITHUB:
        return PrBodyRefreshResult(
            change_id,
            artifact_path,
            True,
            True,
            "publication-ready: committed evidence links target the current HEAD; "
            "publish this generated handoff verbatim",
        )
    return PrBodyRefreshResult(
        change_id,
        artifact_path,
        True,
        False,
        "local-only: repo-relative links are checked for offline review; "
        "refresh with GitHub commit links before PR publication",
    )


def render_pr_body_refresh(result: PrBodyRefreshResult) -> str:
    return "\n".join(
        [
            "SDF handoff refresh",
            f"PR body artifact: {result.artifact_path}",
            f"status: {'ready' if result.refreshed else 'not ready'}",
            result.message,
            "github: not mutated",
        ]
    )


def _not_ready(change_id: str, message: str) -> PrBodyRefreshResult:
    return PrBodyRefreshResult(
        change_id,
        pr_body_artifact_path(change_id),
        False,
        False,
        f"publication blocked: {message}",
    )


def _recorded_closeout_result(repo_path: Path, change_id: str, evidence_result):
    return recorded_closeout_result(
        repo_path,
        change_id,
        evidence_result,
    )
