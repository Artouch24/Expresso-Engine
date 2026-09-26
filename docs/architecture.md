# Architecture

Poker Tracker uses a small generic poker core plus one specialized Expresso module.

- **core**: immutable cards, players/actions, a reusable hand, positions, streets, and pot contributions.
- **winamax**: recursive read-only scanning, conservative parsers, and identifier-based deduplication.
- **formats/expresso**: tournament results, phases, centralized effective-depth buckets, and future analytical contracts.
- **storage**: versioned SQLite schema and repositories with unique `hand_id` and `tournament_id` keys.
- **services**: import transaction orchestration and aggregate analysis.
- **cli**: dependency-free commands and human-readable diagnostics.

Money is always integer cents; chips are integers. Decimal is used for ratios. Source histories are only read, never renamed or changed. The V1 parser intentionally supports the documented synthetic fixture grammar, rather than claiming unverified compatibility with every Winamax export variation.
