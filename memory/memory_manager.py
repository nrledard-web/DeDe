"""
DeDe - Memory Manager

Central memory coordinator for DeDe.

The MemoryManager is responsible for storing, retrieving and organizing
the information needed to preserve long-term cognitive continuity.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from interfaces.memory_provider import MemoryProvider


class MemoryManager(MemoryProvider):
    """
    First implementation of DeDe's memory system.

    This initial version uses an in-memory store.
    Later versions will connect to persistent databases, vector stores,
    semantic indexes and autobiographical memory systems.
    """

    def __init__(self):
        self.short_term_memory: list[dict[str, Any]] = []
        self.long_term_memory: list[dict[str, Any]] = []

    def retrieve(self, state: CognitiveState) -> dict[str, Any]:
        """
        Retrieve relevant memory for the current cognitive state.
        """

        return {
            "short_term": self.short_term_memory[-10:],
            "long_term": self.long_term_memory[-20:],
        }

    def store(self, state: CognitiveState) -> None:
        """
        Store the current cognitive state.
        """

        memory_item = {
            "state_id": state.state_id,
            "created_at": state.created_at,
            "user_input": state.user_input,
            "intent": state.intent,
            "priority": state.priority,
            "active_agents": state.active_agents,
            "execution_plan": state.execution_plan,
            "analyses": state.analyses,
            "final_response": state.final_response,
            "metadata": state.metadata,
        }

        self.short_term_memory.append(memory_item)

        if self._is_long_term_relevant(memory_item):
            self.long_term_memory.append(memory_item)

    def search(self, query: str) -> list[Any]:
        """
        Search memory using simple keyword matching.
        """

        query = query.lower()
        results = []

        for item in self.short_term_memory + self.long_term_memory:
            text = str(item).lower()
            if query in text:
                results.append(item)

        return results

    def clear(self) -> None:
        """
        Clear all memory stores.
        """

        self.short_term_memory.clear()
        self.long_term_memory.clear()

    def _is_long_term_relevant(
        self,
        memory_item: dict[str, Any],
    ) -> bool:
        """
        Decide whether an interaction deserves long-term storage
        from structured cognitive information rather than lexical
        markers.

        This legacy MemoryManager should not infer durability from
        particular words or languages.
        """

        if not isinstance(
            memory_item,
            dict,
        ):
            return False

        metadata = memory_item.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        # --------------------------------------------------
        # Explicit structured persistence signal
        # --------------------------------------------------

        if bool(
            metadata.get(
                "long_term_relevant",
                False,
            )
        ):
            return True

        if bool(
            metadata.get(
                "durable_memory",
                False,
            )
        ):
            return True

        # --------------------------------------------------
        # Explicit structured priority signal
        # --------------------------------------------------

        priority = memory_item.get(
            "priority"
        )

        if isinstance(
            priority,
            (int, float),
        ):
            return priority >= 0.75

        return False
