"""Render the small SDF-owned verification narrative block."""

from __future__ import annotations

from pathlib import Path

from sdf_cli.verification_formatting import format_duration, status_label
from sdf_cli.verification_results import VerificationRunResult

START = "<!-- sdf:verification-summary:start -->"
END = "<!-- sdf:verification-summary:end -->"


def verification_summary_lines(result: VerificationRunResult) -> list[str]:
    status = "passed" if result.exit_code == 0 else "failed"
    checks = result.command_results
    duration = sum(command.duration_seconds or 0.0 for command in checks)
    return [
        "- Configured verification: "
        f"{status} — {len(checks)} {'check' if len(checks) == 1 else 'checks'}, "
        f"{format_duration(duration)} total. "
        "Compact run facts are in the machine record.",
        f"  - Status: {status}.",
        "- Verification limits: records configured executions and executor-supplied "
        "statuses; it does not infer categories or parse command output.",
    ]


def refresh_evidence_verification_summary(
    evidence_path: Path, result: VerificationRunResult
) -> bool:
    text = evidence_path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return False
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    block = "\n".join((START, *verification_summary_lines(result), END))
    evidence_path.write_text(before + block + after, encoding="utf-8")
    return True


def compact_check_summary(result: VerificationRunResult) -> str | None:
    if not result.command_results:
        return None
    return "; ".join(_check_label(check) for check in result.command_results)


def _check_label(command) -> str:
    details = [status_label(command)]
    if command.duration_seconds is not None:
        details.append(format_duration(command.duration_seconds))
    return f"`{command.name}` ({', '.join(details)})"
