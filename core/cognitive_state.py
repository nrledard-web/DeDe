"""
DeDe - Cognitive State

Shared internal state of DeDe during a cognitive cycle.

The CognitiveState object stores the evolving understanding of a user input:
intent, context, memory, active agents, analyses, confidence levels and final response.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class CognitiveState:
    """
    Represents the shared cognitive state of DeDe for one interaction.
    """

    user_input: str
    context: dict = field(default_factory=dict)

    state_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    intent: str | None = None
    priority: str | None = None

    memory: dict = field(default_factory=dict)
    active_agents: list[str] = field(default_factory=list)
    execution_plan: list[str] = field(default_factory=list)

    analyses: dict[str, Any] = field(default_factory=dict)

    gnosis_level: float | None = None
    nous_level: float | None = None
    doxa_level: float | None = None
    reduction_level: float | None = None
    revisability_level: float | None = None

    confidence: float | None = None
    final_response: str | None = None

    metadata: dict = field(default_factory=dict)

    def add_analysis(self, agent_name: str, result: Any) -> None:
        """
        Store an analysis produced by a cognitive agent.
        """

        self.analyses[agent_name] = result

    def activate_agent(self, agent_name: str) -> None:
        """
        Mark an agent as active during this cognitive cycle.
        """

        if agent_name not in self.active_agents:
            self.active_agents.append(agent_name)

    def set_execution_plan(self, plan: list[str]) -> None:
        """
        Store the execution plan selected by the Executive Controller.
        """

        self.execution_plan = plan

    def to_dict(self) -> dict:
        """
        Convert the cognitive state into a serializable dictionary.
        """

        return {
            "state_id": self.state_id,
            "created_at": self.created_at,
            "user_input": self.user_input,
            "context": self.context,
            "intent": self.intent,
            "priority": self.priority,
            "memory": self.memory,
            "active_agents": self.active_agents,
            "execution_plan": self.execution_plan,
            "analyses": self.analyses,
            "gnosis_level": self.gnosis_level,
            "nous_level": self.nous_level,
            "doxa_level": self.doxa_level,
            "reduction_level": self.reduction_level,
            "revisability_level": self.revisability_level,
            "confidence": self.confidence,
            "final_response": self.final_response,
            "metadata": self.metadata,
        }
