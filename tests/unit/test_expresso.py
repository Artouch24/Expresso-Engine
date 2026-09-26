from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from poker_tracker.formats.expresso import ExpressoTournament, calculate_results, depth_bucket


def tournament(identifier, buyin, prize, finish, multiplier, day=0):
    return ExpressoTournament(
        identifier,
        buyin,
        finish,
        prize,
        datetime(2026, 1, 1) + timedelta(days=day),
        500,
        Decimal(multiplier),
    )


def test_profit_roi_finishes_multipliers_and_drawdown():
    stats = calculate_results(
        [
            tournament("1", 100, 300, 1, "3"),
            tournament("2", 100, 0, 3, "2", 1),
            tournament("3", 100, 0, 2, "2", 2),
        ]
    )
    assert stats.profit_cents == 0
    assert stats.roi_percent == Decimal("0")
    assert stats.finish_counts == {1: 1, 2: 1, 3: 1}
    assert stats.finish_percentages[1] == Decimal(100) / Decimal(3)
    assert stats.average_multiplier == Decimal(7) / Decimal(3)
    assert stats.multiplier_distribution == {"2": 2, "3": 1}
    assert stats.bankroll_cumulative_cents == (200, 100, 0)
    assert stats.max_drawdown_cents == 200


def test_position_validation():
    with pytest.raises(ValueError):
        tournament("x", 100, 0, 4, "2")


@pytest.mark.parametrize(
    ("depth", "expected"),
    [
        (6, "<= 6 BB"),
        (Decimal("6.1"), "> 6 to 10 BB"),
        (10, "> 6 to 10 BB"),
        (15, "> 10 to 15 BB"),
        (20, "> 15 to 20 BB"),
        (30, "> 20 to 30 BB"),
        (31, "> 30 BB"),
    ],
)
def test_depth_buckets(depth, expected):
    assert depth_bucket(depth) == expected
