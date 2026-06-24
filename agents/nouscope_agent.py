"""
DeDe - NOUSCOPE Agent

The NOUSCOPE Agent evaluates cognitive filters, interpretive frames,
perspective calibration and possible influences shaping perception.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from interfaces.cognitive_agent import CognitiveAgent


class NOUSCOPEAgent(CognitiveAgent):
    """
    Cognitive agent responsible for cognitive filter modeling.
    """

    name = "nouscope"

    def can_handle(self, state: CognitiveState) -> bool:
        """
        NOUSCOPE can evaluate most interpretive inputs.
        """

        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:
        """
        Produce a first symbolic NOUSCOPE analysis.
        """

        text = state.user_input.lower()

        filter_markers = self._count_markers(
            text,
            [
                "filter",
                "perception",
                "bias",
                "interpretation",
                "perspective",
                "frame",
                "mental model",
                "worldview",
            ],
        )

        emotional_markers = self._count_markers(
            text,
            [
                "fear",
                "anger",
                "sad",
                "stress",
                "hope",
                "desire",
                "hate",
                "love",
                "pain",
            ],
        )

        cultural_markers = self._count_markers(
            text,
            [
                "culture",
                "society",
                "education",
                "religion",
                "politics",
                "ideology",
                "media",
                "tradition",
            ],
        )

        memory_markers = self._count_markers(
            text,
            [
                "remember",
                "memory",
                "past",
                "experience",
                "history",
                "trauma",
                "habit",
            ],
        )

        cognitive_filter_level = min(
            1.0,
            0.30
            + filter_markers * 0.12
            + emotional_markers * 0.08
            + cultural_markers * 0.08
            + memory_markers * 0.06,
        )

        result = {
            "agent": self.name,
            "cognitive_filter_level": cognitive_filter_level,
            "filter_markers": filter_markers,
            "emotional_markers": emotional_markers,
            "cultural_markers": cultural_markers,
            "memory_markers": memory_markers,
            "possible_filter_influence": cognitive_filter_level > 0.60,
            "summary": (
                "Significant cognitive filtering may influence interpretation."
                if cognitive_filter_level > 0.60
                else "No strong cognitive filter influence detected."
            ),
        }

        state.metadata["nouscope"] = {
            "cognitive_filter_level": cognitive_filter_level
        }

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        """
        Count simple textual markers.
        """

        return sum(1 for marker in markers if marker in text)
