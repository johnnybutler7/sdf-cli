"""GitHub API boundary for controlled open-PR body publication."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Mapping, Protocol


@dataclass(frozen=True)
class ObservedPullRequest:
    number: int | None
    state: str | None
    draft: bool | None
    body: str | None
    head_sha: str | None
    head_repository: str | None
    base_ref: str | None
    etag: str | None


class OpenPrGithubBoundary(Protocol):
    def observe_pull_request(
        self, github_repo: str, pr_number: str
    ) -> ObservedPullRequest: ...

    def changed_files(self, github_repo: str, pr_number: str) -> tuple[str, ...]: ...

    def file_payload(
        self, github_repo: str, head_sha: str, path: str
    ) -> dict[str, object]: ...

    def update_pr_body_if_current(
        self,
        pr_number: str,
        github_repo: str,
        expected: ObservedPullRequest,
        body: str,
    ) -> bool: ...


class GhOpenPrBoundary:
    """Read current PR data through GitHub and delegate the body-only write."""

    def observe_pull_request(
        self, github_repo: str, pr_number: str
    ) -> ObservedPullRequest:
        result = subprocess.run(
            ["gh", "api", "--include", f"repos/{github_repo}/pulls/{pr_number}"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        response = _included_response(result.stdout)
        if response.status != 200:
            raise RuntimeError(f"GitHub PR observation returned HTTP {response.status}")
        return observed_pull_request(json.loads(response.body), etag=response.etag)

    def changed_files(self, github_repo: str, pr_number: str) -> tuple[str, ...]:
        result = subprocess.run(
            [
                "gh",
                "api",
                "--paginate",
                f"repos/{github_repo}/pulls/{pr_number}/files?per_page=100",
                "--jq",
                ".[].filename",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        return tuple(line for line in result.stdout.splitlines() if line)

    def file_payload(
        self, github_repo: str, head_sha: str, path: str
    ) -> dict[str, object]:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{github_repo}/contents/{path}",
                "--method",
                "GET",
                "-f",
                f"ref={head_sha}",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(result.stdout)
        return payload if isinstance(payload, dict) else {}

    def update_pr_body_if_current(
        self,
        pr_number: str,
        github_repo: str,
        expected: ObservedPullRequest,
        body: str,
    ) -> bool:
        if not expected.etag:
            return False
        endpoint = f"repos/{github_repo}/pulls/{pr_number}"
        result = subprocess.run(
            [
                "gh",
                "api",
                "--include",
                "--header",
                f"If-None-Match: {expected.etag}",
                endpoint,
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        response = _included_response(result.stdout)
        if response.status == 200:
            return False
        if response.status != 304:
            result.check_returncode()
            raise RuntimeError(
                f"GitHub PR freshness check returned HTTP {response.status}"
            )
        subprocess.run(
            ["gh", "api", "--method", "PATCH", endpoint, "--input", "-"],
            input=json.dumps({"body": body}),
            check=True,
            text=True,
            stdout=subprocess.DEVNULL,
        )
        return True


def observed_pull_request(
    payload: object, *, etag: str | None = None
) -> ObservedPullRequest:
    data = _mapping(payload)
    head = _mapping(data.get("head"))
    base = _mapping(data.get("base"))
    head_repo = _mapping(head.get("repo"))
    return ObservedPullRequest(
        number=_integer(data.get("number")),
        state=_text(data.get("state")),
        draft=data.get("draft") if isinstance(data.get("draft"), bool) else None,
        body=_body(data.get("body")),
        head_sha=_text(head.get("sha")),
        head_repository=_text(head_repo.get("full_name")),
        base_ref=_text(base.get("ref")),
        etag=etag,
    )


@dataclass(frozen=True)
class _IncludedResponse:
    status: int
    etag: str | None
    body: str


def _included_response(output: str) -> _IncludedResponse:
    normalized = output.replace("\r\n", "\n")
    header_text, separator, body = normalized.partition("\n\n")
    lines = header_text.splitlines()
    if not separator or not lines:
        raise RuntimeError("GitHub API response did not include HTTP headers")
    status_parts = lines[0].split()
    if len(status_parts) < 2 or not status_parts[1].isdigit():
        raise RuntimeError("GitHub API response has an invalid HTTP status line")
    headers = {}
    for line in lines[1:]:
        name, found, value = line.partition(":")
        if found:
            headers[name.lower()] = value.strip()
    return _IncludedResponse(
        status=int(status_parts[1]),
        etag=headers.get("etag"),
        body=body,
    )


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _body(value: object) -> str | None:
    return "" if value is None else value if isinstance(value, str) else None


def _integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
