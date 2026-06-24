"""
DeDe - Cognitive Agent Interface

Defines the abstract contract that every cognitive agent must follow.
"""

from abc import ABC, abstractmethod
from typing import Any

from core.cognitive_state import CognitiveState
from core.message_bus import MessageBus


class CognitiveAgent(ABC):
    """
    Base interface for all DeDe cognitive agents.
    """

    name: str = "cognitive_agent"

    def __init__(self, message_bus: MessageBus | None = None):
        self.message_bus = message_bus

    def initialize(self) -> None:
        """
        Optional initialization hook.
        """
        pass

    @abstractmethod
    def can_handle(self, state: CognitiveState) -> bool:
        """
        Decide whether this agent should process the current cognitive state.
        """
        pass

    @abstractmethod
    def analyze(self, state: CognitiveState) -> Any:
        """
        Analyze the current cognitive state and return this agent's contribution.
        """
        pass

    def update_state(self, state: CognitiveState, result: Any) -> CognitiveState:
        """
        Store the agent's analysis inside the shared cognitive state.
        """
        state.add_analysis(self.name, result)
        state.activate_agent(self.name)
        return state

    def shutdown(self) -> None:
        """
        Optional shutdown hook.
        """
        pass
