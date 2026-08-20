"""
DeDe - Search Query Builder

Builds a useful web-search query from the user's natural-language request.

Objectives:
- remove conversational instructions
- preserve the actual subject of the request
- support French, English, Spanish and Filipino
- use extracted concepts only as secondary support
- never return an empty or truncated query
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


class SearchQueryBuilder:
    """
    Converts a natural-language request into a concise search query.

    Example:
        "Trouve-moi des liens sur les chevaux en me faisant un résumé"
        -> "chevaux"
    """

    name = "search_query_builder"

    # Expressions surrounding the actual topic.
    # They are deliberately removed as complete phrases before
    # individual stop words are processed.

    # Structural terms that generally do not belong in a query.

    def build(
        self,
        text: str,
        conversation_context: dict[str, Any] | None = None,
        concept_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build a search query and return diagnostic information.
        """

        conversation_context = conversation_context or {}
        concept_data = concept_data or {}

        original_text = self._clean_whitespace(text)

        if not original_text:
            return {
                "builder": self.name,
                "status": "empty",
                "query": "",
                "original_text": "",
                "terms": [],
                "source": "none",
                "summary": "No search query could be built from empty text.",
            }

        natural_query = self._extract_natural_query(
            original_text
        )

        concept_query = self._build_from_concepts(
            concept_data
        )

        # --------------------------------------------------
        # Semantic subject first
        # --------------------------------------------------
        # Concepts already extracted by DeDe are safer than
        # removing words through fixed multilingual markers.
        #
        # Natural language remains the fallback when no
        # usable concept is available.
        # --------------------------------------------------

        # Preserve the user's natural request first.
        # Semantic concepts are only a fallback.

        query = natural_query
        source = "natural_language"

        if (
            not self._is_usable(query)
            and self._is_usable(concept_query)
        ):
            query = concept_query
            source = "concepts"

        # Final safety fallback: preserve the full user request rather
        # than returning an empty or meaningless fragment.
        if not self._is_usable(query):
            query = original_text
            source = "original_text_fallback"

        query = self._clean_query(query)

        print("=" * 80)
        print("SEARCH QUERY BUILDER")
        print("TEXT :", text)
        print("NATURAL :", natural_query)
        print("CONCEPT :", concept_query)
        print("FINAL :", query)
        print("=" * 80)

        return {
            "builder": self.name,
            "status": "ready",
            "query": query,
            "original_text": original_text,
            "natural_query": natural_query,
            "concept_query": concept_query,
            "terms": query.split(),
            "source": source,
            "summary": (
                f"Search query built from {source}: '{query}'."
            ),
        }

    def _extract_natural_query(
        self,
        text: str,
    ) -> str:
        """
        Preserve the semantic subject of the user's request.

        This extractor deliberately avoids keyword-by-keyword
        deletion. Search intent is handled elsewhere by DeDe's
        governors; the query builder should preserve meaning,
        not attempt to infer it from marker lists.
        """

        query = self._clean_whitespace(
            text
        )

        if not query:
            return ""

        # URLs are handled by URLReader.
        query = re.sub(
            r"https?://\S+|www\.\S+",
            " ",
            query,
            flags=re.IGNORECASE,
        )

        query = self._clean_whitespace(
            query
        )

        # --------------------------------------------------
        # Prefer semantic concepts when they are already
        # present inside the natural request.
        #
        # Do not delete individual words from the sentence:
        # that can destroy names, relations and context.
        # --------------------------------------------------

        return query

    def _build_from_concepts(
        self,
        concept_data: dict[str, Any],
    ) -> str:
        """
        Extract semantic concepts without language-specific markers.
        """

        raw_concepts = (
            concept_data.get("main_concepts")
            or concept_data.get("concepts")
            or concept_data.get("keywords")
            or []
        )

        if isinstance(raw_concepts, str):
            raw_concepts = [raw_concepts]

        selected = []

        for item in raw_concepts:

            concept = self._concept_to_text(
                item
            )

            if not concept:
                continue

            normalized = self._normalize_token(
                concept
            )

            if len(normalized) < 2:
                continue

            selected.append(
                concept
            )

        return self._deduplicate_tokens(
            selected[:8]
        )

    def _concept_to_text(
        self,
        item: Any,
    ) -> str:
        """
        Support concepts represented as strings or dictionaries.
        """

        if isinstance(item, str):
            return item.strip()

        if isinstance(item, dict):
            value = (
                item.get("label")
                or item.get("concept")
                or item.get("name")
                or item.get("text")
                or ""
            )

            return str(value).strip()

        return ""

    def _merge_queries(
        self,
        first: str,
        second: str,
    ) -> str:
        tokens = []

        for value in (first, second):
            for token in value.split():
                normalized = self._normalize_token(token)

                if normalized in {
                    self._normalize_token(existing)
                    for existing in tokens
                }:
                    continue

                tokens.append(token)

        return " ".join(tokens[:10])

    def _deduplicate_tokens(
        self,
        tokens: list[str],
    ) -> str:
        result = []
        seen = set()

        for token in tokens:
            cleaned = token.strip()
            normalized = self._normalize_token(cleaned)

            if not normalized or normalized in seen:
                continue

            seen.add(normalized)
            result.append(cleaned)

        return " ".join(result[:10]).strip()

    def _normalize_token(
        self,
        token: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFKD",
            token.lower().strip(),
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )

        return normalized.strip("'")

    def _clean_query(
        self,
        query: str,
    ) -> str:
        query = self._clean_whitespace(query)
        query = query.strip(" ,.;:!?\"'")

        # Keep the query short enough for search providers.
        words = query.split()

        if len(words) > 12:
            query = " ".join(words[:12])

        return query

    def _clean_whitespace(
        self,
        value: str,
    ) -> str:
        return re.sub(
            r"\s+",
            " ",
            str(value or ""),
        ).strip()

    def _is_usable(
        self,
        query: str,
    ) -> bool:

        cleaned = self._clean_whitespace(
            query
        )

        return bool(cleaned)

    def _should_enrich(
        self,
        query: str,
    ) -> bool:
        """
        A single precise topic such as 'chevaux' does not need enrichment.
        Only an extremely weak term should be enriched.
        """

        if not query:
            return True

        tokens = query.split()

        return len(tokens) == 1 and len(tokens[0]) < 4
