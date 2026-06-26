"""
DeDe - Cognitive Comparator

Compares the current cognitive vector with the user's historical profile.
"""

from typing import Any


class CognitiveComparator:
    """
    Compare the current cognitive state to the user's average profile.
    """

    def compare(
        self,
        current_vector: dict[str, Any],
        user_profile: dict[str, Any],
    ) -> dict[str, Any]:

        average = user_profile["average_vector"]

        comparison = {}

        for key in current_vector:

            delta = current_vector[key] - average.get(key, 0.0)

            if delta > 0.05:
                trend = "higher"

            elif delta < -0.05:
                trend = "lower"

            else:
                trend = "stable"

            comparison[key] = {
                "current": current_vector[key],
                "average": average[key],
                "delta": delta,
                "trend": trend,
            }

        return comparison
