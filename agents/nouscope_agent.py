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

    def __init__(self):
        self.workspace = None

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

        previous_context = ""
        previous_signals = []

        knowledge_quality = "unknown"
        nous_level = None
        doxa_level = None
        reduction_level = None

        if self.workspace is not None:
            previous_context = self.workspace.previous_summary(
                "NOUSCOPE"
            )

            previous_signals = self.workspace.previous_signals(
                "NOUSCOPE"
            )

            for signal in previous_signals:
                if signal.get("agent") == "knowledge":
                    answer = signal.get("answer", "")

                    if (
                        answer
                        and "not found" not in answer.lower()
                    ):
                        knowledge_quality = "available"
                    else:
                        knowledge_quality = "missing"

                elif signal.get("agent") == "nous":
                    nous_level = signal.get("nous_level")

                elif signal.get("agent") == "doxa":
                    doxa_level = signal.get("doxa_level")

                elif signal.get("agent") == "reduction":
                    reduction_level = signal.get("reduction_level")

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

        if reduction_level is not None:
            summary = (
                "NOUSCOPE evaluated cognitive filters after considering "
                "Knowledge, Nous, Doxa and Reduction."
            )
        elif cognitive_filter_level > 0.60:
            summary = (
                "Significant cognitive filtering may influence interpretation."
            )
        else:
            summary = "No strong cognitive filter influence detected."

        result = {
            "agent": self.name,
            "cognitive_filter_level": cognitive_filter_level,
            "filter_markers": filter_markers,
            "emotional_markers": emotional_markers,
            "cultural_markers": cultural_markers,
            "memory_markers": memory_markers,
            "possible_filter_influence": cognitive_filter_level > 0.60,

            "previous_context": previous_context,
            "previous_signals": previous_signals,

            "knowledge_quality": knowledge_quality,
            "nous_level": nous_level,
            "doxa_level": doxa_level,
            "reduction_level": reduction_level,

            "summary": summary,
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
