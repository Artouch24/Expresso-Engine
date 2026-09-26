import argparse
import logging
import os
import sqlite3
import sys
from decimal import Decimal
from pathlib import Path

from poker_tracker.services import AnalysisService, ImportService
from poker_tracker.storage import DEFAULT_DATABASE, Database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="poker_tracker", description="Local Winamax Expresso tracker"
    )
    parser.add_argument(
        "--database", type=Path, default=DEFAULT_DATABASE, help="SQLite database path"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="initialize the SQLite database")
    importer = sub.add_parser("import", help="import a Winamax history directory (read-only)")
    importer.add_argument("path", type=Path)
    sub.add_parser("stats", help="show available aggregate statistics")
    sub.add_parser("doctor", help="check runtime, data directory, and database")
    return parser


def _money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d} EUR"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    database = Database(args.database)
    if args.command == "init":
        database.initialize()
        print(f"Initialized database: {database.path}")
        return 0
    if args.command == "import":
        try:
            report = ImportService(database).import_path(args.path)
        except (FileNotFoundError, NotADirectoryError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        for label, value in (
            ("Files scanned", report.files_scanned),
            ("Hands parsed", report.hands_parsed),
            ("Hands inserted", report.hands_inserted),
            ("Duplicates ignored", report.duplicates_ignored),
            ("Tournaments parsed", report.tournaments_parsed),
            ("Errors", report.errors),
        ):
            print(f"{label + ':':<22}{value}")
        return 1 if report.errors else 0
    if args.command == "doctor":
        return doctor(database)
    if not database.schema_is_current:
        print("Database is not initialized; run 'poker_tracker init'.", file=sys.stderr)
        return 2
    stats, hands = AnalysisService(database).global_stats()
    print(f"Tournaments: {stats.tournaments}")
    print(f"Total buy-ins: {_money(stats.total_buy_ins_cents)}")
    print(f"Total won: {_money(stats.total_prizes_cents)}")
    print(f"Net profit: {_money(stats.profit_cents)}")
    roi = stats.roi_percent.quantize(Decimal("0.01")) if stats.roi_percent is not None else "n/a"
    print(f"ROI: {roi}%")
    for position in (1, 2, 3):
        count = stats.finish_counts[position]
        percentage = stats.finish_percentages[position]
        print(f"Finish {position}: {count} ({percentage:.2f}%)")
    average_buy_in = (
        f"{stats.average_buy_in_cents / Decimal(100):.2f} EUR"
        if stats.average_buy_in_cents is not None
        else "n/a"
    )
    print(f"Average buy-in: {average_buy_in}")
    print(f"Average multiplier: {stats.average_multiplier or 'n/a'}")
    print(f"Multiplier distribution: {stats.multiplier_distribution}")
    print(f"Cumulative bankroll (cents): {list(stats.bankroll_cumulative_cents)}")
    print(f"Hands: {hands['hands']}")
    print(f"3-handed: {hands['three_handed']}; heads-up: {hands['heads_up']}")
    print(f"Heads-up reach: {hands['heads_up_reach_percent']:.2f}%")
    print(f"Effective-depth buckets: {hands['depth_buckets']}")
    print(f"Maximum drawdown: {_money(stats.max_drawdown_cents)}")
    return 0


def doctor(database: Database) -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python >= 3.11", sys.version_info >= (3, 11), sys.version.split()[0]))
    data_dir = database.path.parent
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        writable = os.access(data_dir, os.W_OK)
    except OSError:
        writable = False
    checks.append(("Data directory writable", writable, str(data_dir)))
    checks.append(("Database exists", database.path.exists(), str(database.path)))
    checks.append(("Schema current", database.schema_is_current, str(database.schema_version())))
    recent_errors = 0
    if database.schema_is_current:
        try:
            with database.connect() as connection:
                recent_errors = connection.execute(
                    "SELECT COUNT(*) FROM import_files WHERE error IS NOT NULL"
                ).fetchone()[0]
        except sqlite3.Error:
            recent_errors = -1
    checks.append(("No recorded import errors", recent_errors == 0, str(recent_errors)))
    for name, passed, detail in checks:
        print(f"[{'OK' if passed else 'FAIL'}] {name}: {detail}")
    return 0 if all(item[1] for item in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
