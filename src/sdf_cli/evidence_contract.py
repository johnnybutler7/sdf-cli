"""Evidence machine-record parsing and rendering."""

from __future__ import annotations

from dataclasses import dataclass

from sdf_cli.evidence_contract_validation import valid_machine_values
from sdf_cli.evidence_machine_record_parse import (
    contract_version_from,
    parse_machine_record,
)
from sdf_cli.evidence_machine_record_yaml import fenced_record

MACHINE_RECORD_HEADING = "## Machine Record"
EVIDENCE_ARCHIVE_CONTRACT = 5
SUPPORTED_CONTRACTS = {4, 5}
DECLARED_FIELDS = ("surface", "model", "reasoning", "speed")


class EvidenceMachineRecordError(ValueError):
    """A machine record is unsupported or cannot be safely read."""


@dataclass(frozen=True)
class EvidenceMachineRecord:
    contract_version: int
    change_id: str
    written_by: str
    repository: dict[str, str]
    branch: dict[str, str]
    declared: dict[str, str]
    started_at: str | None
    closed_at: str | None
    closeout_status: str
    total_runs: int
    failed_runs: int
    final_pass_followed_earlier_failure: bool
    latest_run: dict[str, object] | None
    body: bytes
    yaml_start: int
    yaml_end: int


def read_machine_record(data: bytes, *, change_id: str) -> EvidenceMachineRecord:
    try:
        metadata, body, yaml_start, yaml_end = fenced_record(
            data, MACHINE_RECORD_HEADING
        )
    except ValueError as error:
        if str(error) == "evidence.md machine-record heading is missing":
            raise EvidenceMachineRecordError(_unsupported_message()) from error
        raise EvidenceMachineRecordError(
            f"invalid machine record: {error}"
        ) from error
    contract_version = contract_version_from(metadata)
    if contract_version is None:
        raise EvidenceMachineRecordError(_unsupported_message())
    if contract_version not in SUPPORTED_CONTRACTS:
        raise EvidenceMachineRecordError(_unsupported_message())
    values = parse_machine_record(metadata, contract_version=contract_version)
    if (
        values is None
        or values["change_id"] != change_id
        or not valid_machine_values(values)
    ):
        raise EvidenceMachineRecordError(
            _invalid_record_message(
                contract_version, "required values are missing or invalid"
            )
        )
    record = EvidenceMachineRecord(
        contract_version=contract_version,
        change_id=change_id,
        written_by=str(values["written_by"]),
        repository=values["repository"],  # type: ignore[arg-type]
        branch=values["branch"],  # type: ignore[arg-type]
        declared=values["declared"],  # type: ignore[arg-type]
        started_at=values["started_at"],  # type: ignore[arg-type]
        closed_at=values["closed_at"],  # type: ignore[arg-type]
        closeout_status=str(values["closeout_status"]),
        total_runs=values["total_runs"],  # type: ignore[arg-type]
        failed_runs=values["failed_runs"],  # type: ignore[arg-type]
        final_pass_followed_earlier_failure=values[
            "final_pass_followed_earlier_failure"
        ],  # type: ignore[arg-type]
        latest_run=values["latest_run"],  # type: ignore[arg-type]
        body=body,
        yaml_start=yaml_start,
        yaml_end=yaml_end,
    )
    if metadata != render_machine_record(record):
        raise EvidenceMachineRecordError(
            _invalid_record_message(
                contract_version,
                "contains unsupported fields or non-canonical content",
            )
        )
    return record


def render_machine_record(record: EvidenceMachineRecord) -> str:
    lines = [
        f"contract: {record.contract_version}",
        f"written_by: {_yaml_scalar(record.written_by)}",
        f"change_id: {_yaml_scalar(record.change_id)}",
    ]
    if record.contract_version >= 5:
        lines.extend(
            [
                "repository:",
                f"  name: {_yaml_scalar(record.repository.get('name', 'unavailable'))}",
                f"  path: {_yaml_scalar(record.repository.get('path', 'unavailable'))}",
                "  github: "
                f"{_yaml_scalar(record.repository.get('github', 'unavailable'))}",
                "branch:",
                f"  name: {_yaml_scalar(record.branch.get('name', 'unavailable'))}",
                f"  head: {_yaml_scalar(record.branch.get('head', 'unavailable'))}",
            ]
        )
    lines.extend(_shared_record_lines(record))
    if record.latest_run is None:
        lines.append("  latest_run: null")
        return "\n".join(lines) + "\n"
    latest = record.latest_run
    total_duration = float(latest["total_duration_seconds"])
    lines.extend(
        [
            "  latest_run:",
            f"    status: {_yaml_scalar(str(latest['status']))}",
            f"    total_duration_seconds: {total_duration:.2f}",
            "    checks:" if latest["checks"] else "    checks: []",
        ]
    )
    for check in latest["checks"]:  # type: ignore[index]
        duration = check["duration_seconds"]
        lines.extend(
            [
                f"      - name: {_yaml_scalar(str(check['name']))}",
                f"        status: {_yaml_scalar(str(check['status']))}",
                "        duration_seconds: "
                + ("null" if duration is None else f"{float(duration):.2f}"),
            ]
        )
    return "\n".join(lines) + "\n"


def _shared_record_lines(record: EvidenceMachineRecord) -> list[str]:
    return [
        "run_context:",
        *(
            f"  {field}: {_yaml_scalar(record.declared.get(field, 'unknown'))}"
            for field in DECLARED_FIELDS
        ),
        f"started_at: {_yaml_or_null(record.started_at)}",
        f"closed_at: {_yaml_or_null(record.closed_at)}",
        f"closeout_status: {_yaml_scalar(record.closeout_status)}",
        "verification:",
        f"  total_runs: {record.total_runs}",
        f"  failed_runs: {record.failed_runs}",
        "  final_pass_followed_earlier_failure: "
        f"{str(record.final_pass_followed_earlier_failure).lower()}",
    ]


def _yaml_scalar(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _yaml_or_null(value: str | None) -> str:
    return "null" if value is None else _yaml_scalar(value)


def _unsupported_message() -> str:
    return (
        "historical or unsupported evidence machine record "
        "(contract 4 or 5 required)"
    )


def _invalid_record_message(contract_version: int, reason: str) -> str:
    if contract_version == 4:
        return _unsupported_message()
    return f"invalid contract 5 machine record: {reason}"
