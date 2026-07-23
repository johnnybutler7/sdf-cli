"""Pre-mutation readiness policy for controlled open-PR body publication."""

from __future__ import annotations

import re
from pathlib import Path

from sdf_cli.evidence_archive_check import EvidenceArchiveCheckResult
from sdf_cli.evidence_contract_four import EvidenceMachineRecord
from sdf_cli.open_pr_github import ObservedPullRequest
from sdf_cli.pr_body_check import check_pr_body_content
from sdf_cli.pr_body_links import LINK_MODE_GITHUB

CLOUD_SURFACES = frozenset({"codex_cloud", "claude_cloud"})
FULL_SHA = re.compile(r"[0-9a-f]{40}")
GITHUB_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
MAX_GITHUB_PR_BODY_CHARACTERS = 65_536


def option_error(pr_number: str, github_repo: str, base_branch: str) -> str | None:
    if not pr_number.isdigit() or int(pr_number) < 1:
        return "pull request number is invalid or ambiguous"
    if not GITHUB_REPOSITORY.fullmatch(github_repo):
        return "GitHub repository identity is invalid or ambiguous"
    if not base_branch or any(character.isspace() for character in base_branch):
        return "trusted base branch identity is invalid or ambiguous"
    return None


def repository_state_ineligibility(
    *,
    pr_number: str,
    github_repo: str,
    base_branch: str,
    observed: ObservedPullRequest,
) -> str | None:
    if observed.number != int(pr_number):
        return "GitHub pull request identity is missing or ambiguous"
    if observed.state != "open":
        return "pull request is not open"
    if observed.draft is not True:
        return "pull request is not an open draft"
    if observed.head_repository != github_repo:
        return "pull request is from a fork or has ambiguous head repository state"
    if observed.base_ref != base_branch:
        return "pull request does not target the trusted base branch"
    if (
        observed.body is None
        or not observed.head_sha
        or not FULL_SHA.fullmatch(observed.head_sha)
        or not observed.etag
    ):
        return "GitHub pull request body or head identity is missing or ambiguous"
    return None


def is_contract_five(evidence: EvidenceArchiveCheckResult) -> bool:
    return any(
        file.filename == "evidence.md" and file.contract_version == 5
        for file in evidence.files
    )


def evidence_identity_error(
    github_repo: str, record: EvidenceMachineRecord | None
) -> str | None:
    expected_name = github_repo.rpartition("/")[2]
    if record is None or record.change_id == "":
        return "contract-5 evidence identity is missing or ambiguous"
    if record.repository.get("name") != expected_name:
        return "contract-5 evidence repository identity does not match the PR"
    recorded_github = record.repository.get("github")
    if recorded_github not in ("unavailable", github_repo):
        return "contract-5 evidence GitHub identity does not match the PR"
    if record.declared.get("surface") not in CLOUD_SURFACES:
        return "contract-5 evidence does not identify an eligible Cloud surface"
    return None


def handoff_readiness_error(
    *,
    repo_path: Path,
    change_id: str,
    handoff: str,
    artifact_path: str,
    github_repo: str,
    github_ref: str,
) -> str | None:
    if len(handoff) > MAX_GITHUB_PR_BODY_CHARACTERS:
        return "generated SDF reviewer handoff exceeds GitHub's body limit"
    handoff_check = check_pr_body_content(
        str(repo_path),
        change_id,
        handoff,
        artifact_path=artifact_path,
        link_mode=LINK_MODE_GITHUB,
        github_repo=github_repo,
        github_ref=github_ref,
    )
    if not handoff_check.passed:
        return "generated SDF reviewer handoff is not ready"
    return None
