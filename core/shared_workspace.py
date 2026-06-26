from dataclasses import dataclass, field
from typing import Any


@dataclass
class CognitiveObservation:
    agent: str
    level: float
    observation: str
    implication: str
    confidence: float
    signals: dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedCognitiveWorkspace:
    question: str
    response: str
    observations: list[CognitiveObservation] = field(default_factory=list)

    def add_observation(
        self,
        agent: str,
        level: float,
        observation: str,
        implication: str,
        confidence: float,
        signals: dict[str, Any] | None = None,
    ):
        self.observations.append(
            CognitiveObservation(
                agent=agent,
                level=level,
                observation=observation,
                implication=implication,
                confidence=confidence,
                signals=signals or {},
            )
        )

    def find(self, agent_name: str):
        for obs in self.observations:
            if obs.agent.lower() == agent_name.lower():
                return obs
        return None

    def summary(self) -> dict:
        return {
            "question": self.question,
            "response": self.response,
            "observations": [
                {
                    "agent": obs.agent,
                    "level": obs.level,
                    "observation": obs.observation,
                    "implication": obs.implication,
                    "confidence": obs.confidence,
                    "signals": obs.signals,
                }
                for obs in self.observations
            ],
        }
