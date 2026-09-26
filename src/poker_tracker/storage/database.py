import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .schema import SCHEMA_SQL, SCHEMA_VERSION

DEFAULT_DATABASE = Path("data/poker_tracker.sqlite3")


class Database:
    def __init__(self, path: Path = DEFAULT_DATABASE) -> None:
        self.path = Path(path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA_SQL)

    def schema_version(self) -> int | None:
        if not self.path.exists():
            return None
        with self.connect() as connection:
            try:
                row = connection.execute("SELECT version FROM schema_version").fetchone()
            except sqlite3.OperationalError:
                return None
        return int(row[0]) if row else None

    @property
    def schema_is_current(self) -> bool:
        return self.schema_version() == SCHEMA_VERSION
