"""
DeDe - User Cognitive Model

Represents the long-term cognitive profile of one user.
"""

from typing import Any


class UserCognitiveModel:
    """
    Tracks the user's average cognitive vector over time.
    """

    def __init__(self):
        self.analysis_count = 0

        self.average_vector = {
            "gnosis": 0.0,
            "nous": 0.0,
            "doxa": 0.0,
            "reduction": 0.0,
            "revisability": 0.0,
        }

    def update(self, vector: dict[str, Any]) -> None:
        """
        Update the user's average cognitive vector.
        """

        self.analysis_count += 1
        count = self.analysis_count

        for key in self.average_vector:
            previous_average = self.average_vector[key]
            new_value = float(vector.get(key, 0.0))

            self.average_vector[key] = (
                previous_average * (count - 1) + new_value
            ) / count

    def profile(self) -> dict[str, Any]:
        """
        Return the current user cognitive profile.
        """

        return {
            "analysis_count": self.analysis_count,
            "average_vector": self.average_vector,
        }
