from poker_tracker.core import Hand
from poker_tracker.formats.expresso import ExpressoTournament

from .database import Database


class TrackerRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_tournament(self, item: ExpressoTournament) -> bool:
        with self.database.connect() as db:
            cursor = db.execute(
                """INSERT OR IGNORE INTO tournaments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.tournament_id,
                    item.buy_in_cents,
                    item.rake_cents,
                    item.prize_pool_cents,
                    str(item.multiplier) if item.multiplier is not None else None,
                    item.finishing_position,
                    item.prize_cents,
                    item.played_at.isoformat(),
                    item.starting_stack,
                ),
            )
            return cursor.rowcount == 1

    def add_hand(self, hand: Hand) -> bool:
        with self.database.connect() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO hands VALUES (?, ?, ?, ?, ?)",
                (
                    hand.hand_id,
                    hand.tournament_id,
                    hand.played_at.isoformat(),
                    hand.small_blind,
                    hand.big_blind,
                ),
            )
            if cursor.rowcount != 1:
                return False
            db.executemany(
                "INSERT INTO players VALUES (?, ?, ?, ?)",
                [(hand.hand_id, p.name, p.starting_stack, p.position.value) for p in hand.players],
            )
            db.executemany(
                "INSERT INTO actions VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        hand.hand_id,
                        a.sequence,
                        a.player,
                        a.street.value,
                        a.action_type.value,
                        a.amount,
                    )
                    for a in hand.actions
                ],
            )
            if hand.tournament_id:
                db.execute(
                    "INSERT OR IGNORE INTO tournament_hands VALUES (?, ?)",
                    (hand.tournament_id, hand.hand_id),
                )
            return True
