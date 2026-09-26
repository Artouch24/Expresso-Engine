from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class ExpressoTournament:
    tournament_id: str
    buy_in_cents: int
    finishing_position: int
    prize_cents: int
    played_at: datetime
    starting_stack: int
    multiplier: Decimal | None = None
    rake_cents: int | None = None
    prize_pool_cents: int | None = None
    hand_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.tournament_id:
            raise ValueError("tournament_id is required")
        if self.finishing_position not in (1, 2, 3):
            raise ValueError("finishing_position must be 1, 2, or 3")
        for value in (self.buy_in_cents, self.prize_cents, self.starting_stack):
            if value < 0:
                raise ValueError("money and chips cannot be negative")

    @property
    def profit_cents(self) -> int:
        return self.prize_cents - self.buy_in_cents
