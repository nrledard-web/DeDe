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
    INSTRUCTION_PATTERNS = [
        # French
        r"\btrouve(?:-|\s)?moi\b",
        r"\bcherche(?:-|\s)?moi\b",
        r"\brecherche(?:-|\s)?moi\b",
        r"\bdonne(?:-|\s)?moi\b",
        r"\bmontre(?:-|\s)?moi\b",
        r"\bpeux[- ]tu\b",
        r"\bpourrais[- ]tu\b",
        r"\bje veux\b",
        r"\bj['’]?aimerais\b",
        r"\bfais(?:-|\s)?moi\b",
        r"\ben me faisant\b",
        r"\bavec un résumé\b",
        r"\bavec une synthèse\b",
        r"\bet fais un résumé\b",
        r"\bet résume\b",
        r"\brésume(?:-|\s)?moi\b",
        r"\bdes? liens?\b",
        r"\bdes? sites?\b",
        r"\bdes? sources?\b",

        # English
        r"\bfind me\b",
        r"\bsearch for\b",
        r"\blook for\b",
        r"\bgive me\b",
        r"\bshow me\b",
        r"\bcan you\b",
        r"\bcould you\b",
        r"\bi want\b",
        r"\bi would like\b",
        r"\bwith a summary\b",
        r"\band summarize\b",
        r"\bsummarize it\b",
        r"\bsome links?\b",
        r"\bsome websites?\b",
        r"\bsome sources?\b",

        # Spanish
        r"\bbúscame\b",
        r"\bbusca(?:me)?\b",
        r"\bencuéntrame\b",
        r"\bdame\b",
        r"\bmuéstrame\b",
        r"\bpuedes\b",
        r"\bpodrías\b",
        r"\bquiero\b",
        r"\bme gustaría\b",
        r"\bcon un resumen\b",
        r"\by haz un resumen\b",
        r"\benlaces?\b",
        r"\bsitios?\b",
        r"\bfuentes?\b",

        # Filipino / Tagalog
        r"\bhanapan mo ako\b",
        r"\bmaghanap ka\b",
        r"\bigawa mo ako\b",
        r"\bipakita mo\b",
        r"\bmaaari mo bang\b",
        r"\bmay buod\b",
        r"\bat ibuod\b",
        r"\bmga link\b",
        r"\bmga source\b",
    ]

    # Structural terms that generally do not belong in a query.
    STOP_WORDS = {
        # French
        "a",
        "à",
        "au",
        "aux",
        "avec",
        "ce",
        "ces",
        "cette",
        "de",
        "des",
        "du",
        "en",
        "et",
        "faisant",
        "la",
        "le",
        "les",
        "lien",
        "liens",
        "me",
        "moi",
        "mon",
        "ma",
        "mes",
        "pour",
        "résumé",
        "resume",
        "sur",
        "synthèse",
        "synthese",
        "un",
        "une",

        # English
        "a",
        "an",
        "and",
        "about",
        "for",
        "link",
        "links",
        "me",
        "of",
        "on",
        "some",
        "summary",
        "the",
        "with",

        # Spanish
        "acerca",
        "con",
        "de",
        "del",
        "en",
        "enlace",
        "enlaces",
        "haz",
        "los",
        "las",
        "me",
        "resumen",
        "sobre",
        "un",
        "una",
        "y",

        # Filipino
        "ako",
        "ang",
        "at",
        "buod",
        "link",
        "mga",
        "mo",
        "ng",
        "sa",
        "tungkol",
    }

    SEARCH_VERBS = {
        # French
        "cherche",
        "chercher",
        "trouve",
        "trouver",
        "recherche",
        "rechercher",
        "donne",
        "montre",

        # English
        "find",
        "search",
        "look",
        "give",
        "show",

        # Spanish
        "busca",
        "buscar",
        "encuentra",
        "encontrar",

        # Filipino
        "hanap",
        "maghanap",
    }

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

        natural_query = self._extract_natural_query(original_text)
        concept_query = self._build_from_concepts(concept_data)

        query = natural_query
        source = "natural_language"

        # Concepts are a fallback, not the primary source.
        if not self._is_usable(query) and self._is_usable(concept_query):
            query = concept_query
            source = "concepts"

        # If the natural extraction is too short, enrich it with
        # useful concepts without replacing its subject.
        elif self._should_enrich(query) and concept_query:
            query = self._merge_queries(
                query,
                concept_query,
            )
            source = "natural_language_and_concepts"

        # Final safety fallback: preserve the full user request rather
        # than returning an empty or meaningless fragment.
        if not self._is_usable(query):
            query = original_text
            source = "original_text_fallback"

        query = self._clean_query(query)

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
        Remove conversational instructions and retain the topic.
        """

        query = text.lower()

        query = query.replace("’", "'")
        query = query.replace("-", " ")

        # Remove URLs because URL reading is handled elsewhere.
        query = re.sub(
            r"https?://\S+|www\.\S+",
            " ",
            query,
            flags=re.IGNORECASE,
        )

        for pattern in self.INSTRUCTION_PATTERNS:
            query = re.sub(
                pattern,
                " ",
                query,
                flags=re.IGNORECASE,
            )

        # Remove punctuation after phrase extraction.
        query = re.sub(
            r"[^\wÀ-ÿ'-]+",
            " ",
            query,
            flags=re.UNICODE,
        )

        tokens = []

        for token in query.split():
            normalized = self._normalize_token(token)

            if not normalized:
                continue

            if normalized in self.STOP_WORDS:
                continue

            if normalized in self.SEARCH_VERBS:
                continue

            if len(normalized) < 2:
                continue

            tokens.append(token.strip("'"))

        return self._deduplicate_tokens(tokens)

    def _build_from_concepts(
        self,
        concept_data: dict[str, Any],
    ) -> str:
        """
        Extract useful semantic concepts as a fallback or enrichment.
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
            concept = self._concept_to_text(item)

            if not concept:
                continue

            normalized = self._normalize_token(concept)

            if normalized in self.STOP_WORDS:
                continue

            if normalized in self.SEARCH_VERBS:
                continue

            if len(normalized) < 2:
                continue

            selected.append(concept)

        return self._deduplicate_tokens(selected[:8])

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
        if not query:
            return False

        meaningful_tokens = [
            token
            for token in query.split()
            if self._normalize_token(token) not in self.STOP_WORDS
        ]

        return bool(meaningful_tokens)

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
