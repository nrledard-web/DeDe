"""
DeDe - Doxa Agent

The Doxa Agent evaluates certainty, cognitive closure,
assertiveness and epistemic rigidity.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from interfaces.cognitive_agent import CognitiveAgent


class DoxaAgent(CognitiveAgent):
    """
    Cognitive agent responsible for evaluating certainty.
    """

    name = "doxa"

    def can_handle(self, state: CognitiveState) -> bool:
        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:

        text = state.user_input.lower()

        certainty_markers = self._count_markers(
            text,
            [
                "always",
                "never",
                "certain",
                "obviously",
                "everyone",
                "nobody",
                "undeniable",
                "must",
                "cannot",
                "impossible",
                "definitely",
                "absolutely",
            ],
        )

        nuance_markers = self._count_markers(
            text,
            [
                "maybe",
                "perhaps",
                "possible",
                "might",
                "could",
                "sometimes",
                "depends",
                "uncertain",
            ],
        )

        doxa_level = min(
            1.0,
            max(
                0.0,
                0.40 + certainty_markers * 0.10 - nuance_markers * 0.05,
            ),
        )

        cognitive_closure = doxa_level > 0.75

        result = {
            "agent": self.name,
            "doxa_level": doxa_level,
            "certainty_markers": certainty_markers,
            "nuance_markers": nuance_markers,
            "cognitive_closure": cognitive_closure,
            "summary": (
                "High certainty detected."
                if cognitive_closure
                else "Certainty remains cognitively revisable."
            ),
        }

        state.doxa_level = doxa_level

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        return sum(1 for marker in markers if marker in text)
