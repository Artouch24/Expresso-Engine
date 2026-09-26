from collections import defaultdict


class ParseError(ValueError):
    pass


def blocks(text: str, start: str, end: str) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line == start:
            if current is not None:
                raise ParseError(f"Nested {start}")
            current = []
        elif line == end:
            if current is None:
                raise ParseError(f"Unexpected {end}")
            result.append(current)
            current = None
        elif current is not None and line and not line.startswith("#"):
            current.append(line)
    if current is not None:
        raise ParseError(f"Missing {end}")
    return result


def fields(lines: list[str]) -> tuple[dict[str, str], dict[str, list[str]]]:
    values: dict[str, str] = {}
    repeated: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        if ":" not in line:
            raise ParseError(f"Expected Key: value, got {line!r}")
        key, value = (part.strip() for part in line.split(":", 1))
        repeated[key].append(value)
        values[key] = value
    return values, repeated
