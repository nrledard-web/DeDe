from typing import Any
import urllib.parse
import urllib.request
import json
import os

from search.search_provider import SearchProvider


class BraveProvider(SearchProvider):
    name = "brave"

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:

        api_key = os.getenv("BRAVE_SEARCH_API_KEY")

        if not api_key:
            return {
                "provider": self.name,
                "status": "missing_api_key",
                "query": query,
                "results": [],
                "summary": "Brave Search API key is missing.",
            }

        url = (
            "https://api.search.brave.com/res/v1/web/search?"
            + urllib.parse.urlencode(
                {
                    "q": query,
                    "count": max_results,
                }
            )
        )

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = []

        for item in data.get("web", {}).get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                }
            )

        return {
            "provider": self.name,
            "status": "success",
            "query": query,
            "results": results,
            "summary": f"Brave returned {len(results)} result(s).",
        }
