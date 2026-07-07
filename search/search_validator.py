"""
DeDe - Search Validator

Evaluates whether search results are relevant to DeDe's search query
using concepts rather than language-specific markers.
"""

from typing import Any


class SearchValidator:
    name = "search_validator"

    def validate(
        self,
        query: str,
        search_result: dict[str, Any],
        concepts: list[str] | None = None,
    ) -> dict[str, Any]:

        results = search_result.get("results", [])
        concepts = concepts or []

        if not results:
            return {
                "validator": self.name,
                "status": "empty",
                "query": query,
                "concepts": concepts,
                "relevance": 0.0,
                "is_relevant": False,
                "summary": "No search results to validate.",
            }

        anchors = self._anchors(
            query=query,
            concepts=concepts,
        )

        if not anchors:
            return {
                "validator": self.name,
                "status": "no_anchors",
                "query": query,
                "concepts": concepts,
                "relevance": 0.0,
                "is_relevant": False,
                "summary": "No conceptual anchors available.",
            }

        scored_results = []

        for item in results:
            text = " ".join(
                [
                    item.get("title", ""),
                    item.get("snippet", ""),
                    item.get("url", ""),
                ]
            ).lower()

            matched = [
                anchor
                for anchor in anchors
                if anchor.lower() in text
            ]

            score = len(matched) / len(anchors)

            scored_results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "score": round(score, 3),
                    "matched_concepts": matched,
                }
            )

        best_score = max(
            item["score"]
            for item in scored_results
        )

        average_score = sum(
            item["score"]
            for item in scored_results
        ) / len(scored_results)

        relevance = max(best_score, average_score)

        return {
            "validator": self.name,
            "status": "ready",
            "query": query,
            "concepts": concepts,
            "anchors": anchors,
            "relevance": round(relevance, 3),
            "is_relevant": relevance >= 0.35,
            "best_score": round(best_score, 3),
            "average_score": round(average_score, 3),
            "scored_results": scored_results,
            "summary": (
                f"Search relevance estimated at "
                f"{round(relevance * 100)}%."
            ),
        }

    def _anchors(
        self,
        query: str,
        concepts: list[str],
    ) -> list[str]:

        anchors = []

        for concept in concepts:
            concept = str(concept).strip()

            if concept and len(concept) > 2:
                anchors.append(concept)

        if anchors:
            return anchors[:5]

        fallback = str(query).strip()

        if fallback:
            return [fallback]

        return []
