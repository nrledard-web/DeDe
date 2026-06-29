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
    Executes all registered knowledge providers.
    """

    def __init__(self):

        self.providers = [

            LocalProvider(),

        ]

    def search(
        self,
        query: str,
    ) -> dict[str, Any]:

        results = []

        for provider in self.providers:

            results.append(
                provider.search(query)
            )

        found = [

            r

            for r in results

            if r.get("found")

        ]

        if found:

            best = max(
                found,
                key=lambda x: x["confidence"],
            )

        else:

            best = max(
                results,
                key=lambda x: x["confidence"],
            )

        return {

            "best_result": best,

            "results": results,

            "provider_count":
                len(self.providers),

        }
