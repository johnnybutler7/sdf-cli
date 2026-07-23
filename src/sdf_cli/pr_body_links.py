"""PR body evidence link modes and local validation helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

LINK_MODE_REPO_RELATIVE = "repo-relative"
LINK_MODE_GITHUB = "github"
EVIDENCE_LINK_LABELS: dict[str, str] = {
    "evidence.md": "Evidence notes",
}
GITHUB_REPO_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$"
)
FULL_COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
GITHUB_HEADING_PUNCTUATION_PATTERN = re.compile(r"[^\w\s-]")
GITHUB_REF_STABILITY_WARNING = (
    "warning: --github-ref is not a full 40-character commit SHA; branch refs "
    "are the recommended active draft review default after the branch is "
    "pushed, but may break after merge or branch deletion. Durable "
    "commit-SHA evidence links belong to the post-merge finalizer."
)


@dataclass(frozen=True)
class EvidenceLinkTarget:
    change_id: str
    link_mode: str = LINK_MODE_REPO_RELATIVE
    github_repo: str | None = None
    github_ref: str | None = None

    def link_for(self, filename: str, *, heading: str | None = None) -> str:
        relative_path = f".sdf/evidence/{self.change_id}/{filename}"
        fragment = f"#{github_heading_slug(heading)}" if heading else ""
        if self.link_mode == LINK_MODE_REPO_RELATIVE:
            return f"{relative_path}{fragment}"
        return (
            f"https://github.com/{self.github_repo}/blob/"
            f"{self.github_ref}/{relative_path}{fragment}"
        )


@dataclass(frozen=True)
class GithubLinkContext:
    repo: str
    ref: str


def validate_pr_body_link_options(
    *,
    link_mode: str,
    github_repo: str | None,
    github_ref: str | None,
    require_immutable_ref: bool = True,
) -> tuple[str, ...]:
    errors: list[str] = []
    if link_mode == LINK_MODE_GITHUB:
        if not github_repo:
            errors.append("--github-repo is required when --link-mode github")
        elif not is_valid_github_repo(github_repo):
            errors.append("--github-repo must look like owner/name")
        if not github_ref:
            errors.append("--github-ref is required when --link-mode github")
        elif require_immutable_ref and not is_full_commit_sha(github_ref):
            errors.append(
                "--github-ref must be the full 40-character immutable PR head SHA"
            )
        elif _is_local_absolute_path(github_ref) or _has_unsafe_github_ref(github_ref):
            errors.append("--github-ref must be a branch or SHA, not a local path")
    return tuple(errors)


def is_full_commit_sha(value: str) -> bool:
    return FULL_COMMIT_SHA_PATTERN.match(value) is not None


def github_heading_slug(heading: str) -> str:
    """Return GitHub's stable fragment form for a unique Markdown heading."""
    text = re.sub(r"^#{1,6}\s+", "", heading.strip()).lower()
    text = GITHUB_HEADING_PUNCTUATION_PATTERN.sub("", text)
    return re.sub(r"\s", "-", text)


def github_ref_stability_warnings(
    *,
    link_mode: str,
    github_ref: str | None,
) -> tuple[str, ...]:
    if link_mode != LINK_MODE_GITHUB or not github_ref:
        return ()
    if is_full_commit_sha(github_ref):
        return ()
    return (GITHUB_REF_STABILITY_WARNING,)


def is_valid_github_repo(value: str) -> bool:
    if _is_local_absolute_path(value) or "\\" in value:
        return False
    return GITHUB_REPO_PATTERN.match(value) is not None


def github_context(
    *,
    link_mode: str,
    github_repo: str | None,
    github_ref: str | None,
) -> GithubLinkContext | None:
    if (
        link_mode != LINK_MODE_GITHUB
        or not github_repo
        or not github_ref
        or not is_valid_github_repo(github_repo)
    ):
        return None
    return GithubLinkContext(repo=github_repo, ref=github_ref)


def local_target_for_evidence_link(
    repo_path: Path,
    link: str,
    *,
    archive_path: str,
    github_context: GithubLinkContext | None,
) -> Path | None:
    if is_repo_relative_evidence_link(link, archive_path):
        return repo_path / link.partition("#")[0]
    github_filename = github_evidence_filename(
        link,
        archive_path=archive_path,
        github_context=github_context,
    )
    if github_filename is None:
        return None
    return repo_path / archive_path / github_filename


def github_evidence_filename(
    link: str,
    *,
    archive_path: str,
    github_context: GithubLinkContext | None,
) -> str | None:
    if github_context is None:
        return None
    prefix = f"https://github.com/{github_context.repo}/blob/{github_context.ref}/"
    archive_prefix = f"{archive_path}/"
    if not link.startswith(prefix):
        return None
    path = link.removeprefix(prefix).partition("#")[0]
    if not path.startswith(archive_prefix):
        return None
    return path.removeprefix(archive_prefix)


def wrong_github_evidence_links(
    links: tuple[str, ...],
    *,
    archive_path: str,
    github_context: GithubLinkContext | None,
) -> tuple[str, ...]:
    wrong: list[str] = []
    evidence_marker = f"/{archive_path}/"
    for link in links:
        if not link.startswith("https://github.com/") or evidence_marker not in link:
            continue
        if github_evidence_filename(
            link,
            archive_path=archive_path,
            github_context=github_context,
        ) is None:
            wrong.append(link)
    return tuple(wrong)


def repo_relative_evidence_links(
    links: tuple[str, ...],
    *,
    archive_path: str,
    link_mode: str,
) -> tuple[str, ...]:
    if link_mode != LINK_MODE_GITHUB:
        return ()
    return tuple(
        link for link in links if is_repo_relative_evidence_link(link, archive_path)
    )


def is_local_absolute_evidence_link(link: str) -> bool:
    return _is_local_absolute_path(link) and ".sdf/evidence" in link.replace("\\", "/")


def is_repo_relative_evidence_link(link: str, archive_path: str) -> bool:
    return link.startswith(f"{archive_path}/") or link.startswith(".sdf/evidence/")


def _is_local_absolute_path(value: str) -> bool:
    return (
        value.startswith("/")
        or value.casefold().startswith("file:")
        or re.match(r"^[A-Za-z]:[\\/]", value) is not None
    )


def _has_unsafe_github_ref(value: str) -> bool:
    return (
        value.strip() != value
        or not value
        or any(character.isspace() for character in value)
        or "\\" in value
    )
