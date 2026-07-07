"""
DeDe - Search Summarizer

Builds a compact source summary from validated search results.
"""

from typing import Any


class SearchSummarizer:
    name = "search_summarizer"

    def summarize(
        self,
        search_result: dict[str, Any],
        search_validation: dict[str, Any] | None = None,
        max_results: int = 5,
    ) -> dict[str, Any]:

        search_validation = search_validation or {}
        results = search_result.get("results", [])

        if not results:
            return {
                "summarizer": self.name,
                "status": "empty",
                "sources": [],
                "summary_text": "",
                "summary": "No search results to summarize.",
            }

        sources = []

        for item in results[:max_results]:
            title = item.get("title", "").strip()
            url = item.get("url", "").strip()
            snippet = item.get("snippet", "").strip()

            if not title and not url:
                continue

            sources.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                }
            )

        lines = ["Validated web sources:"]

        for index, source in enumerate(sources, start=1):
            lines.append("")
            lines.append(f"{index}. {source['title']}")
            if source["url"]:
                lines.append(f"URL: {source['url']}")
            if source["snippet"]:
                lines.append(f"Snippet: {source['snippet']}")

        return {
            "summarizer": self.name,
            "status": "ready",
            "relevance": search_validation.get("relevance", 0.0),
            "is_relevant": search_validation.get("is_relevant", False),
            "sources": sources,
            "summary_text": "\n".join(lines),
            "summary": f"{len(sources)} source(s) summarized.",
        }
