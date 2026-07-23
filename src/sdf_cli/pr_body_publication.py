"""Publication readiness checks for generated PR body handoffs."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.git_output import git_output
from sdf_cli.pr_body_links import LINK_MODE_REPO_RELATIVE


def publication_readiness_warnings(
    repo_path: Path,
    change_id: str,
    *,
    link_mode: str,
    github_ref: str | None,
) -> tuple[str, ...]:
    if link_mode == LINK_MODE_REPO_RELATIVE:
        return (
            "notice: repo-relative handoff is checked for local/offline review "
            "and is not publication-ready.",
        )
    if link_mode != "github" or not github_ref:
        return ()
    head = git_output(repo_path, "rev-parse", "HEAD")
    archive_path = f".sdf/evidence/{change_id}"
    if (
        head != github_ref
        or git_output(repo_path, "status", "--porcelain", "--", archive_path)
        or git_output(
            repo_path,
            "cat-file",
            "-e",
            f"{github_ref}:{archive_path}/evidence.md",
        )
        is None
    ):
        return (
            "warning: evidence archive is not committed at the referenced SHA; "
            "this handoff is not publication-ready. Commit evidence, then run "
            "sdf close --refresh-handoff.",
        )
    return ()


def committed_evidence_error(
    repo_path: Path, change_id: str, github_ref: str | None
) -> str | None:
    head = git_output(repo_path, "rev-parse", "HEAD")
    if head is None:
        return "local committed HEAD is unavailable"
    if github_ref != head:
        return "GitHub evidence ref must equal the local committed HEAD"
    archive_path = f".sdf/evidence/{change_id}"
    if git_output(repo_path, "status", "--porcelain", "--", archive_path):
        return "evidence archive is not committed at the referenced SHA"
    committed_archive = git_output(
        repo_path,
        "cat-file",
        "-e",
        f"{head}:{archive_path}/evidence.md",
    )
    if committed_archive is not None:
        return None
    return "evidence archive is not committed at the referenced SHA"
