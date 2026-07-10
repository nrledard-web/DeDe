"""
DeDe - Search Engine

Search orchestrator.
Supports single-provider and multi-provider search.
"""

from typing import Any

from search.providers.duckduckgo_provider import DuckDuckGoProvider
from search.providers.brave_provider import BraveProvider
from search.providers.arxiv_provider import ArxivProvider
from search.providers.crossref_provider import CrossRefProvider


class SearchEngine:

    name = "search_engine"

    def __init__(self) -> None:
        self.providers = {
            "duckduckgo": DuckDuckGoProvider(),
            "brave": BraveProvider(),
            "arxiv": ArxivProvider(),
            "crossref": CrossRefProvider(),
        }

    def search(
        self,
        query: str,
        provider: str | list[str] = "none",
        max_results: int = 5,
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Normalize provider selection
        # --------------------------------------------------

        if isinstance(provider, str):
            providers = [provider]
        else:
            providers = provider or []

        profile_map = {
            "general": ["duckduckgo"],
            "shopping": ["duckduckgo"],
            "news": ["duckduckgo"],
            "programming": ["duckduckgo"],
            "legal": ["duckduckgo"],
            "scientific": [
                "duckduckgo",
                "arxiv",
                "crossref",
            ],
        }

        expanded_providers = []

        for item in providers:
            if item in profile_map:
                expanded_providers.extend(
                    profile_map[item]
                )
            else:
                expanded_providers.append(item)

        providers = [
            item
            for item in expanded_providers
            if item and item != "none"
        ]

        # Remove duplicates while preserving order.
        providers = list(dict.fromkeys(providers))

        # --------------------------------------------------
        # Search disabled
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Run selected providers
        # --------------------------------------------------

        for provider_name in providers:
            selected = self.providers.get(
                provider_name
            )

            if not selected:
                provider_results.append(
                    {
                        "provider": provider_name,
                        "status": "placeholder",
                        "query": query,
                        "results": [],
                        "summary": (
                            f"Search provider '{provider_name}' "
                            "is selected but not connected yet."
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
                    "summary": (
                        f"{provider_name} search failed."
                    ),
                    "error_type": type(error).__name__,
                    "error": str(error),
                }

            provider_results.append(result)

            for item in result.get(
                "results",
                [],
            ):
                normalized_item = dict(item)
                normalized_item["provider"] = (
                    provider_name
                )
                all_results.append(
                    normalized_item
                )

        # --------------------------------------------------
        # Final status
        # --------------------------------------------------

        provider_errors = [
            result
            for result in provider_results
            if result.get("status") == "error"
        ]

        if all_results:
            final_status = "success"

        elif provider_errors:
            final_status = "error"

        else:
            final_status = "no_results"

        # --------------------------------------------------
        # Final report
        # --------------------------------------------------

        return {
            "engine": self.name,
            "status": final_status,
            "provider": "+".join(providers),
            "providers": providers,
            "query": query,
            "results": all_results,
            "provider_results": provider_results,
            "summary": (
                f"Search completed with "
                f"{len(providers)} provider(s), "
                f"{len(all_results)} total result(s)."
            ),
        }
