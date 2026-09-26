from collections import Counter
from dataclasses import dataclass
from decimal import Decimal

from .tournament import ExpressoTournament


@dataclass(frozen=True, slots=True)
class ResultStats:
    tournaments: int
    total_buy_ins_cents: int
    total_prizes_cents: int
    profit_cents: int
    roi_percent: Decimal | None
    finish_counts: dict[int, int]
    finish_percentages: dict[int, Decimal]
    average_buy_in_cents: Decimal | None
    average_multiplier: Decimal | None
    multiplier_distribution: dict[str, int]
    bankroll_cumulative_cents: tuple[int, ...]
    max_drawdown_cents: int


def calculate_results(items: list[ExpressoTournament]) -> ResultStats:
    ordered = sorted(items, key=lambda item: item.played_at)
    buyins = sum(item.buy_in_cents for item in ordered)
    prizes = sum(item.prize_cents for item in ordered)
    profit = prizes - buyins
    count = len(ordered)
    finishes = Counter(item.finishing_position for item in ordered)
    multipliers = [item.multiplier for item in ordered if item.multiplier is not None]
    distribution = Counter(str(value) for value in multipliers)
    bankroll: list[int] = []
    running = peak = drawdown = 0
    for item in ordered:
        running += item.profit_cents
        bankroll.append(running)
        peak = max(peak, running)
        drawdown = max(drawdown, peak - running)
    return ResultStats(
        count,
        buyins,
        prizes,
        profit,
        Decimal(profit * 100) / Decimal(buyins) if buyins else None,
        {position: finishes[position] for position in (1, 2, 3)},
        {
            position: Decimal(finishes[position] * 100) / Decimal(count) if count else Decimal(0)
            for position in (1, 2, 3)
        },
        Decimal(buyins) / Decimal(count) if count else None,
        sum(multipliers, Decimal(0)) / Decimal(len(multipliers)) if multipliers else None,
        dict(sorted(distribution.items())),
        tuple(bankroll),
        drawdown,
    )
