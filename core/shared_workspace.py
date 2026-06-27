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

    def previous_observations(
        self,
        current_agent: str,
    ):
        previous = []

        for obs in self.observations:
            if obs.agent.lower() == current_agent.lower():
                break

            previous.append(obs)

        return previous

    def previous_summary(
        self,
        current_agent: str,
    ):
        previous = self.previous_observations(
            current_agent
        )

        if not previous:
            return ""

        return "\n".join(
            f"{obs.agent}: {obs.observation}"
            for obs in previous
        )

    def previous_signals(
        self,
        current_agent: str,
    ):
        previous = self.previous_observations(
            current_agent
        )

        cleaned_signals = []

        for obs in previous:
            signals = dict(obs.signals)

            signals.pop(
                "previous_signals",
                None,
            )

            signals.pop(
                "previous_context",
                None,
            )

            cleaned_signals.append(
                signals
            )

        return cleaned_signals

    def get_all(self):
        return self.observations

    def get_agent(self, agent_name: str):
        return [
            obs
            for obs in self.observations
            if obs.agent.lower() == agent_name.lower()
        ]

    def latest(self):
        if not self.observations:
            return None

        return self.observations[-1]

    def agents(self):
        return sorted(
            {
                obs.agent
                for obs in self.observations
            }
        )

    def high_confidence(
        self,
        threshold: float = 0.7,
    ):
        return [
            obs
            for obs in self.observations
            if obs.confidence >= threshold
        ]

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
