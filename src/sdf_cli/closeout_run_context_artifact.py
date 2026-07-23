"""Rendering helpers for the compact declared run-context handoff."""

from __future__ import annotations

from typing import Any

from sdf_cli.run_context import DECLARED_CONTEXT_FIELDS


def render_run_context_artifact_lines(run_context: Any) -> list[str]:
    context = " / ".join(
        f"{field} {run_context.declared_value(field)}"
        for field in DECLARED_CONTEXT_FIELDS
    )
    lines = [f"- Declared run context: {context}"]
    if not run_context.valid:
        lines.append(
            "- Run-context validation: "
            f"{'; '.join(run_context.errors) if run_context.errors else 'invalid'}"
        )
    return lines
