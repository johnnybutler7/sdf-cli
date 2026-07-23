"""PR body check result model and rendering."""

from __future__ import annotations

from dataclasses import dataclass

from sdf_cli.pr_body_artifact import PR_BODY_FILENAME


@dataclass(frozen=True)
class PrBodyCheckResult:
    change_id: str
    artifact_path: str
    exists: bool
    missing_sections: tuple[str, ...] = ()
    missing_evidence_links: tuple[str, ...] = ()
    broken_evidence_links: tuple[str, ...] = ()
    absolute_evidence_links: tuple[str, ...] = ()
    repo_relative_evidence_links: tuple[str, ...] = ()
    wrong_github_evidence_links: tuple[str, ...] = ()
    malformed_evidence_links: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    recovery_command: str | None = None
    recheck_command: str | None = None

    @property
    def passed(self) -> bool:
        return (
            self.exists
            and not self.missing_sections
            and not self.missing_evidence_links
            and not self.broken_evidence_links
            and not self.absolute_evidence_links
            and not self.repo_relative_evidence_links
            and not self.wrong_github_evidence_links
            and not self.malformed_evidence_links
        )

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1


def render_pr_body_check(result: PrBodyCheckResult) -> str:
    lines = [
        f"PR body check: {result.artifact_path}",
        f"status: {'ready' if result.passed else 'not ready'}",
    ]
    if not result.exists:
        lines.append(f"missing file: {PR_BODY_FILENAME}")
        _append_recovery_command(lines, result)
        lines.extend(result.warnings)
        return "\n".join(lines)

    lines.append(f"present: {PR_BODY_FILENAME}")
    for section in result.missing_sections:
        lines.append(f"missing section: {section}")
    for filename in result.missing_evidence_links:
        lines.append(f"missing evidence link: {filename}")
    for link in result.broken_evidence_links:
        lines.append(f"broken evidence link: {link}")
    for link in result.absolute_evidence_links:
        lines.append(f"absolute evidence link: {link}")
    for link in result.repo_relative_evidence_links:
        lines.append(f"repo-relative evidence link in GitHub mode: {link}")
    for link in result.wrong_github_evidence_links:
        lines.append(f"wrong GitHub evidence link: {link}")
    for link in result.malformed_evidence_links:
        lines.append(f"malformed evidence link: {link}")
    if not result.passed:
        _append_recovery_command(lines, result)
    lines.extend(result.warnings)
    return "\n".join(lines)


def _append_recovery_command(lines: list[str], result: PrBodyCheckResult) -> None:
    if result.recovery_command:
        lines.append(f"recovery: {result.recovery_command}")
    if result.recheck_command:
        lines.append(f"then check: {result.recheck_command}")
