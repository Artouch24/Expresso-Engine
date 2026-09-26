from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def unique_by(items: Iterable[T], identity: Callable[[T], str]) -> list[T]:
    """Keep first occurrence of each stable domain identifier."""
    seen: set[str] = set()
    result: list[T] = []
    for item in items:
        key = identity(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
