from dataclasses import dataclass

from .enums import Position


@dataclass(frozen=True, slots=True)
class Player:
    name: str
    starting_stack: int
    position: Position

    def __post_init__(self) -> None:
        if self.starting_stack < 0:
            raise ValueError("starting_stack cannot be negative")
