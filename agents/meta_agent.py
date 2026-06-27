"""
Meta Agent
Cognitive Committee
"""

from core.shared_workspace import SharedCognitiveWorkspace


class MetaAgent:

    def analyze(
        self,
        workspace: SharedCognitiveWorkspace,
    ):

        observations = workspace.get_all()

        agreements = []
        disagreements = []
        concerns = []
        recommendations = []

        for obs in observations:

            if obs.confidence >= 0.70:
                agreements.append(obs.agent)

            if obs.confidence <= 0.40:
                concerns.append(obs.agent)

            if "revision" in obs.observation.lower():
                recommendations.append(
                    "Cognitive revision recommended."
                )

            if "grounding" in obs.observation.lower():
                recommendations.append(
                    "Increase factual grounding."
                )

            if "reduction" in obs.observation.lower():
                recommendations.append(
                    "Check for forgotten reductions."
                )

        summary = (
            f"{len(observations)} cognitive agents participated. "
            f"{len(agreements)} strong agreements. "
            f"{len(concerns)} low-confidence observations."
        )

        return {

            "agent": "meta",

            "committee_size": len(observations),

            "agreements": agreements,

            "concerns": concerns,

            "recommendations": sorted(
                set(recommendations)
            ),

            "summary": summary,

            "confidence": 0.95,

            "coherence": (
                len(agreements)
                / max(1, len(observations))
            ),
        }
