"""Strict materialisation and selection of one contract-5 evidence file."""

from __future__ import annotations

import base64
import binascii
from pathlib import Path

from sdf_cli.evidence_archive_scaffold import validate_change_id
from sdf_cli.open_pr_github import OpenPrGithubBoundary

MAX_EVIDENCE_FILE_BYTES = 1_000_000
EVIDENCE_PREFIX = ".sdf/evidence/"


def select_evidence_change_id(changed_files: tuple[str, ...]) -> str | None:
    evidence_paths = tuple(
        path for path in changed_files if path.startswith(EVIDENCE_PREFIX)
    )
    if len(evidence_paths) != 1:
        return None
    path = evidence_paths[0]
    parts = path.split("/")
    if len(parts) != 4 or parts[:2] != [".sdf", "evidence"]:
        return None
    change_id, filename = parts[2:]
    if filename != "evidence.md":
        return None
    if validate_change_id(change_id, command_label="open PR publication"):
        return None
    return change_id


def materialize_evidence(
    *,
    github: OpenPrGithubBoundary,
    github_repo: str,
    head_sha: str,
    change_id: str,
    destination: Path,
) -> Path:
    path = f"{EVIDENCE_PREFIX}{change_id}/evidence.md"
    payload = github.file_payload(github_repo, head_sha, path)
    content = _content(payload, path)
    target = destination / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return target


def docs_only_change(changed_files: tuple[str, ...]) -> bool:
    product_paths = tuple(
        path for path in changed_files if not path.startswith(EVIDENCE_PREFIX)
    )
    return bool(product_paths) and all(
        _documentation_path(path) for path in product_paths
    )


def _documentation_path(path: str) -> bool:
    return path.startswith("docs/") or path.endswith((".md", ".mdx", ".rst"))


def _content(payload: dict[str, object], path: str) -> bytes:
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise ValueError(f"evidence API payload is not a regular base64 file: {path}")
    raw = payload.get("content")
    if not isinstance(raw, str):
        raise ValueError(f"evidence API payload is missing content: {path}")
    try:
        content = base64.b64decode(
            raw.replace("\n", "").replace("\r", ""), validate=True
        )
    except (ValueError, binascii.Error) as error:
        raise ValueError(f"evidence API payload has invalid base64: {path}") from error
    if len(content) > MAX_EVIDENCE_FILE_BYTES:
        raise ValueError(f"evidence file exceeds the size limit: {path}")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"evidence file is not valid UTF-8: {path}") from error
    return content
