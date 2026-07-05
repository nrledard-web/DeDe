"""
DeDe - Search Engine

Search orchestrator.
Supports single-provider and multi-provider search.
"""

from typing import Any

from search.providers.duckduckgo_provider import DuckDuckGoProvider
from search.providers.brave_provider import BraveProvider


class SearchEngine:
    name = "search_engine"

    def __init__(self) -> None:
        self.providers = {
            "duckduckgo": DuckDuckGoProvider(),
            "brave": BraveProvider(),
        }

    def search(
        self,
        query: str,
        provider: str | list[str] = "none",
        max_results: int = 5,
    ) -> dict[str, Any]:

        if isinstance(provider, str):
            providers = [provider]
        else:
            providers = provider

        providers = [
            item for item in providers
            if item and item != "none"
        ]

        if not providers:
            return {
                "engine": self.name,
                "status": "disabled",
                "provider": "none",
                "providers": [],
                "query": query,
                "results": [],
                "provider_results": [],
                "summary": "Search disabled.",
            }

        provider_results = []
        all_results = []

        for provider_name in providers:
            selected = self.providers.get(provider_name)

            if not selected:
                provider_results.append(
                    {
                        "provider": provider_name,
                        "status": "placeholder",
                        "query": query,
                        "results": [],
                        "summary": (
                            f"Search provider '{provider_name}' is selected "
                            "but not connected yet."
                        ),
                    }
                )
                continue

            try:
                result = selected.search(
                    query=query,
                    max_results=max_results,
                )
            except Exception as error:
                result = {
                    "provider": provider_name,
                    "status": "error",
                    "query": query,
                    "results": [],
                    "summary": f"{provider_name} search failed.",
                    "error": str(error),
                }

            provider_results.append(result)

            for item in result.get("results", []):
                item["provider"] = provider_name
                all_results.append(item)

        return {
            "engine": self.name,
            "status": "success" if all_results else "empty",
            "provider": "+".join(providers),
            "providers": providers,
            "query": query,
            "results": all_results,
            "provider_results": provider_results,
            "summary": (
                f"Search completed with {len(providers)} provider(s), "
                f"{len(all_results)} total result(s)."
            ),
        }
