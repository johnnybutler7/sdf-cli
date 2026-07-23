from __future__ import annotations

import base64
from dataclasses import replace
from pathlib import Path

from tests.contract_five_pr_body_fixtures import write_contract_five_archive

from sdf_cli.evidence_front_matter import (
    load_evidence_machine_record,
    update_evidence_machine_record,
)
from sdf_cli.open_pr_body_publication import OpenPrBodyPublicationOptions
from sdf_cli.open_pr_github import ObservedPullRequest

REPO = "example/sdf-cli"
SHA = "0123456789abcdef0123456789abcdef01234567"


class FakeOpenPrGithub:
    def __init__(
        self,
        *,
        evidence: bytes,
        changed_files: tuple[str, ...],
        observations: tuple[ObservedPullRequest, ...] | None = None,
    ) -> None:
        self.evidence = evidence
        self.files = changed_files
        self.observations = observations or (observed_pr(),)
        self.observe_calls = 0
        self.file_calls: list[tuple[str, str, str]] = []
        self.update_calls: list[tuple[str, str, str]] = []

    def observe_pull_request(
        self, github_repo: str, pr_number: str
    ) -> ObservedPullRequest:
        index = min(self.observe_calls, len(self.observations) - 1)
        self.observe_calls += 1
        return self.observations[index]

    def changed_files(self, github_repo: str, pr_number: str) -> tuple[str, ...]:
        return self.files

    def file_payload(
        self, github_repo: str, head_sha: str, path: str
    ) -> dict[str, object]:
        self.file_calls.append((github_repo, head_sha, path))
        return {
            "type": "file",
            "encoding": "base64",
            "content": base64.b64encode(self.evidence).decode(),
        }

    def update_pr_body_if_current(
        self,
        pr_number: str,
        github_repo: str,
        expected: ObservedPullRequest,
        body: str,
    ) -> bool:
        index = min(self.observe_calls, len(self.observations) - 1)
        current = self.observations[index]
        if current != expected:
            return False
        self.update_calls.append((pr_number, github_repo, body))
        return True


def observed_pr(
    *,
    body: str = "Provider-native PR summary",
    state: str = "open",
    draft: bool = True,
    head_repository: str = REPO,
    base_ref: str = "main",
    head_sha: str = SHA,
    etag: str = 'W/"current-pr-state"',
) -> ObservedPullRequest:
    return ObservedPullRequest(
        number=41,
        state=state,
        draft=draft,
        body=body,
        head_sha=head_sha,
        head_repository=head_repository,
        base_ref=base_ref,
        etag=etag,
    )


def publication_options(destination: Path) -> OpenPrBodyPublicationOptions:
    return OpenPrBodyPublicationOptions(
        github_repo=REPO,
        pr_number="41",
        base_branch="main",
        evidence_data_dir=str(destination),
    )


def changed_files(change_id: str = "cloud-change") -> tuple[str, ...]:
    return (
        f".sdf/evidence/{change_id}/evidence.md",
        "src/sdf_cli/example.py",
    )


def evidence_bytes(
    source: Path,
    *,
    change_id: str = "cloud-change",
    surface: str = "codex_cloud",
    closeout_status: str = "passed",
    failed_check: str = "wheel-packaging-smoke",
    repository_name: str = "sdf-cli",
) -> bytes:
    write_contract_five_archive(
        source,
        change_id,
        intent=["- Standardize the provider-native PR body."],
        review_focus=["- Review the generated SDF reviewer handoff."],
        limits=["- Keep failed closeout claims honest."],
        declared={
            "surface": surface,
            "model": "cloud-model",
            "reasoning": "high",
            "speed": "fast",
        },
    )
    path = source / ".sdf" / "evidence" / change_id / "evidence.md"
    record = load_evidence_machine_record(path, change_id=change_id)
    assert record is not None
    passed = closeout_status == "passed"
    checks = [
        {"name": "ruff", "status": "passed", "duration_seconds": 0.10},
        {
            "name": failed_check,
            "status": "passed" if passed else "failed",
            "duration_seconds": 1.20,
        },
    ]
    update_evidence_machine_record(
        path,
        change_id=change_id,
        record=replace(
            record,
            repository={
                "name": repository_name,
                "path": "/untrusted/cloud/workspace",
                "github": "unavailable",
            },
            branch={"name": "provider/native-name", "head": "unavailable"},
            closed_at="2026-07-16T09:00:00+00:00" if passed else None,
            closeout_status=closeout_status,
            total_runs=1,
            failed_runs=0 if passed else 1,
            latest_run={
                "status": "passed" if passed else "failed",
                "total_duration_seconds": 1.30,
                "checks": checks,
            },
        ),
    )
    return path.read_bytes()
