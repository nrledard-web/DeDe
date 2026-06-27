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

    def __init__(self):
        self.workspace = None

    def can_handle(self, state: CognitiveState) -> bool:
        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:

        text = state.user_input.lower()

        previous_context = ""
        previous_signals = []

        knowledge_available = False
        knowledge_quality = "unknown"

        nous_available = False
        nous_level = None

        doxa_available = False
        doxa_level = None

        if self.workspace is not None:

            previous_context = self.workspace.previous_summary(
                "Reduction"
            )

            previous_signals = self.workspace.previous_signals(
                "Reduction"
            )

            for signal in previous_signals:

                if signal.get("agent") == "knowledge":
                    knowledge_available = True

                    answer = signal.get(
                        "answer",
                        "",
                    )

                    if (
                        answer
                        and "not found"
                        not in answer.lower()
                    ):
                        knowledge_quality = "available"
                    else:
                        knowledge_quality = "missing"

                elif signal.get("agent") == "nous":
                    nous_available = True
                    nous_level = signal.get(
                        "nous_level"
                    )

                elif signal.get("agent") == "doxa":
                    doxa_available = True
                    doxa_level = signal.get(
                        "doxa_level"
                    )

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

        if doxa_available:
            summary = (
                "Reduction evaluated after considering "
                "Knowledge, Nous and Doxa."
            )
        else:
            summary = (
                "Potential conceptual reduction detected."
                if reduction_level > 0.60
                else "No significant conceptual reduction detected."
            )

        result = {
            "agent": self.name,
            "reduction_level": reduction_level,
            "reduction_markers": reduction_markers,
            "missing_dimension_markers": missing_dimension_markers,
            "possible_hidden_assumptions": reduction_level > 0.60,

            "previous_context": previous_context,
            "previous_signals": previous_signals,

            "knowledge_available": knowledge_available,
            "knowledge_quality": knowledge_quality,

            "nous_available": nous_available,
            "nous_level": nous_level,

            "doxa_available": doxa_available,
            "doxa_level": doxa_level,

            "summary": summary,
        }

        state.reduction_level = reduction_level

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        return sum(
            1
            for marker in markers
            if marker in text
        )
