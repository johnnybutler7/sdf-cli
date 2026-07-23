"""Workflow-safe merged PR-body evidence link finalisation."""

from __future__ import annotations

from dataclasses import dataclass

from sdf_cli.pr_body_finalize_boundaries import GhCliPrBoundary, GithubPrBoundary
from sdf_cli.pr_body_finalize_links import finalize_body_links
from sdf_cli.pr_body_links import is_full_commit_sha, is_valid_github_repo


@dataclass(frozen=True)
class FinalizeMergedPrBodyOptions:
    pr_number: str
    github_repo: str
    merge_sha: str


@dataclass(frozen=True)
class FinalizeMergedPrBodyResult:
    pr_number: str
    merge_sha: str
    updated: bool
    skip_reason: str | None = None

    @property
    def exit_code(self) -> int:
        return 0


def validate_finalize_merged_pr_body_options(
    options: FinalizeMergedPrBodyOptions,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not is_valid_github_repo(options.github_repo):
        errors.append("--github-repo must look like owner/name")
    if not is_full_commit_sha(options.merge_sha):
        errors.append("--merge-sha must be a full 40-character commit SHA")
    return tuple(errors)


def finalize_merged_pr_body(
    options: FinalizeMergedPrBodyOptions,
    *,
    github: GithubPrBoundary | None = None,
) -> FinalizeMergedPrBodyResult:
    github = github or GhCliPrBoundary()
    live_body = github.read_pr_body(options.pr_number, options.github_repo)
    finalized = finalize_body_links(
        live_body,
        github_repo=options.github_repo,
        merge_sha=options.merge_sha,
    )
    if finalized == live_body:
        return FinalizeMergedPrBodyResult(
            pr_number=options.pr_number,
            merge_sha=options.merge_sha,
            updated=False,
            skip_reason="no eligible SDF evidence links required a merge-SHA rewrite",
        )

    github.update_pr_body(options.pr_number, options.github_repo, finalized)
    return FinalizeMergedPrBodyResult(
        pr_number=options.pr_number,
        merge_sha=options.merge_sha,
        updated=True,
    )


def render_finalize_merged_pr_body_result(
    result: FinalizeMergedPrBodyResult,
) -> str:
    lines = [
        "Merged PR body finalization",
        f"PR number: {result.pr_number}",
        f"merge SHA: {result.merge_sha}",
        f"updated: {'yes' if result.updated else 'no'}",
    ]
    if result.skip_reason:
        lines.append(f"skip reason: {result.skip_reason}")
    lines.append("github: live PR body mutation boundary")
    return "\n".join(lines)
