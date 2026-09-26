"""Reserved interface for future cev analytics.

No estimates are produced until algorithms and mathematical fixtures are validated.
"""

from typing import Protocol


class Analyzer(Protocol):
    """Contract for a future validated cev analyzer."""

    def analyze(self, tournament_id: str) -> object: ...
