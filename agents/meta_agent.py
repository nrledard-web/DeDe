"""
Meta Agent
Cognitive Committee
"""

from core.shared_workspace import SharedCognitiveWorkspace
from reasoning.committee_engine import CommitteeEngine


class MetaAgent:

    def __init__(self):
        self.committee_engine = CommitteeEngine()

    def analyze(
        self,
        workspace: SharedCognitiveWorkspace,
    ):

        committee = self.committee_engine.deliberate(
            workspace
        )

        diagnoses = []

        knowledge = workspace.find("Knowledge")
        nous = workspace.find("Nous")
        doxa = workspace.find("Doxa")
        reduction = workspace.find("Reduction")
        nouscope = workspace.find("NOUSCOPE")
        therapy = workspace.find("Cognitive Therapy")

        if (
            knowledge
            and nous
            and knowledge.confidence > 0.80
            and nous.confidence < 0.50
        ):
            diagnoses.append(
                "Knowledge is available but remains weakly integrated."
            )

        if (
            nous
            and doxa
            and doxa.confidence > nous.confidence
        ):
            diagnoses.append(
                "Certainty currently exceeds integrated understanding."
            )

        if (
            doxa
            and reduction
            and doxa.confidence > 0.60
            and reduction.confidence > 0.60
        ):
            diagnoses.append(
                "High certainty combines with conceptual reduction."
            )

        if (
            reduction
            and nouscope
            and reduction.confidence > 0.50
            and nouscope.confidence > 0.50
        ):
            diagnoses.append(
                "Cognitive filters may reinforce conceptual reductions."
            )

        if (
            therapy
            and therapy.confidence > 0.70
        ):
            diagnoses.append(
                "The committee recommends cognitive recalibration."
            )

        if (
            not diagnoses
        ):
            diagnoses.append(
                "No major cognitive imbalance detected by the committee."
            )

        return {
            "agent": "meta",

            "committee_size": committee["committee_size"],

            "agreements": committee["strong_agreements"],

            "concerns": committee["concerns"],

            "recommendations": committee["recommendations"],

            "diagnoses": diagnoses,

            "agent_positions": committee["agent_positions"],

            "discussion": committee["discussion"],

            "round_table": committee["round_table"],

            "committee_confidence": committee["committee_confidence"],

            "summary": committee["summary"],

            "confidence": 0.95,

            "coherence": committee["committee_confidence"],
        }
