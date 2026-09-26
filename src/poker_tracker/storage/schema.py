SCHEMA_VERSION = 1
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);
INSERT INTO schema_version(version) SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM schema_version);
CREATE TABLE IF NOT EXISTS tournaments (
 tournament_id TEXT PRIMARY KEY, buy_in_cents INTEGER NOT NULL, rake_cents INTEGER,
 prize_pool_cents INTEGER, multiplier TEXT, finishing_position INTEGER NOT NULL
 CHECK(finishing_position BETWEEN 1 AND 3),
 prize_cents INTEGER NOT NULL, played_at TEXT NOT NULL, starting_stack INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS hands (
 hand_id TEXT PRIMARY KEY, tournament_id TEXT, played_at TEXT NOT NULL,
 small_blind INTEGER NOT NULL, big_blind INTEGER NOT NULL,
 FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id)
);
CREATE TABLE IF NOT EXISTS players (
 hand_id TEXT NOT NULL, name TEXT NOT NULL, starting_stack INTEGER NOT NULL, position TEXT NOT NULL,
 PRIMARY KEY(hand_id, name), FOREIGN KEY(hand_id) REFERENCES hands(hand_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS actions (
 hand_id TEXT NOT NULL, sequence INTEGER NOT NULL, player TEXT NOT NULL, street TEXT NOT NULL,
 action_type TEXT NOT NULL, amount INTEGER NOT NULL, PRIMARY KEY(hand_id, sequence),
 FOREIGN KEY(hand_id) REFERENCES hands(hand_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS tournament_hands (
 tournament_id TEXT NOT NULL, hand_id TEXT NOT NULL UNIQUE,
 PRIMARY KEY(tournament_id, hand_id),
 FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id),
 FOREIGN KEY(hand_id) REFERENCES hands(hand_id)
);
CREATE TABLE IF NOT EXISTS import_files (
 path TEXT NOT NULL, content_sha256 TEXT NOT NULL, imported_at TEXT NOT NULL,
 error TEXT, PRIMARY KEY(path, content_sha256)
);
"""
