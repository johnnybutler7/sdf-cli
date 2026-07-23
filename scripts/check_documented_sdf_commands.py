"""Check current operational docs against the registered SDF commands."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sdf_cli.main import build_parser

HISTORICAL_MARKER = "<!-- sdf-command-check: historical -->"
INLINE_CODE = re.compile(r"`([^`]+)`")
COMMAND = re.compile(r"(?<![\w-])(?:[\w./-]+/)?sdf\s+([a-z][a-z-]*)\b")
SOURCE_MODULE = re.compile(r"(?:PYTHONPATH=[^\s]+\s+)?python3 -m sdf_cli\.main\b")
ACTIVE_LOCATIONS = (
    "AGENTS.md",
    "GETTING-STARTED.md",
    "README.md",
    ".sdf/agent-instructions.md",
    ".sdf/standard-sdf-non-claims.md",
    ".sdf/contracts",
    ".sdf/playbooks",
    "docs/AGENTS.md",
    "docs/README.md",
    "docs/architecture",
    "docs/playbooks",
    "docs/inspection",
    "docs/product/assessments",
    "docs/product/boundaries",
    "docs/product/receivers",
    "docs/product/releases",
    "docs/product/workflows",
    "docs/verification",
    "docs/workflows",
)


@dataclass(frozen=True)
class UnsupportedCommand:
    path: Path
    line: int
    command: str


@dataclass(frozen=True)
class SourceModuleInvocation:
    path: Path
    line: int


def registered_commands() -> frozenset[str]:
    """Return command names registered by the actual CLI parser."""

    for action in build_parser()._actions:
        if isinstance(action, argparse._SubParsersAction):
            return frozenset(action.choices)
    return frozenset()


def unsupported_commands(
    root: Path, commands: frozenset[str]
) -> tuple[UnsupportedCommand, ...]:
    """Find unsupported commands in active Markdown command examples."""

    findings: list[UnsupportedCommand] = []
    for path in active_documents(root):
        text = path.read_text(encoding="utf-8")
        if HISTORICAL_MARKER in text:
            continue
        findings.extend(_unsupported_in_document(path, text, commands))
    return tuple(findings)


def ordinary_source_module_invocations(
    root: Path,
) -> tuple[SourceModuleInvocation, ...]:
    """Find source-module commands outside explicitly labelled fallback context."""

    findings: list[SourceModuleInvocation] = []
    for path in active_documents(root):
        lines = path.read_text(encoding="utf-8").splitlines()
        if HISTORICAL_MARKER in "\n".join(lines):
            continue
        for index, line in enumerate(lines):
            if SOURCE_MODULE.search(line) and not _is_source_fallback_context(
                lines, index
            ):
                findings.append(SourceModuleInvocation(path, index + 1))
    return tuple(findings)


def active_documents(root: Path) -> tuple[Path, ...]:
    """Return guidance and retained historical records, excluding evidence."""

    paths: list[Path] = []
    for location in ACTIVE_LOCATIONS:
        path = root / location
        if path.is_file():
            paths.append(path)
        elif path.is_dir():
            paths.extend(path.rglob("*.md"))
    return tuple(sorted(paths))


def render(
    command_findings: Iterable[UnsupportedCommand],
    source_findings: Iterable[SourceModuleInvocation] = (),
) -> str:
    """Render one coherent report for command and invocation findings."""

    command_findings = tuple(command_findings)
    source_findings = tuple(source_findings)
    lines = ["Documented SDF command consistency"]
    if command_findings:
        lines.extend(["", "Unsupported commands:"])
        lines.extend(
        f"- {finding.path}:{finding.line}: sdf {finding.command}"
            for finding in command_findings
        )
    if source_findings:
        lines.extend(["", "Ordinary source-module invocations:"])
        lines.extend(
            f"- {finding.path}:{finding.line}" for finding in source_findings
        )
    status = "failed" if command_findings or source_findings else "passed"
    lines.extend(["", f"Overall: {status}"])
    return "\n".join(lines)


def _is_source_fallback_context(lines: list[str], index: int) -> bool:
    context = "\n".join(lines[max(0, index - 8) : index + 1]).lower()
    section_context = "\n".join(lines[max(0, index - 30) : index + 1]).lower()
    return (
        "### source-module fallback" in section_context
        or "## source-module fallback" in section_context
        or
        ("source-module" in context and "fallback" in context)
        or any(
            label in context
            for label in (
                "source-module fallback",
                "source development",
                "diagnos",
                "ci isolation",
                "ci-isolation",
            )
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check active SDF documentation command names."
    )
    parser.add_argument("--repo", default=".", help="Repository path.")
    args = parser.parse_args(argv)
    root = Path(args.repo).resolve()
    command_findings = unsupported_commands(root, registered_commands())
    source_findings = ordinary_source_module_invocations(root)
    print(render(command_findings, source_findings))
    return 1 if command_findings or source_findings else 0


def _unsupported_in_document(
    path: Path, text: str, commands: frozenset[str]
) -> list[UnsupportedCommand]:
    findings: list[UnsupportedCommand] = []
    fenced = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        examples = (line,) if fenced else INLINE_CODE.findall(line)
        for example in examples:
            for command in COMMAND.findall(example):
                if command not in commands:
                    findings.append(UnsupportedCommand(path, line_number, command))
    return findings


if __name__ == "__main__":
    raise SystemExit(main())
