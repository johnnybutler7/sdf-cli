"""Status extraction for machine-owned closeout records."""

from __future__ import annotations

from sdf_cli.closeout_check import CloseoutCheckResult


def closeout_status(result: CloseoutCheckResult) -> str:
    return "passed" if result.exit_code == 0 else "failed"


def evidence_status(result: CloseoutCheckResult) -> str:
    return "ready" if result.evidence_result.exit_code == 0 else "not_ready"


def verification_status(result: CloseoutCheckResult) -> str:
    verification = result.verification_result
    if verification.status == "recorded":
        return "recorded" if verification.exit_code == 0 else "failed"
    if verification.status == "skipped":
        return "skipped"
    return "passed" if verification.exit_code == 0 else "failed"


def yaml_scalar(value: str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
