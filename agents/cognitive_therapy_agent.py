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

    def __init__(self):
        self.workspace = None

    def can_handle(self, state: CognitiveState) -> bool:
        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:

        previous_context = ""
        previous_signals = []

        knowledge_quality = "unknown"
        nous_level = None
        doxa_level_from_committee = None
        reduction_level_from_committee = None
        cognitive_filter_level = None

        if self.workspace is not None:
            previous_context = self.workspace.previous_summary(
                "Cognitive Therapy"
            )

            previous_signals = self.workspace.previous_signals(
                "Cognitive Therapy"
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
                    doxa_level_from_committee = signal.get("doxa_level")

                elif signal.get("agent") == "reduction":
                    reduction_level_from_committee = signal.get(
                        "reduction_level"
                    )

                elif signal.get("agent") == "nouscope":
                    cognitive_filter_level = signal.get(
                        "cognitive_filter_level"
                    )

        doxa_level = state.doxa_level or 0.0
        reduction_level = state.reduction_level or 0.0
        gnosis_level = state.gnosis_level or 0.0
        nous_state_level = state.nous_level or 0.0

        recalibration_needed = (
            doxa_level > 0.65
            or reduction_level > 0.60
            or (gnosis_level + nous_state_level) < doxa_level
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

        if nous_state_level < 0.40:
            strategies.append(
                "Improve integrated understanding by connecting facts, context and meaning."
            )

        if cognitive_filter_level is not None and cognitive_filter_level > 0.60:
            strategies.append(
                "Examine possible cognitive filters influencing interpretation."
            )

        if knowledge_quality == "missing":
            strategies.append(
                "Clarify or retrieve missing knowledge before final interpretation."
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

        summary = (
            "Cognitive recalibration is recommended after reviewing the committee."
            if recalibration_needed
            else "Cognitive state appears sufficiently revisable after committee review."
        )

        result = {
            "agent": self.name,
            "recalibration_needed": recalibration_needed,
            "revisability_level": revisability_level,
            "strategies": strategies,

            "previous_context": previous_context,
            "previous_signals": previous_signals,

            "knowledge_quality": knowledge_quality,
            "nous_level": nous_level,
            "doxa_level_from_committee": doxa_level_from_committee,
            "reduction_level_from_committee": reduction_level_from_committee,
            "cognitive_filter_level": cognitive_filter_level,

            "summary": summary,
        }

        state.revisability_level = revisability_level

        return result
