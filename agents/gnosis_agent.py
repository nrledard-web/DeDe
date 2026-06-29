"""
DeDe - Gnosis Agent

The Gnosis Agent evaluates articulated knowledge, factual grounding,
conceptual precision and the need for verification.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from core.cognitive_dynamics import GroundingDynamic
from interfaces.cognitive_agent import CognitiveAgent


class GnosisAgent(CognitiveAgent):
    """
    Cognitive agent responsible for knowledge grounding and factual precision.
    """

    name = "gnosis"

    def can_handle(self, state: CognitiveState) -> bool:
        """
        Decide whether Gnosis should analyze the current input.
        """

        text = state.user_input.lower()

        markers = [
            "fact",
            "source",
            "verify",
            "evidence",
            "proof",
            "true",
            "false",
            "history",
            "science",
            "law",
            "constitution",
            "research",
            "data",
            "document",
            "citation",
        ]

        return any(marker in text for marker in markers)

    def analyze(self, state: CognitiveState) -> dict[str, Any]:
        """
        Produce a symbolic Gnosis analysis using GroundingDynamic.
        """

        text = state.user_input.lower()

        factual_markers = self._count_markers(
            text,
            [
                "fact",
                "source",
                "evidence",
                "proof",
                "data",
                "citation",
                "research",
            ],
        )

        uncertainty_markers = self._count_markers(
            text,
            [
                "maybe",
                "perhaps",
                "possible",
                "seems",
                "appears",
                "uncertain",
                "hypothesis",
            ],
        )

        verification_needed = factual_markers > 0 or any(
            marker in text
            for marker in [
                "verify",
                "true",
                "false",
                "law",
                "science",
                "history",
                "constitution",
            ]
        )

        base_gnosis_level = min(
            1.0,
            0.30
            + factual_markers * 0.10
            + uncertainty_markers * 0.05,
        )

        grounding_dynamic = GroundingDynamic().evaluate(
            {
                "grounding_signal": base_gnosis_level,
            }
        )

        gnosis_effect = grounding_dynamic.value * 0.20

        gnosis_level = min(
            1.0,
            max(
                0.0,
                base_gnosis_level + gnosis_effect,
            ),
        )

        result = {
            "agent": self.name,
            "gnosis_level": gnosis_level,
            "base_gnosis_level": base_gnosis_level,
            "factual_markers": factual_markers,
            "uncertainty_markers": uncertainty_markers,
            "verification_needed": verification_needed,
            "summary": (
                "The input appears to require knowledge grounding and factual precision."
                if verification_needed
                else "No strong factual verification requirement detected."
            ),
            "grounding_dynamic": {
                "value": grounding_dynamic.value,
                "gnosis_effect": gnosis_effect,
                "description": grounding_dynamic.description,
            },
        }

        state.gnosis_level = gnosis_level

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        """
        Count simple textual markers.
        """

        return sum(1 for marker in markers if marker in text)
