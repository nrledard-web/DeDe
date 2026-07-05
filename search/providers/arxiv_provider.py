"""
DeDe - arXiv Search Provider
"""

from typing import Any
import arxiv

from search.search_provider import SearchProvider


class ArxivProvider(SearchProvider):
    name = "arxiv"

    def search(
        self,
        query: str,
        max_results: int = 3,
    ) -> dict[str, Any]:

        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []

        for paper in client.results(search):
            results.append(
                {
                    "title": paper.title,
                    "url": paper.entry_id,
                    "snippet": paper.summary[:900],
                }
            )

        return {
            "provider": self.name,
            "status": "success" if results else "empty",
            "query": query,
            "results": results,
            "summary": f"arXiv returned {len(results)} result(s).",
        }
