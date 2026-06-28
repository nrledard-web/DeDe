"""
Meta Agent
Cognitive Committee
"""

from core.shared_workspace import SharedCognitiveWorkspace
from reasoning.committee_engine import CommitteeEngine
from reasoning.committee_reasoner import CommitteeReasoner


class MetaAgent:

    def __init__(self):
        self.committee_engine = CommitteeEngine()
        self.committee_reasoner = CommitteeReasoner()

    def analyze(
        self,
        workspace: SharedCognitiveWorkspace,
    ):

        committee = self.committee_engine.deliberate(
            workspace
        )

        reasoning = self.committee_reasoner.reason(
            workspace,
            committee,
        )

        narrative = self._build_narrative(
            reasoning
        )

        return {
            "agent": "meta",
            "committee_size": committee["committee_size"],
            "agreements": committee["strong_agreements"],
            "concerns": committee["concerns"],
            "recommendations": committee["recommendations"],
            "agent_positions": committee["agent_positions"],
            "discussion": committee["discussion"],
            "round_table": committee["round_table"],
            "committee_confidence": committee["committee_confidence"],
            "summary": narrative,
            "technical_summary": committee["summary"],
            "confidence": 0.95,
            "coherence": committee["committee_confidence"],
            "reasoning": reasoning,
            "diagnoses": reasoning["diagnoses"],
            "hypotheses": reasoning["hypotheses"],
            "strengths": reasoning["strengths"],
            "weaknesses": reasoning["weaknesses"],
            "conflicts": reasoning["conflicts"],
            "recommended_next_steps": reasoning["recommended_next_steps"],
            "narrative": narrative,
        }

    def _build_narrative(
        self,
        reasoning,
    ):
        strengths = reasoning.get("strengths", [])
        weaknesses = reasoning.get("weaknesses", [])
        diagnoses = reasoning.get("diagnoses", [])
        next_steps = reasoning.get("recommended_next_steps", [])

        has_knowledge = any(
            "knowledge" in item.lower()
            for item in strengths
        )

        weak_integration = any(
            "understanding remains weak" in item.lower()
            or "weakly integrated" in item.lower()
            for item in weaknesses + diagnoses
        )

        certainty_exceeds_understanding = any(
            "certainty" in item.lower()
            and "understanding" in item.lower()
            for item in diagnoses
        )

        if has_knowledge and weak_integration:
            opening = (
                "The committee has a factual basis, "
                "but integrated understanding remains weak."
            )
        elif has_knowledge:
            opening = (
                "The committee has a factual basis for analysis."
            )
        elif weak_integration:
            opening = (
                "The committee detects weak conceptual integration."
            )
        else:
            opening = (
                "The committee found no major cognitive imbalance."
            )

        if certainty_exceeds_understanding:
            middle = (
                "Certainty should therefore remain cautious "
                "until understanding becomes more integrated."
            )
        else:
            middle = (
                "The current interpretation should remain revisable."
            )

        if next_steps:
            closing = (
                f"The recommended next step is to "
                f"{next_steps[0][0].lower()}{next_steps[0][1:]}"
            )
        else:
            closing = (
                "The recommended next step is to maintain revisability."
            )

        return (
            f"{opening} "
            f"{middle} "
            f"{closing}"
        )
