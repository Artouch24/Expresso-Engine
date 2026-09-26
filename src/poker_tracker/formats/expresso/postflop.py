"""Reserved interface for future postflop analytics.

No estimates are produced until algorithms and mathematical fixtures are validated.
"""

from typing import Protocol


class Analyzer(Protocol):
    """Contract for a future validated postflop analyzer."""

    def analyze(self, tournament_id: str) -> object: ...
