from typing import Any

from duckduckgo_search import DDGS

from search.search_provider import SearchProvider


class DuckDuckGoProvider(SearchProvider):
    name = "duckduckgo"

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:

        results = []

        print("DDG QUERY =", repr(query))

        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                    }
                )

        return {
            "provider": self.name,
            "status": "success",
            "query": query,
            "results": results,
            "summary": f"DuckDuckGo returned {len(results)} result(s).",
        }
