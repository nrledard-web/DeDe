"""
DeDe - Search Provider Interface
"""

from typing import Any


class SearchProvider:
    name = "base_provider"

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        raise NotImplementedError
