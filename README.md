# Poker Tracker

Local Winamax Expresso tracker focused on:

- cEV/game
- ROI
- Heads-Up vs 3-handed performance
- effective BB depth
- preflop/postflop frequencies
- automated leak detection

## Status

This repository is a tested V1 foundation. Recursive scanning, a deliberately limited synthetic-fixture parser, identifier-based idempotent imports, local SQLite persistence, tournament result statistics, and CLI diagnostics operate today. **V1 does not calculate cEV**: pot reconstruction, equity, side pots, and adjusted cEV will not be exposed until they have rigorous mathematical tests.

No full compatibility claim is made for real Winamax histories. Real anonymized samples are required to validate and extend grammar safely.

## Install

Python 3.11 or later is required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

## CLI

```bash
python -m poker_tracker init
python -m poker_tracker import /read-only/path/to/hand_histories
python -m poker_tracker stats
python -m poker_tracker doctor
```

The default database is `data/poker_tracker.sqlite3`; override it with `--database PATH` before the subcommand. Import scans `.txt` and `.log` recursively and never writes to source files. `stats` reports tournament totals, profit/ROI, finishes, hand phase counts, and maximum monetary drawdown.

## Architecture

The `src/poker_tracker` package separates a minimal generic `core`, read-only `winamax` ingestion, specialized `formats/expresso` rules, `storage`, `services`, and `cli`. This permits later `formats/cash` or `formats/space_ko` modules without putting their rules in core, but neither is implemented. See [architecture](docs/architecture.md).

## Data safety

Real histories contain sensitive data. Never commit, publish, modify, move, or delete them. History directories, archives, databases, and environment files are ignored. Checked-in fixtures are visibly synthetic and use invented identities. Review `git status` before every commit.

## Current limitations

The parser only recognizes the transparent `[TOURNAMENT]` / `[HAND]` synthetic grammar in `tests/fixtures`; it has not been validated against real Winamax exports. It does not yet parse boards/showdowns from room text, calculate positional frequencies, group stored hands by BB bucket, reconstruct side pots, calculate equity/cEV, detect leaks, or provide a dashboard. Missing data is not inferred.

## Roadmap

1. Validate real grammar using anonymized samples and broaden parser tests.
2. Add opportunity-based preflop/postflop and effective-depth reports.
3. Build tested pot/side-pot/equity reconstruction and adjusted cEV/game.
4. Add statistically responsible leak detection, then a local dashboard.

Details and the proposed cEV validation rules are in [the roadmap](docs/roadmap.md).
