"""Small YAML text operations for the owned evidence machine record."""

from __future__ import annotations

from sdf_cli.evidence_front_matter_text import indented_yaml, unquote


def fenced_record(data: bytes, heading: str) -> tuple[str, bytes, int, int]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("evidence.md is not UTF-8") from error
    lines = text.splitlines(keepends=True)
    headings = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == heading
    ]
    if not headings:
        raise ValueError("evidence.md machine-record heading is missing")
    if len(headings) != 1:
        raise ValueError("evidence.md has multiple machine-record sections")
    start = headings[0] + 1
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start == len(lines) or lines[start].rstrip("\r\n") != "```yaml":
        raise ValueError("machine-record YAML fence is missing")
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].rstrip("\r\n") == "```"
        ),
        None,
    )
    if end is None:
        raise ValueError("machine-record YAML fence is unclosed")
    metadata = "".join(lines[start + 1 : end])
    validate_yaml_shape(metadata)
    yaml_start = len("".join(lines[: start + 1]).encode("utf-8"))
    yaml_end = yaml_start + len(metadata.encode("utf-8"))
    return metadata, data[:yaml_start] + data[yaml_end:], yaml_start, yaml_end


def validate_yaml_shape(metadata: str) -> None:
    for line in metadata.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if (
            "\t" in line[:indent]
            or indent % 2
            or (":" not in line and not line.lstrip().startswith("- "))
        ):
            raise ValueError("machine-record YAML is malformed")


def scalar_at(metadata: str, parent: str, key: str) -> str | None:
    lines = metadata.splitlines()
    try:
        start = lines.index(f"{parent}:")
    except ValueError:
        return None
    for line in lines[start + 1 :]:
        if line and not line.startswith("  "):
            break
        if line.startswith(f"  {key}:"):
            return unquote(line.partition(":")[2].strip())
    return None


def nested_block(metadata: str, header: str, *, child_indent: str) -> str | None:
    lines = metadata.splitlines()
    try:
        start = lines.index(header)
    except ValueError:
        return None
    end = start + 1
    while end < len(lines) and (not lines[end] or lines[end].startswith(child_indent)):
        end += 1
    return (
        "\n".join(
            line[len(child_indent) :] if line else "" for line in lines[start + 1 : end]
        )
        + "\n"
    )


def replace_nested_block(metadata: str, header: str, value_yaml: str) -> str:
    lines = metadata.splitlines()
    try:
        start = lines.index(header)
    except ValueError as error:
        raise ValueError(f"{header.strip()[:-1]} is missing") from error
    end = start + 1
    while end < len(lines) and (not lines[end] or lines[end].startswith("    ")):
        end += 1
    return (
        "\n".join([*lines[:start], header, *indented_yaml(value_yaml), *lines[end:]])
        + "\n"
    )
