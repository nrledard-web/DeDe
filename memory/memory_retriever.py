"""
DeDe - Memory Retriever

Retrieves structured durable memory before reasoning.

This retriever is multilingual by structure.
It does not use language-specific marker lists.
"""

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

        persistent_memory = (
            persistent_memory or {}
        )

        owner = persistent_memory.get(
            "owner",
            {},
        )

        if not isinstance(
            owner,
            dict,
        ):
            owner = {}

        memory_items = persistent_memory.get(
            "memory_items",
            [],
        )

        if not isinstance(
            memory_items,
            list,
        ):
            memory_items = []

        core_memories = self._core_memories(
            memory_items
        )

        core_ids = {
            item.get("memory_id")
            for item in core_memories
        }

        relevant_memories = (
            self._relevant_memories(
                text=text,
                memory_items=memory_items,
                excluded_ids=core_ids,
            )
        )

        relevant_facts = (
            self._legacy_items(
                text=text,
                items=persistent_memory.get(
                    "known_facts",
                    [],
                ),
            )
        )

        relevant_notes = (
            self._legacy_items(
                text=text,
                items=persistent_memory.get(
                    "interaction_notes",
                    [],
                ),
            )
        )

        return {
            "retriever": self.name,
            "status": "ready",
            "owner": {
                "preferred_name": (
                    owner.get(
                        "preferred_name"
                    )
                    or persistent_memory.get(
                        "preferred_name"
                    )
                ),
                "preferred_language": (
                    owner.get(
                        "preferred_language"
                    )
                    or persistent_memory.get(
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
            "relevant_memories": (
                relevant_memories
            ),
            "relevant_facts": relevant_facts,
            "relevant_notes": relevant_notes,
            "summary": (
                "Structured durable memory retrieved "
                "for current reasoning."
            ),
        }

    def _core_memories(
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
            key=self._confidence,
            reverse=True,
        )

        return selected[:limit]

    def _relevant_memories(
        self,
        text: str,
        memory_items: list[Any],
        excluded_ids: set[Any],
        limit: int = 8,
    ) -> list[dict[str, Any]]:

        scored = []

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

            similarity = self._similarity(
                text,
                content,
            )

            score = (
                similarity * 0.90
                + self._confidence(item) * 0.10
            )

            if score < 0.12:
                continue

            scored.append(
                {
                    **item,
                    "retrieval_score": round(
                        score,
                        3,
                    ),
                }
            )

        scored.sort(
            key=lambda item: item.get(
                "retrieval_score",
                0.0,
            ),
            reverse=True,
        )

        return scored[:limit]

    def _legacy_items(
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

        scored = []

        for item in items:
            score = self._similarity(
                text,
                str(item),
            )

            if score >= 0.12:
                scored.append(
                    {
                        "item": item,
                        "score": score,
                    }
                )

        scored.sort(
            key=lambda entry: entry[
                "score"
            ],
            reverse=True,
        )

        return [
            entry["item"]
            for entry in scored[:limit]
        ]

    def _similarity(
        self,
        first_value: Any,
        second_value: Any,
    ) -> float:

        first_terms = self._terms(
            first_value
        )

        second_terms = self._terms(
            second_value
        )

        if not first_terms or not second_terms:
            return 0.0

        intersection = len(
            first_terms & second_terms
        )

        union = len(
            first_terms | second_terms
        )

        if not union:
            return 0.0

        return intersection / union

    def _terms(
        self,
        value: Any,
    ) -> set[str]:

        words = re.findall(
            r"\w+",
            str(value or "").lower(),
            flags=re.UNICODE,
        )

        return {
            word
            for word in words
            if len(word) >= 3
        }

    def _confidence(
        self,
        item: dict[str, Any],
    ) -> float:

        try:
            confidence = float(
                item.get(
                    "confidence",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            confidence = 0.0

        return max(
            0.0,
            min(confidence, 1.0),
        )
