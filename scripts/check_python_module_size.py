"""Audit Python module sizes against SDF CLI guidance."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

WARN_THRESHOLD = 150
FAIL_THRESHOLD = 250
IGNORED_DIRS = frozenset(
    {
        "__pycache__",
        ".venv",
        ".git",
        ".mypy_cache",
        ".ruff_cache",
    }
)


@dataclass(frozen=True)
class ModuleSizeFinding:
    path: str
    lines: int


@dataclass(frozen=True)
class ModuleSizeAudit:
    warnings: tuple[ModuleSizeFinding, ...]
    failures: tuple[ModuleSizeFinding, ...]

    @property
    def exit_code(self) -> int:
        return 1 if self.failures else 0


def audit_paths(
    paths: Iterable[str | Path],
    *,
    warn_threshold: int = WARN_THRESHOLD,
    fail_threshold: int = FAIL_THRESHOLD,
) -> ModuleSizeAudit:
    """Return module-size findings for Python files under the given paths."""

    findings = []
    for path in _python_files(paths):
        line_count = _count_physical_lines(path)
        display_path = _display_path(path)
        if line_count >= fail_threshold:
            findings.append(("failure", ModuleSizeFinding(display_path, line_count)))
        elif line_count >= warn_threshold:
            findings.append(("warning", ModuleSizeFinding(display_path, line_count)))

    warnings = tuple(finding for kind, finding in findings if kind == "warning")
    failures = tuple(finding for kind, finding in findings if kind == "failure")
    return ModuleSizeAudit(warnings=warnings, failures=failures)


def render_audit(
    audit: ModuleSizeAudit,
    *,
    warn_threshold: int = WARN_THRESHOLD,
    fail_threshold: int = FAIL_THRESHOLD,
) -> str:
    lines = [
        "Python module-size audit",
        "",
        f"Warn threshold: {warn_threshold} lines",
        f"Fail threshold: {fail_threshold} lines",
        "",
        "Warnings:",
    ]
    lines.extend(_render_findings(audit.warnings))
    lines.extend(["", "Failures:"])
    lines.extend(_render_findings(audit.failures))
    lines.extend(["", f"Overall: {'failed' if audit.failures else 'passed'}"])
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    audit = audit_paths(args)
    print(render_audit(audit))
    return audit.exit_code


def _python_files(paths: Iterable[str | Path]) -> tuple[Path, ...]:
    files: list[Path] = []
    for path_value in paths:
        path = Path(path_value)
        if path.is_file() and path.suffix == ".py" and not _is_ignored(path):
            files.append(path)
        elif path.is_dir() and not _is_ignored(path):
            files.extend(_walk_python_files(path))

    return tuple(sorted(files, key=_display_path))


def _walk_python_files(root: Path) -> Iterable[Path]:
    for child in sorted(root.iterdir(), key=lambda candidate: candidate.name):
        if _is_ignored(child):
            continue
        if child.is_dir():
            yield from _walk_python_files(child)
        elif child.is_file() and child.suffix == ".py":
            yield child


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def _count_physical_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8") as python_file:
            return sum(1 for _line in python_file)
    except OSError:
        return 0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _render_findings(findings: tuple[ModuleSizeFinding, ...]) -> list[str]:
    if not findings:
        return ["- none"]
    return [f"- {finding.path}: {finding.lines} lines" for finding in findings]


if __name__ == "__main__":
    raise SystemExit(main())
