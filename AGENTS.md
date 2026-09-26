# Agent guide

## Objective and architecture
Build a privacy-first local tracker for Winamax NLHE 3-max Expresso. Keep the reusable poker value objects in `src/poker_tracker/core`, Winamax read-only ingestion in `winamax`, format rules in `formats/expresso`, SQLite in `storage`, orchestration in `services`, and presentation in `cli`. Do not add Cash or Space KO yet and do not generalize for unsupported rooms.

## Setup and commands
- Install: `python -m pip install -e '.[dev]'`
- Test: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .`
- CLI: `python -m poker_tracker --help`

## Conventions and dependencies
Require Python 3.11+, type public boundaries, document important public interfaces, prefer dataclasses and `pathlib`, and represent money in integer cents and chips as integers. Keep dependencies minimal; SQLite, argparse, and logging remain standard-library based. Add dependencies only with a concrete V1 requirement and tests. Keep `core` free of Expresso constants.

## Data safety
Never modify, delete, move, commit, or publish the user's real poker history files.
Real hand histories are read-only input data.
Only synthetic or fully anonymized fixtures are allowed. Databases, archives, environment files, and history directories must remain ignored. Never log private hand contents or player identity data unnecessarily.

Do not implement poker formulas from intuition when correctness can be tested.
For cEV, equity, side pots and payout calculations, add explicit mathematical tests
before relying on the implementation.

## Roadmap
First validate parsing against user-provided anonymized Winamax samples, then expand action coverage and diagnostics. Next add depth/position aggregates and verified pot reconstruction. Implement equity/all-in adjusted cEV only after mathematical fixtures, followed by leak rules and a local dashboard.
