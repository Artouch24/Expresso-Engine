"""Reserved interface for future preflop analytics.

No estimates are produced until algorithms and mathematical fixtures are validated.
"""

from typing import Protocol


class Analyzer(Protocol):
    """Contract for a future validated preflop analyzer."""

    def analyze(self, tournament_id: str) -> object: ...
