from datetime import datetime
from decimal import Decimal

from poker_tracker.formats.expresso import (
    ExpressoTournament,
    ResultStats,
    calculate_results,
    depth_bucket,
)
from poker_tracker.storage import Database


class AnalysisService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def global_stats(self) -> tuple[ResultStats, dict[str, object]]:
        with self.database.connect() as db:
            rows = db.execute(
                "SELECT * FROM tournaments ORDER BY played_at, tournament_id"
            ).fetchall()
            hand_rows = db.execute("""SELECT COUNT(*) total,
              SUM(CASE WHEN player_count = 3 THEN 1 ELSE 0 END) three_handed,
              SUM(CASE WHEN player_count = 2 THEN 1 ELSE 0 END) heads_up
              FROM (SELECT h.hand_id, COUNT(p.name) player_count FROM hands h
                    LEFT JOIN players p ON p.hand_id=h.hand_id GROUP BY h.hand_id)""").fetchone()
            depths = db.execute("""SELECT h.hand_id, h.big_blind, MIN(p.starting_stack) depth
                FROM hands h JOIN players p ON p.hand_id=h.hand_id
                GROUP BY h.hand_id, h.big_blind""").fetchall()
            hu_tournaments = db.execute("""SELECT COUNT(DISTINCT tournament_id) FROM (
                SELECT h.tournament_id FROM hands h JOIN players p ON p.hand_id=h.hand_id
                WHERE h.tournament_id IS NOT NULL GROUP BY h.hand_id
                HAVING COUNT(p.name) = 2)""").fetchone()[0]
        tournaments = [
            ExpressoTournament(
                tournament_id=row["tournament_id"],
                buy_in_cents=row["buy_in_cents"],
                rake_cents=row["rake_cents"],
                prize_pool_cents=row["prize_pool_cents"],
                multiplier=Decimal(row["multiplier"]) if row["multiplier"] else None,
                finishing_position=row["finishing_position"],
                prize_cents=row["prize_cents"],
                played_at=datetime.fromisoformat(row["played_at"]),
                starting_stack=row["starting_stack"],
            )
            for row in rows
        ]
        bucket_counts: dict[str, int] = {}
        for row in depths:
            bucket = depth_bucket(Decimal(row["depth"]) / Decimal(row["big_blind"]))
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        hands: dict[str, object] = {
            "hands": int(hand_rows["total"] or 0),
            "three_handed": int(hand_rows["three_handed"] or 0),
            "heads_up": int(hand_rows["heads_up"] or 0),
            "depth_buckets": bucket_counts,
        }
        hands["heads_up_reach_percent"] = (
            (Decimal(hu_tournaments * 100) / Decimal(len(tournaments)))
            if tournaments
            else Decimal(0)
        )
        return calculate_results(tournaments), hands
