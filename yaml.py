"""Minimal YAML compatibility layer for offline test environments.

Implements a tiny subset of YAML required by this repository's tests:
- key/value mappings
- nested blocks by indentation
- sequences with `-` items
- inline flow mappings/lists (`{...}` / `[...]`)
- booleans/null/numbers/quoted strings/bare strings
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable


class YAMLError(ValueError):
    """Raised when YAML parsing fails."""


@dataclass
class _Line:
    indent: int
    text: str


def safe_load(stream: Any) -> Any:
    """Parse a YAML document into Python data structures."""
    if hasattr(stream, "read"):
        content = stream.read()
    else:
        content = str(stream)
    return _parse_yaml(content)


def _parse_yaml(content: str) -> Any:
    lines = _tokenize(content)
    if not lines:
        return None
    value, idx = _parse_block(lines, 0, lines[0].indent)
    if idx != len(lines):
        raise YAMLError("Trailing content after YAML document")
    return value


def _tokenize(content: str) -> list[_Line]:
    out: list[_Line] = []
    for raw in content.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()
        out.append(_Line(indent=indent, text=text))
    return out


def _parse_block(lines: list[_Line], idx: int, indent: int) -> tuple[Any, int]:
    if idx >= len(lines):
        return {}, idx

    # Sequence block
    if lines[idx].text.startswith("-"):
        seq: list[Any] = []
        while idx < len(lines) and lines[idx].indent == indent and lines[idx].text.startswith("-"):
            item_text = lines[idx].text[1:].strip()
            idx += 1

            if not item_text:
                if idx >= len(lines) or lines[idx].indent <= indent:
                    seq.append(None)
                else:
                    nested, idx = _parse_block(lines, idx, lines[idx].indent)
                    seq.append(nested)
                continue

            # list item can start a mapping: - key: value
            if ":" in item_text and not item_text.startswith("{"):
                key, val = _split_key_value(item_text)
                item: dict[str, Any] = {}
                if val:
                    item[key] = _parse_scalar(val)
                else:
                    if idx < len(lines) and lines[idx].indent > indent:
                        nested, idx = _parse_block(lines, idx, lines[idx].indent)
                        item[key] = nested
                    else:
                        item[key] = None

                while idx < len(lines) and lines[idx].indent > indent:
                    if lines[idx].indent == indent + 2 and ":" in lines[idx].text and not lines[idx].text.startswith("-"):
                        sub_key, sub_val = _split_key_value(lines[idx].text)
                        idx += 1
                        if sub_val:
                            item[sub_key] = _parse_scalar(sub_val)
                        else:
                            if idx < len(lines) and lines[idx].indent > indent + 2:
                                nested, idx = _parse_block(lines, idx, lines[idx].indent)
                                item[sub_key] = nested
                            else:
                                item[sub_key] = None
                    else:
                        break
                seq.append(item)
                continue

            seq.append(_parse_scalar(item_text))

        return seq, idx

    # Mapping block
    mapping: dict[str, Any] = {}
    while idx < len(lines) and lines[idx].indent == indent and not lines[idx].text.startswith("-"):
        key, val = _split_key_value(lines[idx].text)
        idx += 1
        if val:
            mapping[key] = _parse_scalar(val)
        else:
            if idx < len(lines) and lines[idx].indent > indent:
                nested, idx = _parse_block(lines, idx, lines[idx].indent)
                mapping[key] = nested
            else:
                mapping[key] = None

    return mapping, idx


def _split_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise YAMLError(f"Invalid mapping line: {text}")
    key, val = text.split(":", 1)
    return key.strip(), val.strip()


def _parse_scalar(value: str) -> Any:
    if value.startswith("{") and value.endswith("}"):
        return _parse_flow_map(value[1:-1])
    if value.startswith("[") and value.endswith("]"):
        return _parse_flow_list(value[1:-1])

    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in {"null", "none", "~"}:
        return None

    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)

    return value


def _parse_flow_map(body: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for part in _split_flow_parts(body):
        if not part:
            continue
        key, val = _split_key_value(part)
        out[key] = _parse_scalar(val)
    return out


def _parse_flow_list(body: str) -> list[Any]:
    return [_parse_scalar(part) for part in _split_flow_parts(body)]


def _split_flow_parts(body: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None

    for ch in body:
        if quote is not None:
            current.append(ch)
            if ch == quote:
                quote = None
            continue

        if ch in {'"', "'"}:
            quote = ch
            current.append(ch)
            continue

        if ch in "[{":
            depth += 1
            current.append(ch)
            continue
        if ch in "]}":
            depth -= 1
            current.append(ch)
            continue

        if ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue

        current.append(ch)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def safe_dump(data: Any, *args: Any, **kwargs: Any) -> str:
    """Not implemented in compatibility parser."""
    raise YAMLError("safe_dump is not implemented in yaml compatibility module")
