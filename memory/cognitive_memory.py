"""
DeDe - Cognitive Memory

Stores the cognitive evolution of a user over time.

This is the first step toward a persistent Daimon capable of
remembering cognitive history rather than isolated conversations.
"""

from datetime import datetime
from typing import Any


class CognitiveMemory:
    """
    Stores the history of cognitive analyses.
    """

    def __init__(self):
        self.history = []

    def add_analysis(
        self,
        text: str,
        detector_results: dict[str, Any],
        interpretation: dict[str, Any],
    ) -> None:

        self.history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "text": text,
                "vector": detector_results.get("cognitive_vector", {}),
                "metrics": detector_results.get("metrics", {}),
                "formulas": detector_results.get("formulas", {}),
                "interpretation": interpretation,
            }
        )

    def last_analysis(self) -> dict[str, Any] | None:

        if not self.history:
            return None

        return self.history[-1]

    def count(self) -> int:

        return len(self.history)

    def export(self) -> list[dict[str, Any]]:

        return self.history
