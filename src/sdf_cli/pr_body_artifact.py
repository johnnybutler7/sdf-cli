"""PR body artifact names and write result rendering."""

from __future__ import annotations

from dataclasses import dataclass

from sdf_cli.closeout_check import CloseoutCheckResult

PR_BODY_FILENAME = "pr-body.md"
LOCAL_HANDOFF_DIRECTORY = ".sdf/handoffs"


@dataclass(frozen=True)
class PrBodyWriteResult:
    change_id: str
    artifact_path: str
    written: bool
    overwritten: bool = False
    existing: bool = False
    skipped_reason: str | None = None
    closeout_result: CloseoutCheckResult | None = None
    warnings: tuple[str, ...] = ()

    @property
    def exit_code(self) -> int:
        return 0 if self.written else 1


def pr_body_artifact_path(change_id: str) -> str:
    return f"{LOCAL_HANDOFF_DIRECTORY}/{change_id}/{PR_BODY_FILENAME}"


def render_pr_body_write_result(result: PrBodyWriteResult) -> str:
    lines = [f"PR body artifact: {result.artifact_path}"]
    if result.written:
        status = "overwritten" if result.overwritten else "written"
        lines.append(f"status: {status}")
        lines.append("source: close renderer")
        lines.append("github: not mutated")
        lines.extend(result.warnings)
        return "\n".join(lines)

    lines.append("status: not written")
    if result.skipped_reason:
        lines.append(result.skipped_reason)
    lines.append("github: not mutated")
    lines.extend(result.warnings)
    return "\n".join(lines)
