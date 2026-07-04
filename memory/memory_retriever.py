"""
DeDe - Memory Retriever

Retrieves relevant memory before LLM reasoning.

This first version is simple:
- always returns core owner memory
- selects notes/facts that overlap with the current message
"""

from typing import Any


class MemoryRetriever:

    name = "memory_retriever"

    def retrieve(
        self,
        text: str,
        persistent_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        persistent_memory = persistent_memory or {}
        lowered = text.lower()

        relevant_notes = self._select_relevant_items(
            lowered,
            persistent_memory.get("interaction_notes", []),
        )

        relevant_facts = self._select_relevant_items(
            lowered,
            persistent_memory.get("known_facts", []),
        )

        return {
            "retriever": self.name,
            "status": "ready",
            "owner": {
                "preferred_name": persistent_memory.get("preferred_name"),
                "preferred_language": persistent_memory.get("preferred_language"),
                "conversation_count": persistent_memory.get("conversation_count"),
                "last_seen": persistent_memory.get("last_seen"),
            },
            "relevant_facts": relevant_facts,
            "relevant_notes": relevant_notes,
            "summary": (
                "Relevant persistent memory retrieved for current reasoning."
            ),
        }

    def _select_relevant_items(
        self,
        lowered_text: str,
        items: list[Any],
        limit: int = 8,
    ) -> list[Any]:

        if not items:
            return []

        words = {
            word.strip(".,;:!?()[]{}\"'")
            for word in lowered_text.split()
            if len(word.strip(".,;:!?()[]{}\"'")) >= 4
        }

        selected = []

        for item in items:
            item_text = str(item).lower()

            if any(word in item_text for word in words):
                selected.append(item)

            if len(selected) >= limit:
                break

        return selected
