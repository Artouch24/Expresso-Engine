from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from .action import Action
from .cards import Card
from .player import Player


@dataclass(slots=True)
class Hand:
    hand_id: str
    tournament_id: str | None
    played_at: datetime
    small_blind: int
    big_blind: int
    players: list[Player]
    actions: list[Action] = field(default_factory=list)
    board: list[Card] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.hand_id:
            raise ValueError("hand_id is required")
        if self.small_blind <= 0 or self.big_blind <= 0:
            raise ValueError("blinds must be positive")

    @property
    def effective_stack(self) -> int:
        """Return the smallest starting stack participating in the hand."""
        if not self.players:
            raise ValueError("effective stack requires at least one player")
        return min(player.starting_stack for player in self.players)

    @property
    def effective_stack_bb(self) -> Decimal:
        return Decimal(self.effective_stack) / Decimal(self.big_blind)
