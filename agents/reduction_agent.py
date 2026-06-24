"""
DeDe - Reduction Agent

The Reduction Agent evaluates hidden assumptions,
implicit reductions and missing dimensions.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from interfaces.cognitive_agent import CognitiveAgent


class ReductionAgent(CognitiveAgent):

    name = "reduction"

    def can_handle(self, state: CognitiveState) -> bool:
        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:

        text = state.user_input.lower()

        reduction_markers = self._count_markers(
            text,
            [
                "all",
                "only",
                "nothing",
                "everything",
                "always",
                "never",
                "must",
                "cannot",
                "simple",
                "obvious",
            ],
        )

        missing_dimension_markers = self._count_markers(
            text,
            [
                "except",
                "however",
                "alternative",
                "other",
                "context",
                "depends",
                "possibility",
                "hypothesis",
            ],
        )

        reduction_level = min(
            1.0,
            max(
                0.0,
                0.40
                + reduction_markers * 0.10
                - missing_dimension_markers * 0.05,
            ),
        )

        result = {
            "agent": self.name,
            "reduction_level": reduction_level,
            "reduction_markers": reduction_markers,
            "missing_dimension_markers": missing_dimension_markers,
            "possible_hidden_assumptions": reduction_level > 0.60,
            "summary": (
                "Potential conceptual reduction detected."
                if reduction_level > 0.60
                else "No significant conceptual reduction detected."
            ),
        }

        state.reduction_level = reduction_level

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        return sum(1 for marker in markers if marker in text)
