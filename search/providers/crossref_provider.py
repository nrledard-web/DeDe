"""
DeDe - CrossRef Search Provider
"""

from typing import Any
import requests

from search.search_provider import SearchProvider


class CrossRefProvider(SearchProvider):
    name = "crossref"

    def search(
        self,
        query: str,
        max_results: int = 3,
    ) -> dict[str, Any]:

        url = "https://api.crossref.org/works"

        params = {
            "query": query,
            "rows": max_results,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("message", {}).get("items", []):
            title = " ".join(item.get("title", []))
            doi = item.get("DOI", "")
            link = f"https://doi.org/{doi}" if doi else item.get("URL", "")

            abstract = item.get("abstract", "")
            publisher = item.get("publisher", "")

            snippet = abstract or publisher or "No abstract available."

            results.append(
                {
                    "title": title,
                    "url": link,
                    "snippet": snippet[:900],
                }
            )

        return {
            "provider": self.name,
            "status": "success" if results else "empty",
            "query": query,
            "results": results,
            "summary": f"CrossRef returned {len(results)} result(s).",
        }
