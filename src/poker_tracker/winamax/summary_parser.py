from datetime import datetime
from decimal import Decimal
from pathlib import Path

from poker_tracker.formats.expresso import ExpressoTournament

from .parsing import ParseError, blocks, fields


class WinamaxSummaryParser:
    """Parse the explicit synthetic summary subset used to establish V1 plumbing."""

    def parse(self, text: str) -> list[ExpressoTournament]:
        tournaments: list[ExpressoTournament] = []
        for block in blocks(text, "[TOURNAMENT]", "[/TOURNAMENT]"):
            values, repeated = fields(block)
            try:
                tournaments.append(
                    ExpressoTournament(
                        tournament_id=values["TournamentId"],
                        buy_in_cents=int(values["BuyInCents"]),
                        rake_cents=int(values["RakeCents"]) if "RakeCents" in values else None,
                        prize_pool_cents=int(values["PrizePoolCents"])
                        if "PrizePoolCents" in values
                        else None,
                        multiplier=Decimal(values["Multiplier"])
                        if "Multiplier" in values
                        else None,
                        finishing_position=int(values["FinishingPosition"]),
                        prize_cents=int(values["PrizeCents"]),
                        played_at=datetime.fromisoformat(values["Date"]),
                        starting_stack=int(values["StartingStack"]),
                        hand_ids=repeated.get("HandId", []),
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ParseError(f"Invalid synthetic tournament: {exc}") from exc
        return tournaments

    def parse_file(self, path: Path) -> list[ExpressoTournament]:
        return self.parse(path.read_text(encoding="utf-8"))
