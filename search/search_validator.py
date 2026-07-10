"""
DeDe - Search Validator

Evaluates whether search results are relevant to DeDe's search query.

The validator uses normalized conceptual anchors rather than requiring
the complete user query to appear inside a result.
"""

from __future__ import annotations

import re
import unicodedata
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
                "anchors": [],
                "relevance": 0.0,
                "is_relevant": False,
                "best_score": 0.0,
                "average_score": 0.0,
                "scored_results": [],
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
                "anchors": [],
                "relevance": 0.0,
                "is_relevant": False,
                "best_score": 0.0,
                "average_score": 0.0,
                "scored_results": [],
                "summary": "No conceptual anchors available.",
            }

        scored_results = []

        for item in results:
            searchable_text = " ".join(
                [
                    item.get("title", ""),
                    item.get("snippet", ""),
                    item.get("url", ""),
                ]
            )

            normalized_text = self._normalize(searchable_text)

            matched = [
                anchor
                for anchor in anchors
                if self._normalize(anchor) in normalized_text
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

        # A strong individual result is sufficient.
        # The average remains useful when several results agree.
        relevance = max(
            best_score,
            average_score,
        )

        is_relevant = (
            best_score >= 0.34
            or average_score >= 0.20
        )

        return {
            "validator": self.name,
            "status": "ready",
            "query": query,
            "concepts": concepts,
            "anchors": anchors,
            "relevance": round(relevance, 3),
            "is_relevant": is_relevant,
            "best_score": round(best_score, 3),
            "average_score": round(average_score, 3),
            "scored_results": scored_results,
            "summary": (
                f"Search relevance estimated at "
                f"{round(relevance * 100)}%."
            ),
        }

    # --------------------------------------------------
    # Build Search Anchors
    # --------------------------------------------------

    def _anchors(
        self,
        query: str,
        concepts: list[str],
    ) -> list[str]:

        anchors = []

        for concept in concepts:
            concept = str(concept).strip()

            if self._is_usable_anchor(concept):
                anchors.append(concept)

        if not anchors:
            anchors = self._extract_query_terms(query)

        return self._deduplicate(
            anchors
        )[:5]

    # --------------------------------------------------
    # Extract Fallback Query Terms
    # --------------------------------------------------

    def _extract_query_terms(
        self,
        query: str,
    ) -> list[str]:

        normalized_query = self._normalize(query)

        words = re.findall(
            r"[a-z0-9][a-z0-9_-]*",
            normalized_query,
        )

        generic_search_terms = {
            # French
            "lien",
            "liens",
            "recherche",
            "rechercher",
            "resume",
            "trouve",
            "trouver",

            # English
            "find",
            "link",
            "links",
            "search",
            "summary",

            # Spanish
            "buscar",
            "busca",
            "enlace",
            "enlaces",
            "resumen",

            # Filipino / Tagalog
            "hanap",
            "hanapin",
            "link",
            "links",
            "buod",
            "tungkol",
            "magbigay",
            "bigyan",
        }

        candidates = [
            word
            for word in words
            if len(word) > 3
            and word not in generic_search_terms
        ]

        if not candidates:
            return []

        # Prefer the longest words because they are more likely
        # to represent meaningful concepts across languages.
        candidates = sorted(
            candidates,
            key=len,
            reverse=True,
        )

        return candidates[:5]

    # --------------------------------------------------
    # Anchor Validation
    # --------------------------------------------------

    def _is_usable_anchor(
        self,
        anchor: str,
    ) -> bool:

        cleaned = anchor.strip()

        if not cleaned:
            return False

        if len(cleaned) <= 2:
            return False

        if cleaned.lower().startswith("claim:"):
            return False

        return True

    # --------------------------------------------------
    # Text Normalization
    # --------------------------------------------------

    def _normalize(
        self,
        text: str,
    ) -> str:

        lowered = str(text).lower().strip()

        decomposed = unicodedata.normalize(
            "NFKD",
            lowered,
        )

        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )

        return " ".join(
            without_accents.split()
        )

    # --------------------------------------------------
    # Anchor Deduplication
    # --------------------------------------------------

    def _deduplicate(
        self,
        items: list[str],
    ) -> list[str]:

        unique = []
        seen = set()

        for item in items:
            normalized = self._normalize(item)

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            unique.append(item)

        return unique
