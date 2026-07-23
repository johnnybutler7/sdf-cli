"""Parse compact evidence machine-record YAML."""

from __future__ import annotations

DECLARED_FIELDS = ("surface", "model", "reasoning", "speed")


def contract_version_from(metadata: str) -> int | None:
    raw_contract = scalar(metadata, "contract")
    if raw_contract is None or not raw_contract.isdigit():
        return None
    return int(raw_contract)


def parse_machine_record(
    metadata: str, *, contract_version: int
) -> dict[str, object] | None:
    lines = metadata.splitlines()
    try:
        declared = {
            field: scalar_in_block(lines, "run_context:", field, "  ")
            for field in DECLARED_FIELDS
        }
        followed_failure = scalar_in_block(
            lines, "verification:", "final_pass_followed_earlier_failure", "  "
        )
        latest = _latest_run(lines)
        if any(value is None for value in declared.values()) or latest is _INVALID:
            return None
        repository = (
            _block_scalars(lines, "repository:", ("name", "path", "github"))
            if contract_version >= 5
            else {
                "name": "unavailable",
                "path": "unavailable",
                "github": "unavailable",
            }
        )
        branch = (
            _block_scalars(lines, "branch:", ("name", "head"))
            if contract_version >= 5
            else {"name": "unavailable", "head": "unavailable"}
        )
        if repository is None or branch is None:
            return None
        return {
            "change_id": scalar(metadata, "change_id"),
            "written_by": scalar(metadata, "written_by"),
            "repository": repository,
            "branch": branch,
            "declared": {key: str(value) for key, value in declared.items()},
            "started_at": none_if_null(scalar(metadata, "started_at")),
            "closed_at": none_if_null(scalar(metadata, "closed_at")),
            "closeout_status": scalar(metadata, "closeout_status"),
            "total_runs": _integer_in_block(lines, "total_runs"),
            "failed_runs": _integer_in_block(lines, "failed_runs"),
            "final_pass_followed_earlier_failure": (
                True
                if followed_failure == "true"
                else False
                if followed_failure == "false"
                else None
            ),
            "latest_run": latest,
        }
    except (IndexError, TypeError, ValueError):
        return None


def scalar(metadata: str, key: str) -> str | None:
    for line in metadata.splitlines():
        if line.startswith(f"{key}:"):
            return unquote(line.partition(":")[2].strip())
    return None


def scalar_in_block(
    lines: list[str], header: str, key: str, indent: str
) -> str | None:
    try:
        start = lines.index(header) + 1
    except ValueError:
        return None
    for line in lines[start:]:
        if line and not line.startswith(indent):
            break
        if line.startswith(f"{indent}{key}:"):
            return unquote(line.partition(":")[2].strip())
    return None


def none_if_null(value: str | None) -> str | None:
    return None if value in (None, "null", "~", "") else value


def unquote(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def _integer_in_block(lines: list[str], key: str) -> int:
    value = scalar_in_block(lines, "verification:", key, "  ")
    return int(value or "")


def _block_scalars(
    lines: list[str], header: str, keys: tuple[str, ...]
) -> dict[str, str] | None:
    values = {key: scalar_in_block(lines, header, key, "  ") for key in keys}
    if any(value is None for value in values.values()):
        return None
    return {key: str(value) for key, value in values.items()}


def _latest_run(lines: list[str]) -> dict[str, object] | None | object:
    try:
        start = lines.index("  latest_run:")
    except ValueError:
        return None if "  latest_run: null" in lines else _INVALID
    values: dict[str, str] = {}
    checks: list[dict[str, object]] = []
    index = start + 1
    while index < len(lines):
        line = lines[index]
        if line and not line.startswith("    "):
            break
        if line.startswith("    ") and not line.startswith("      "):
            key, _, value = line.strip().partition(":")
            if key != "checks":
                values[key] = unquote(value.strip())
        if line.startswith("      - name:"):
            checks.append(_check_at(lines, index))
            index += 2
        index += 1
    if "status" not in values or "total_duration_seconds" not in values:
        return _INVALID
    return {
        "status": values["status"],
        "total_duration_seconds": float(values["total_duration_seconds"]),
        "checks": checks,
    }


def _check_at(lines: list[str], index: int) -> dict[str, object]:
    name = unquote(lines[index].partition(":")[2].strip())
    status = unquote(lines[index + 1].partition(":")[2].strip())
    raw_duration = lines[index + 2].partition(":")[2].strip()
    return {
        "name": name,
        "status": status,
        "duration_seconds": None if raw_duration == "null" else float(raw_duration),
    }


_INVALID = object()
