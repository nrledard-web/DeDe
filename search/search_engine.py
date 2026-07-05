"""
DeDe - Search Engine

Modular search engine selector.
"""

from typing import Any

from duckduckgo_search import DDGS


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
            return self._duckduckgo_search(
                query=query,
                max_results=max_results,
            )

        return self._placeholder_result(
            query=query,
            provider=provider,
        )

    def _duckduckgo_search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:

        try:
            results = []

            with DDGS() as ddgs:
                for item in ddgs.text(
                    query,
                    max_results=max_results,
                ):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("href", ""),
                            "snippet": item.get("body", ""),
                        }
                    )

            return {
                "engine": self.name,
                "status": "success",
                "provider": "duckduckgo",
                "query": query,
                "results": results,
                "summary": (
                    f"DuckDuckGo returned {len(results)} result(s)."
                ),
            }

        except Exception as error:
            return {
                "engine": self.name,
                "status": "error",
                "provider": "duckduckgo",
                "query": query,
                "results": [],
                "summary": "DuckDuckGo search failed.",
                "error": str(error),
            }

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
