import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poker_tracker.storage import Database, TrackerRepository
from poker_tracker.winamax import WinamaxHandParser, WinamaxSummaryParser, scan_history_files
from poker_tracker.winamax.parsing import ParseError

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ImportReport:
    files_scanned: int = 0
    hands_parsed: int = 0
    hands_inserted: int = 0
    duplicates_ignored: int = 0
    tournaments_parsed: int = 0
    tournaments_inserted: int = 0
    errors: int = 0


class ImportService:
    """Orchestrate a read-only source scan and idempotent database writes."""

    def __init__(self, database: Database) -> None:
        self.database = database
        self.repository = TrackerRepository(database)
        self.hand_parser = WinamaxHandParser()
        self.summary_parser = WinamaxSummaryParser()

    def import_path(self, path: Path) -> ImportReport:
        self.database.initialize()
        files = scan_history_files(path)
        report = ImportReport(files_scanned=len(files))
        parsed: list[tuple[Path, str, list, list]] = []
        for source in files:
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            try:
                text = source.read_text(encoding="utf-8")
                hands = self.hand_parser.parse(text)
                tournaments = self.summary_parser.parse(text)
                parsed.append((source, digest, hands, tournaments))
                report.hands_parsed += len(hands)
                report.tournaments_parsed += len(tournaments)
            except (OSError, UnicodeError, ParseError) as exc:
                report.errors += 1
                LOGGER.warning("Could not import %s: %s", source, exc)
                self._record(source, digest, str(exc))
        for _, _, _, tournaments in parsed:
            for tournament in tournaments:
                report.tournaments_inserted += self.repository.add_tournament(tournament)
        for source, digest, hands, _ in parsed:
            for hand in hands:
                inserted = self.repository.add_hand(hand)
                report.hands_inserted += inserted
                report.duplicates_ignored += not inserted
            self._record(source, digest, None)
        return report

    def _record(self, path: Path, digest: str, error: str | None) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO import_files VALUES (?, ?, ?, ?)",
                (str(path), digest, datetime.now(UTC).isoformat(), error),
            )
