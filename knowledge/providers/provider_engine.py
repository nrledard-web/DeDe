"""
DeDe - Knowledge Provider Engine

Coordinates all knowledge providers.

Each provider returns a standardized knowledge result.
The ProviderEngine selects or combines the best available knowledge.
"""

from typing import Any

from knowledge.providers.local_provider import LocalProvider


class ProviderEngine:
    """
    Coordinates all knowledge providers.
    """

    def __init__(self):

        self.providers = [
            LocalProvider(),
        ]

    def search(self, query: str) -> dict[str, Any]:

        results = []

        for provider in self.providers:
            results.append(provider.search(query))

        best_result = max(
            results,
            key=lambda r: r.get("confidence", 0.0),
        )

        return {
            "results": results,
            "best_result": best_result,
            "provider_count": len(self.providers),
        }
