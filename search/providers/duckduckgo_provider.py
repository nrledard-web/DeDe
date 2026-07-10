"""
DeDe - DuckDuckGo Provider

Current DuckDuckGo-compatible search provider using the ddgs package.
"""

from __future__ import annotations

from typing import Any

from ddgs import DDGS

from search.search_provider import SearchProvider


class DuckDuckGoProvider(SearchProvider):

    name = "duckduckgo"

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:

        cleaned_query = str(query or "").strip()

        if not cleaned_query:
            return {
                "provider": self.name,
                "status": "empty_query",
                "query": "",
                "results": [],
                "summary": "DuckDuckGo search skipped because the query is empty.",
            }

        print("=" * 80)
        print("DUCKDUCKGO PROVIDER")
        print("QUERY :", repr(cleaned_query))
        print("MAX RESULTS :", max_results)
        print("=" * 80)

        results = []

        try:
            raw_results = DDGS(
                timeout=10,
            ).text(
                query=cleaned_query,
                max_results=max_results,
            )

            for item in raw_results or []:
                if not isinstance(item, dict):
                    continue

                title = str(
                    item.get("title", "")
                    or ""
                ).strip()

                url = str(
                    item.get("href", "")
                    or item.get("url", "")
                    or ""
                ).strip()

                snippet = str(
                    item.get("body", "")
                    or item.get("snippet", "")
                    or ""
                ).strip()

                if not title and not url:
                    continue

                results.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    }
                )

                if len(results) >= max_results:
                    break

        except Exception as error:
            print("=" * 80)
            print("DUCKDUCKGO ERROR")
            print(type(error).__name__)
            print(str(error))
            print("=" * 80)

            return {
                "provider": self.name,
                "status": "error",
                "query": cleaned_query,
                "results": [],
                "summary": "DuckDuckGo search failed.",
                "error_type": type(error).__name__,
                "error": str(error),
            }

        status = (
            "success"
            if results
            else "no_results"
        )

        return {
            "provider": self.name,
            "status": status,
            "query": cleaned_query,
            "results": results,
            "summary": (
                f"DuckDuckGo returned {len(results)} result(s)."
            ),
        }
