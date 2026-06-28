"""
DeDe - Nous Agent

The Nous Agent evaluates integrated understanding, coherence,
meaning relations and conceptual synthesis.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from interfaces.cognitive_agent import CognitiveAgent


class NousAgent(CognitiveAgent):
    """
    Cognitive agent responsible for integrated understanding.
    """

    name = "nous"

    def __init__(self):
        self.workspace = None

    def can_handle(self, state: CognitiveState) -> bool:
        """
        Nous is broadly useful and can handle most cognitive states.
        """

        return bool(state.user_input.strip())

    def analyze(self, state: CognitiveState) -> dict[str, Any]:
        """
        Produce a first symbolic Nous analysis.
        """

        text = state.user_input.lower()

        previous_context = ""

        previous_signals = []
        knowledge_available = False
        knowledge_source = None

        knowledge_answer = ""
        knowledge_quality = "unknown"

        if self.workspace is not None:
            previous_context = self.workspace.previous_summary(
                "Nous"
            )
            previous_signals = self.workspace.previous_signals(
                "Nous"
            )
            
            for signal in previous_signals:
                if signal.get("agent") == "knowledge":
                    knowledge_available = True
                    knowledge_source = signal.get("source")
                    knowledge_answer = signal.get("answer", "")

                    if (
                        knowledge_answer
                        and "not found" not in knowledge_answer.lower()
                    ):
                        knowledge_quality = "available"
                    else:
                        knowledge_quality = "missing"

                    break

        relation_markers = self._count_markers(
            text,
            [
                "because",
                "therefore",
                "so",
                "if",
                "then",
                "but",
                "however",
                "whereas",
                "while",
                "relation",
                "link",
                "connection",
            ],
        )

        synthesis_markers = self._count_markers(
            text,
            [
                "understand",
                "meaning",
                "sense",
                "coherence",
                "structure",
                "integrate",
                "synthesis",
                "interpretation",
                "concept",
            ],
        )

        contradiction_markers = self._count_markers(
            text,
            [
                "contradiction",
                "paradox",
                "tension",
                "conflict",
                "opposite",
                "incoherent",
                "inconsistency",
            ],
        )

        nous_level = min(
            1.0,
            0.35
            + relation_markers * 0.08
            + synthesis_markers * 0.1
            + contradiction_markers * 0.06,
        )

        if knowledge_available:
            summary = (
                f"Integrated after considering knowledge "
                f"from {knowledge_source}."
            )
        elif previous_context:
            summary = (
                "Integrated after considering previous committee observations."
            )
        else:
            summary = (
                "The input requires integration of meaning, "
                "context and conceptual relations."
            )

        if knowledge_quality == "missing":
            committee_reply = (
                "Without available knowledge, integration remains partial."
            )
        elif knowledge_quality == "available":
            committee_reply = (
                "Knowledge is available, but conceptual integration remains limited."
            )
        else:
            committee_reply = (
                "Integration requires more context from the committee."
            )

        result = {
            "agent": self.name,
            "nous_level": nous_level,
            "relation_markers": relation_markers,
            "synthesis_markers": synthesis_markers,
            "contradiction_markers": contradiction_markers,
            "previous_context": previous_context,
            "previous_signals": previous_signals,
            "integrated_understanding_needed": True,
            "summary": summary,
            "committee_reply": committee_reply,
            "knowledge_available": knowledge_available,
            "knowledge_source": knowledge_source,
            "knowledge_answer": knowledge_answer,
            "knowledge_quality": knowledge_quality,
        }

        state.nous_level = nous_level

        return result

    def _count_markers(self, text: str, markers: list[str]) -> int:
        """
        Count simple textual markers.
        """

        return sum(1 for marker in markers if marker in text)
