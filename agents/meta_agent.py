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

        parts = []

        if strengths:
            parts.append(strengths[0])

        if weaknesses:
            parts.append(weaknesses[0])

        if diagnoses:
            parts.append(diagnoses[0])

        if next_steps:
            parts.append(next_steps[0])

        if not parts:
            return (
                "The committee found no major cognitive imbalance "
                "and recommends maintaining revisability."
            )

        return " ".join(parts)
