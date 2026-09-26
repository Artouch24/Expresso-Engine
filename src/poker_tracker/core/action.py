from dataclasses import dataclass

from .enums import ActionType, Street


@dataclass(frozen=True, slots=True)
class Action:
    player: str
    street: Street
    action_type: ActionType
    amount: int = 0
    sequence: int = 0

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("action amount cannot be negative")
        if self.sequence < 0:
            raise ValueError("sequence cannot be negative")
