from decimal import Decimal
from enum import StrEnum


class ExpressoPhase(StrEnum):
    THREE_HANDED = "three_handed"
    HEADS_UP = "heads_up"


DEPTH_BUCKETS: tuple[tuple[Decimal | None, str], ...] = (
    (Decimal("6"), "<= 6 BB"),
    (Decimal("10"), "> 6 to 10 BB"),
    (Decimal("15"), "> 10 to 15 BB"),
    (Decimal("20"), "> 15 to 20 BB"),
    (Decimal("30"), "> 20 to 30 BB"),
    (None, "> 30 BB"),
)


def depth_bucket(big_blinds: Decimal | int | str) -> str:
    value = Decimal(big_blinds)
    if value < 0:
        raise ValueError("depth cannot be negative")
    return next(label for ceiling, label in DEPTH_BUCKETS if ceiling is None or value <= ceiling)
