from dataclasses import dataclass, field


@dataclass(slots=True)
class Pot:
    contributions: dict[str, int] = field(default_factory=dict)

    def contribute(self, player: str, chips: int) -> None:
        if chips < 0:
            raise ValueError("contribution cannot be negative")
        self.contributions[player] = self.contributions.get(player, 0) + chips

    @property
    def total(self) -> int:
        return sum(self.contributions.values())
