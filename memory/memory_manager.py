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

    def _is_long_term_relevant(self, memory_item: dict[str, Any]) -> bool:
        """
        Decide whether an interaction deserves long-term storage.

        This first version uses simple signals.
        Later versions will use semantic importance, emotional weight,
        project relevance and user-specific continuity markers.
        """

        text = str(memory_item).lower()

        markers = [
            "project",
            "dede",
            "daimon",
            "memory",
            "mecroyance",
            "mécroyance",
            "doxa",
            "nouscope",
            "important",
            "remember",
            "long-term",
            "architecture",
        ]

        return any(marker in text for marker in markers)
