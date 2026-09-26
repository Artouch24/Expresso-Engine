"""Conservative parser for the documented synthetic V1 fixture subset."""

from datetime import datetime
from pathlib import Path

from poker_tracker.core import Action, ActionType, Hand, Player, Position, Street

from .parsing import ParseError, blocks, fields


class WinamaxHandParser:
    """Parse only validated hand fields; unknown real exports fail explicitly."""

    def parse(self, text: str) -> list[Hand]:
        hands: list[Hand] = []
        for block in blocks(text, "[HAND]", "[/HAND]"):
            values, repeated = fields(block)
            try:
                players = [self._player(value) for value in repeated.get("Player", [])]
                actions = [
                    self._action(value, i) for i, value in enumerate(repeated.get("Action", []))
                ]
                small, big = (int(value) for value in values["Blinds"].split("/"))
                hands.append(
                    Hand(
                        values["HandId"],
                        values.get("TournamentId"),
                        datetime.fromisoformat(values["Date"]),
                        small,
                        big,
                        players,
                        actions,
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ParseError(f"Invalid synthetic hand: {exc}") from exc
        return hands

    @staticmethod
    def _player(value: str) -> Player:
        name, stack, position = value.split("|")
        return Player(name, int(stack), Position(position))

    @staticmethod
    def _action(value: str, sequence: int) -> Action:
        player, street, action_type, amount = value.split("|")
        return Action(player, Street(street), ActionType(action_type), int(amount), sequence)

    def parse_file(self, path: Path) -> list[Hand]:
        return self.parse(path.read_text(encoding="utf-8"))
