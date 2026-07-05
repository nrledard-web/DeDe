"""
DeDe - Search Engine

Modular search engine selector.

Current role:
- prepare multiple search providers
- allow user choice
- keep search optional
"""

from typing import Any


class SearchEngine:
    name = "search_engine"

    def __init__(self) -> None:
        self.available_providers = [
            "none",
            "duckduckgo",
            "brave",
            "serpapi",
        ]

    def search(
        self,
        query: str,
        provider: str = "none",
        max_results: int = 5,
    ) -> dict[str, Any]:

        provider = provider or "none"

        if provider not in self.available_providers:
            provider = "none"

        if provider == "none":
            return self._empty_result(
                query=query,
                provider=provider,
                reason="Search disabled.",
            )

        if provider == "duckduckgo":
            return self._placeholder_result(
                query=query,
                provider=provider,
            )

        if provider == "brave":
            return self._placeholder_result(
                query=query,
                provider=provider,
            )

        if provider == "serpapi":
            return self._placeholder_result(
                query=query,
                provider=provider,
            )

        return self._empty_result(
            query=query,
            provider="none",
            reason="No valid provider selected.",
        )

    def _empty_result(
        self,
        query: str,
        provider: str,
        reason: str,
    ) -> dict[str, Any]:

        return {
            "engine": self.name,
            "status": "disabled",
            "provider": provider,
            "query": query,
            "results": [],
            "summary": reason,
        }

    def _placeholder_result(
        self,
        query: str,
        provider: str,
    ) -> dict[str, Any]:

        return {
            "engine": self.name,
            "status": "placeholder",
            "provider": provider,
            "query": query,
            "results": [],
            "summary": (
                f"Search provider '{provider}' is selected but not "
                "connected yet."
            ),
        }
