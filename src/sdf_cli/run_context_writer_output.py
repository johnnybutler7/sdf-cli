"""Console rendering for scaffold-owned declared run-context updates."""

from __future__ import annotations

from sdf_cli.run_context_writer import RunContextWriteResult


def render_run_context_write_result(result: RunContextWriteResult) -> str:
    lines = [f"Declared run context: {result.artifact_path}"]
    if result.written:
        lines.append("status: written")
        lines.append("source: declared run context")
        lines.append("github: not mutated")
        return "\n".join(lines)
    lines.append("status: failed" if result.failed else "status: already exists")
    if result.skipped_reason:
        lines.append(result.skipped_reason)
    lines.append("github: not mutated")
    return "\n".join(lines)
