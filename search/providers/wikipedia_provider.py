"""
DeDe - Wikipedia Search Provider
"""

from typing import Any
import wikipediaapi

from search.search_provider import SearchProvider


class WikipediaProvider(SearchProvider):
    name = "wikipedia"

    def search(
        self,
        query: str,
        max_results: int = 3,
    ) -> dict[str, Any]:

        wiki = wikipediaapi.Wikipedia(
            user_agent="DeDe-Cognitive-Daimon/0.1",
            language="fr",
        )

        page = wiki.page(query)

        if not page.exists():
            return {
                "provider": self.name,
                "status": "empty",
                "query": query,
                "results": [],
                "summary": "Wikipedia found no direct page.",
            }

        summary = page.summary[:900]

        return {
            "provider": self.name,
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": page.title,
                    "url": page.fullurl,
                    "snippet": summary,
                }
            ],
            "summary": "Wikipedia returned 1 result.",
        }
