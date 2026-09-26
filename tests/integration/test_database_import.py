from pathlib import Path

from poker_tracker.services import ImportService
from poker_tracker.storage import Database

FIXTURE = Path(__file__).parents[1] / "fixtures/winamax"


def test_insert_and_idempotent_import(tmp_path):
    database = Database(tmp_path / "tracker.sqlite3")
    service = ImportService(database)
    first = service.import_path(FIXTURE)
    second = service.import_path(FIXTURE)
    assert (
        first.files_scanned,
        first.hands_parsed,
        first.hands_inserted,
        first.tournaments_inserted,
        first.errors,
    ) == (1, 2, 2, 1, 0)
    assert (second.hands_inserted, second.duplicates_ignored, second.tournaments_inserted) == (
        0,
        2,
        0,
    )
    with database.connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM hands").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM tournaments").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM tournament_hands").fetchone()[0] == 2
