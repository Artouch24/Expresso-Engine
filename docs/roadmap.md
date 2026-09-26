# Roadmap

## Next: validate Winamax ingestion
Obtain several **anonymized** real exports covering locale/date variants, split tournaments, all actions, showdowns, cancellations, and summaries. Turn each observed grammar into redacted fixtures and explicit parser tests before extending the conservative parser.

## Statistics
Add position/action opportunity denominators, tournament-level heads-up reach, and hand grouping by the centralized effective-BB buckets. Preflop modules will distinguish HU BTN first-in, BB versus limp/raise/shove, 3-handed BTN and SB branches, open shoves, calls, 3-bets, and 3-bet shoves. Postflop work will classify streets, pot-relative sizing, all-ins, player count, stack-off depth, and tested hand-strength categories.

## Correct all-in adjusted cEV
No cEV is calculated in V1. The future engine must reconstruct every contribution in action order, return uncalled chips, create main/side pots by eligibility, identify each all-in decision point, and compute exact showdown equities from known cards/ranges. For each eligible pot it will compare actual chip outcome with equity-weighted expectation, preserve chip conservation, and aggregate separately for 3-handed, heads-up, and per game. Golden tests must cover ties, multiway pots, unequal all-ins, folded contributions, rake assumptions, and incomplete information before results are exposed.

## Leaks and UI
Only after reliable opportunity-based statistics and cEV exist, compare sufficiently large samples to configurable baselines, report confidence/sample size, estimate cEV loss where supported, and prioritize actionable leaks. A local dashboard follows; no live HUD, game automation, solver, scraping, or real-time advice is planned.
