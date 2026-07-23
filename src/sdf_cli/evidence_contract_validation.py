"""Validation rules for supported evidence machine records."""

from __future__ import annotations

from datetime import datetime
from math import isfinite

_CLOSEOUT_STATUSES = {"open", "passed", "failed"}
_RUN_STATUSES = {"passed", "failed", "blocked", "skipped"}
_CHECK_STATUSES = {"passed", "failed", "optional_failed", "skipped"}


def valid_machine_values(values: dict[str, object]) -> bool:
    if not all(_nonempty(values.get(field)) for field in ("written_by", "change_id")):
        return False
    writer = str(values["written_by"])
    if not writer.startswith("software-dark-factory ") or not writer.removeprefix(
        "software-dark-factory "
    ).strip():
        return False
    if values.get("closeout_status") not in _CLOSEOUT_STATUSES:
        return False
    if not _required_start(values.get("started_at")) or not _optional_timestamp(
        values.get("closed_at")
    ):
        return False
    declared = values.get("declared")
    if not isinstance(declared, dict) or any(
        not _nonempty(declared.get(field))
        for field in ("surface", "model", "reasoning", "speed")
    ):
        return False
    if not isinstance(values.get("final_pass_followed_earlier_failure"), bool):
        return False
    total_runs = values.get("total_runs")
    failed_runs = values.get("failed_runs")
    if not _counts(total_runs, failed_runs):
        return False
    latest = values.get("latest_run")
    if total_runs == 0:
        return latest is None and failed_runs == 0
    return isinstance(latest, dict) and _latest_run(latest)


def _counts(total_runs: object, failed_runs: object) -> bool:
    return (
        isinstance(total_runs, int)
        and isinstance(failed_runs, int)
        and total_runs >= 0
        and 0 <= failed_runs <= total_runs
    )


def _latest_run(value: dict[str, object]) -> bool:
    if value.get("status") not in _RUN_STATUSES:
        return False
    duration = value.get("total_duration_seconds")
    checks = value.get("checks")
    return (
        _duration(duration)
        and isinstance(checks, list)
        and all(_check(check) for check in checks)
    )


def _check(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        _nonempty(value.get("name"))
        and value.get("status") in _CHECK_STATUSES
        and _optional_duration(value.get("duration_seconds"))
    )


def _timestamp(value: object) -> bool:
    if not _nonempty(value):
        return False
    try:
        datetime.fromisoformat(str(value))
    except ValueError:
        return False
    return True


def _required_start(value: object) -> bool:
    return value == "unavailable" or _timestamp(value)


def _optional_timestamp(value: object) -> bool:
    return value is None or _timestamp(value)


def _duration(value: object) -> bool:
    return isinstance(value, float) and isfinite(value) and value >= 0


def _optional_duration(value: object) -> bool:
    return value is None or _duration(value)


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
