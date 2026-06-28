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

    def __init__(self):
        self.workspace = None

    def can_handle(self, state: CognitiveState) -> bool:
        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:

        text = state.user_input.lower()

        previous_context = ""
        previous_signals = []

        nous_available = False
        nous_level = None
        nous_summary = ""

        knowledge_available = False
        knowledge_quality = "unknown"

        if self.workspace is not None:
            previous_context = self.workspace.previous_summary(
                "Doxa"
            )
            previous_signals = self.workspace.previous_signals(
                "Doxa"
            )

            for signal in previous_signals:
                if signal.get("agent") == "nous":
                    nous_available = True
                    nous_level = signal.get("nous_level")
                    nous_summary = signal.get("summary", "")

                if signal.get("agent") == "knowledge":
                    knowledge_available = True
                    answer = signal.get("answer", "")

                    if answer and "not found" not in answer.lower():
                        knowledge_quality = "available"
                    else:
                        knowledge_quality = "missing"

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

        if cognitive_closure:
            summary = "High certainty detected."
        elif nous_available:
            summary = (
                "Certainty evaluated after considering Nous integration."
            )
        else:
            summary = "Certainty remains cognitively revisable."

        if cognitive_closure:
            committee_reply = (
                "Certainty appears too strong and may reduce revisability."
            )
        elif knowledge_quality == "missing":
            committee_reply = (
                "Certainty should remain moderate because knowledge is missing."
            )
        elif (
            nous_available
            and nous_level is not None
            and nous_level < 0.50
        ):
            committee_reply = (
                "Certainty should remain cautious because integrated understanding is still limited."
            )
        else:
            committee_reply = (
                "Certainty remains moderate and cognitively revisable."
            )

        result = {
            "agent": self.name,
            "doxa_level": doxa_level,
            "certainty_markers": certainty_markers,
            "nuance_markers": nuance_markers,
            "cognitive_closure": cognitive_closure,
            "previous_context": previous_context,
            "previous_signals": previous_signals,
            "knowledge_available": knowledge_available,
            "knowledge_quality": knowledge_quality,
            "nous_available": nous_available,
            "nous_level": nous_level,
            "nous_summary": nous_summary,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        state.doxa_level = doxa_level

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        return sum(1 for marker in markers if marker in text)
