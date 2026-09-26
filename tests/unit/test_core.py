from datetime import datetime
from decimal import Decimal

import pytest

from poker_tracker.core import Action, ActionType, Card, Hand, Player, Position, Street


def test_card_normalizes_and_validates():
    assert str(Card.parse("as")) == "As"
    with pytest.raises(ValueError):
        Card.parse("1x")


def test_action_rejects_negative_chips():
    with pytest.raises(ValueError):
        Action("P", Street.FLOP, ActionType.BET, -1)


def test_positions_are_stable_values():
    assert {position.value for position in Position} == {"BTN", "SB", "BB"}


def test_effective_depth_uses_shortest_stack_and_big_blind():
    hand = Hand(
        "H",
        None,
        datetime(2026, 1, 1),
        10,
        20,
        [Player("A", 500, Position.BUTTON), Player("B", 210, Position.BIG_BLIND)],
    )
    assert hand.effective_stack == 210
    assert hand.effective_stack_bb == Decimal("10.5")
