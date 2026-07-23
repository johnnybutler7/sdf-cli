"""Policy and rendering for manually controlled open-PR body publication."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sdf_cli.evidence_archive_check import check_evidence_archive
from sdf_cli.evidence_front_matter import load_evidence_machine_record
from sdf_cli.open_pr_evidence import (
    docs_only_change,
    materialize_evidence,
    select_evidence_change_id,
)
from sdf_cli.open_pr_github import OpenPrGithubBoundary
from sdf_cli.open_pr_publication_readiness import (
    MAX_GITHUB_PR_BODY_CHARACTERS as MAX_GITHUB_PR_BODY_CHARACTERS,
)
from sdf_cli.open_pr_publication_readiness import (
    evidence_identity_error,
    handoff_readiness_error,
    is_contract_five,
    option_error,
    repository_state_ineligibility,
)
from sdf_cli.pr_body import render_pr_body_markdown
from sdf_cli.pr_body_links import LINK_MODE_GITHUB
from sdf_cli.pr_body_recorded_closeout import recorded_closeout_result


@dataclass(frozen=True)
class OpenPrBodyPublicationOptions:
    github_repo: str
    pr_number: str
    base_branch: str
    evidence_data_dir: str


@dataclass(frozen=True)
class OpenPrBodyPublicationResult:
    updated: bool
    change_id: str | None = None
    surface: str | None = None
    head_sha: str | None = None
    closeout_status: str | None = None
    skip_reason: str | None = None

    @property
    def exit_code(self) -> int:
        return 0


def publish_open_pr_body(
    options: OpenPrBodyPublicationOptions,
    *,
    github: OpenPrGithubBoundary,
) -> OpenPrBodyPublicationResult:
    options_error = option_error(
        options.pr_number, options.github_repo, options.base_branch
    )
    if options_error:
        return _skipped(options_error)
    observed = github.observe_pull_request(options.github_repo, options.pr_number)
    ineligible = repository_state_ineligibility(
        pr_number=options.pr_number,
        github_repo=options.github_repo,
        base_branch=options.base_branch,
        observed=observed,
    )
    if ineligible:
        return _skipped(ineligible)

    changed_files = github.changed_files(options.github_repo, options.pr_number)
    change_id = select_evidence_change_id(changed_files)
    if change_id is None:
        return _skipped("contract-5 evidence change ID is missing or ambiguous")
    if docs_only_change(changed_files):
        return _skipped("documentation-only pull request keeps its existing body")

    assert observed.head_sha is not None
    repo_path = Path(options.evidence_data_dir).expanduser()
    try:
        materialize_evidence(
            github=github,
            github_repo=options.github_repo,
            head_sha=observed.head_sha,
            change_id=change_id,
            destination=repo_path,
        )
    except ValueError as error:
        return _skipped(f"committed evidence is unsafe or unusable: {error}")

    evidence = check_evidence_archive(str(repo_path), change_id)
    if not evidence.passed or not is_contract_five(evidence):
        return _skipped(
            "committed evidence is not a valid contract-5 archive", change_id
        )
    record = load_evidence_machine_record(
        repo_path / evidence.archive_path / "evidence.md", change_id=change_id
    )
    identity_error = evidence_identity_error(options.github_repo, record)
    if identity_error:
        return _skipped(identity_error, change_id)

    recorded = recorded_closeout_result(
        repo_path,
        change_id,
        evidence,
        allow_failed=True,
        include_checks=True,
    )
    if recorded is None:
        return _skipped("contract-5 evidence has no completed closeout", change_id)

    handoff = render_pr_body_markdown(
        recorded,
        link_mode=LINK_MODE_GITHUB,
        github_repo=options.github_repo,
        github_ref=observed.head_sha,
    )
    readiness_error = handoff_readiness_error(
        repo_path=repo_path,
        change_id=change_id,
        handoff=handoff,
        artifact_path=evidence.archive_path,
        github_repo=options.github_repo,
        github_ref=observed.head_sha,
    )
    if readiness_error:
        return _skipped(readiness_error, change_id)

    surface = record.declared["surface"]
    if observed.body == handoff:
        return OpenPrBodyPublicationResult(
            updated=False,
            change_id=change_id,
            surface=surface,
            head_sha=observed.head_sha,
            closeout_status=record.closeout_status,
            skip_reason="standard SDF reviewer handoff is already installed",
        )
    updated = github.update_pr_body_if_current(
        options.pr_number,
        options.github_repo,
        observed,
        handoff,
    )
    if not updated:
        return _skipped("pull request changed during publication; rerun", change_id)
    return OpenPrBodyPublicationResult(
        updated=True,
        change_id=change_id,
        surface=surface,
        head_sha=observed.head_sha,
        closeout_status=record.closeout_status,
    )


def render_open_pr_body_publication(result: OpenPrBodyPublicationResult) -> str:
    lines = [
        "Open PR SDF body publication",
        f"updated: {'yes' if result.updated else 'no'}",
    ]
    for label, value in (
        ("change ID", result.change_id),
        ("surface", result.surface),
        ("head SHA", result.head_sha),
        ("closeout status", result.closeout_status),
    ):
        if value:
            lines.append(f"{label}: {value}")
    if result.skip_reason:
        lines.append(f"skip reason: {result.skip_reason}")
    lines.append("github: PR body only")
    return "\n".join(lines)


def _skipped(reason: str, change_id: str | None = None) -> OpenPrBodyPublicationResult:
    return OpenPrBodyPublicationResult(
        updated=False, change_id=change_id, skip_reason=reason
    )
