"""Playing-card value objects."""

from dataclasses import dataclass

RANKS = "23456789TJQKA"
SUITS = "cdhs"


@dataclass(frozen=True, slots=True)
class Card:
    rank: str
    suit: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "rank", self.rank.upper())
        object.__setattr__(self, "suit", self.suit.lower())
        if self.rank not in RANKS or self.suit not in SUITS:
            raise ValueError(f"Invalid card: {self.rank}{self.suit}")

    @classmethod
    def parse(cls, value: str) -> "Card":
        if len(value) != 2:
            raise ValueError(f"Invalid card: {value}")
        return cls(value[0], value[1])

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"
