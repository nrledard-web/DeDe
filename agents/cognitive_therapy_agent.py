"""
DeDe - Cognitive Therapy Agent

The Cognitive Therapy Agent proposes cognitive recalibration strategies,
alternative hypotheses and revisability improvements.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from interfaces.cognitive_agent import CognitiveAgent


class CognitiveTherapyAgent(CognitiveAgent):
    """
    Cognitive agent responsible for restoring revisability and cognitive balance.
    """

    name = "cognitive_therapy"

    def can_handle(self, state: CognitiveState) -> bool:
        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:
        doxa_level = state.doxa_level or 0.0
        reduction_level = state.reduction_level or 0.0
        gnosis_level = state.gnosis_level or 0.0
        nous_level = state.nous_level or 0.0

        recalibration_needed = (
            doxa_level > 0.65
            or reduction_level > 0.60
            or (gnosis_level + nous_level) < doxa_level
        )

        strategies = []

        if doxa_level > 0.65:
            strategies.append(
                "Reduce certainty by introducing alternative interpretations."
            )

        if reduction_level > 0.60:
            strategies.append(
                "Expand the frame by identifying hidden assumptions and missing dimensions."
            )

        if gnosis_level < 0.40:
            strategies.append(
                "Strengthen factual grounding through verification, sources and evidence."
            )

        if nous_level < 0.40:
            strategies.append(
                "Improve integrated understanding by connecting facts, context and meaning."
            )

        if not strategies:
            strategies.append(
                "Maintain cognitive revisability while preserving the current interpretive structure."
            )

        revisability_level = min(
            1.0,
            0.40
            + len(strategies) * 0.10
            + max(0.0, 1.0 - doxa_level) * 0.20,
        )

        result = {
            "agent": self.name,
            "recalibration_needed": recalibration_needed,
            "revisability_level": revisability_level,
            "strategies": strategies,
            "summary": (
                "Cognitive recalibration is recommended."
                if recalibration_needed
                else "Cognitive state appears sufficiently revisable."
            ),
        }

        state.revisability_level = revisability_level

        return result
