"""
DeDe - Memory Retriever

Retrieves relevant durable memory before reasoning.

Principles:
- structural and multilingual retrieval;
- no language-specific marker lists;
- identity and preferences remain available as core memory;
- other memories are selected by semantic-form similarity;
- legacy facts and notes remain supported.
"""

from __future__ import annotations

from typing import Any
import re


class MemoryRetriever:

    name = "memory_retriever"

    CORE_MEMORY_TYPES = {
        "identity",
        "preference",
    }

    def retrieve(
        self,
        text: str,
        persistent_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        persistent_memory = persistent_memory or {}

        memory_items = persistent_memory.get(
            "memory_items",
            [],
        )

        if not isinstance(
            memory_items,
            list,
        ):
            memory_items = []

        core_memories = self._select_core_memories(
            memory_items
        )

        relevant_memories = (
            self._select_relevant_memories(
                text=text,
                memory_items=memory_items,
                excluded_ids={
                    item.get("memory_id")
                    for item in core_memories
                },
            )
        )

        relevant_notes = self._select_legacy_items(
            text=text,
            items=persistent_memory.get(
                "interaction_notes",
                [],
            ),
        )

        relevant_facts = self._select_legacy_items(
            text=text,
            items=persistent_memory.get(
                "known_facts",
                [],
            ),
        )

        return {
            "retriever": self.name,
            "status": "ready",
            "owner": {
                "preferred_name": (
                    persistent_memory.get(
                        "preferred_name"
                    )
                ),
                "preferred_language": (
                    persistent_memory.get(
                        "preferred_language"
                    )
                ),
                "conversation_count": (
                    persistent_memory.get(
                        "conversation_count"
                    )
                ),
                "last_seen": (
                    persistent_memory.get(
                        "last_seen"
                    )
                ),
            },
            "core_memories": core_memories,
            "relevant_memories": relevant_memories,
            "relevant_facts": relevant_facts,
            "relevant_notes": relevant_notes,
            "summary": (
                "Structured durable memory retrieved "
                "for current reasoning."
            ),
        }

    def _select_core_memories(
        self,
        memory_items: list[Any],
        limit: int = 12,
    ) -> list[dict[str, Any]]:

        selected = []

        for item in memory_items:
            if not isinstance(
                item,
                dict,
            ):
                continue

            memory_type = str(
                item.get(
                    "memory_type",
                    "",
                )
            ).strip().lower()

            content = str(
                item.get(
                    "content",
                    "",
                )
            ).strip()

            if (
                memory_type
                in self.CORE_MEMORY_TYPES
                and content
            ):
                selected.append(item)

        selected.sort(
            key=lambda item: float(
                item.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            ),
            reverse=True,
        )

        return selected[:limit]

    def _select_relevant_memories(
        self,
        text: str,
        memory_items: list[Any],
        excluded_ids: set[Any] | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]]:

        excluded_ids = excluded_ids or set()
        scored_items = []

        for item in memory_items:
            if not isinstance(
                item,
                dict,
            ):
                continue

            if item.get(
                "memory_id"
            ) in excluded_ids:
                continue

            content = str(
                item.get(
                    "content",
                    "",
                )
            ).strip()

            if not content:
                continue

            score = self._score_memory(
                text=text,
                item=item,
            )

            if score < 0.12:
                continue

            enriched_item = {
                **item,
                "retrieval_score": round(
                    score,
                    3,
                ),
            }

            scored_items.append(
                enriched_item
            )

        scored_items.sort(
            key=lambda item: item.get(
                "retrieval_score",
                0.0,
            ),
            reverse=True,
        )

        return scored_items[:limit]

    def _score_memory(
        self,
        text: str,
        item: dict[str, Any],
    ) -> float:

        content = str(
            item.get(
                "content",
                "",
            )
        )

        project = str(
            item.get(
                "project",
                "",
            )
            or ""
        )

        query_terms = self._terms(
            text
        )

        content_terms = self._terms(
            content
        )

        if query_terms:
            token_overlap = (
                len(
                    query_terms
                    & content_terms
                )
                / len(query_terms)
            )
        else:
            token_overlap = 0.0

        character_similarity = (
            self._character_similarity(
                text,
                content,
            )
        )

        project_similarity = 0.0

        if project:
            project_similarity = (
                self._character_similarity(
                    text,
                    project,
                )
            )

        try:
            confidence = float(
                item.get(
                    "confidence",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(
            0.0,
            min(confidence, 1.0),
        )

        score = (
            token_overlap * 0.50
            + character_similarity * 0.25
            + project_similarity * 0.15
            + confidence * 0.10
        )

        return min(
            score,
            1.0,
        )

    def _select_legacy_items(
        self,
        text: str,
        items: list[Any],
        limit: int = 8,
    ) -> list[Any]:

        if not isinstance(
            items,
            list,
        ):
            return []

        scored_items = []

        for item in items:
            item_text = str(
                item
            ).strip()

            if not item_text:
                continue

            score = (
                self._character_similarity(
                    text,
                    item_text,
                )
            )

            if score >= 0.12:
                scored_items.append(
                    {
                        "item": item,
                        "score": score,
                    }
                )

        scored_items.sort(
            key=lambda entry: entry[
                "score"
            ],
            reverse=True,
        )

        return [
            entry["item"]
            for entry in scored_items[:limit]
        ]

    def _terms(
        self,
        value: Any,
    ) -> set[str]:

        normalized = self._normalize(
            value
        )

        return {
            term
            for term in normalized.split()
            if len(term) >= 3
        }

    def _character_similarity(
        self,
        first_value: Any,
        second_value: Any,
    ) -> float:

        first_grams = self._trigrams(
            first_value
        )

        second_grams = self._trigrams(
            second_value
        )

        if not first_grams or not second_grams:
            return 0.0

        intersection = len(
            first_grams & second_grams
        )

        union = len(
            first_grams | second_grams
        )

        if not union:
            return 0.0

        return intersection / union

    def _trigrams(
        self,
        value: Any,
    ) -> set[str]:

        normalized = self._normalize(
            value
        ).replace(
            " ",
            "_",
        )

        if len(normalized) < 3:
            return {
                normalized
            } if normalized else set()

        return {
            normalized[index:index + 3]
            for index in range(
                len(normalized) - 2
            )
        }

    def _normalize(
        self,
        value: Any,
    ) -> str:

        lowered = str(
            value or ""
        ).lower()

        words = re.findall(
            r"\w+",
            lowered,
            flags=re.UNICODE,
        )

        return " ".join(
            words
        )
