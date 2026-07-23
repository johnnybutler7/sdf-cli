"""Small scalar helpers for the deliberately limited verification parser."""

from __future__ import annotations


def parse_scalar(value: str, *, preserve_hash: bool = False) -> str:
    """Return an unquoted scalar, accepting ordinary trailing comments."""
    raw = value.strip()
    if not preserve_hash:
        raw = _without_inline_comment(raw)
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    return raw


def _without_inline_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if quote is not None:
            if character == quote and not escaped:
                quote = None
            escaped = character == "\\" and not escaped
            continue
        if character in ("'", '"'):
            quote = character
        elif character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value
