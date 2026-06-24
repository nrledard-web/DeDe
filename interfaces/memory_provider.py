"""
DeDe - Memory Provider Interface

Abstract interface for long-term and short-term memory providers.
"""

from abc import ABC, abstractmethod
from typing import Any

from core.cognitive_state import CognitiveState


class MemoryProvider(ABC):
    """
    Base interface for DeDe memory systems.
    """

    @abstractmethod
    def retrieve(self, state: CognitiveState) -> dict[str, Any]:
        """
        Retrieve relevant memories for the current cognitive state.
        """
        pass

    @abstractmethod
    def store(self, state: CognitiveState) -> None:
        """
        Persist the updated cognitive state into memory.
        """
        pass

    @abstractmethod
    def search(self, query: str) -> list[Any]:
        """
        Search memory using semantic or keyword retrieval.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the memory store.
        """
        pass
