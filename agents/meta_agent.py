"""
Meta Agent

First cognitive committee orchestrator.
"""

from core.shared_workspace import SharedCognitiveWorkspace


class MetaAgent:

    name = "meta"

    def analyze(
        self,
        workspace: SharedCognitiveWorkspace,
    ):

        observations = workspace.get_all()

        agreements = []
        concerns = []

        for obs in observations:

            if obs.confidence >= 0.70:
                agreements.append(obs.agent)

            if obs.confidence <= 0.40:
                concerns.append(obs.agent)

        return {
            "agent": "meta",
            "committee_size": len(observations),
            "agreements": agreements,
            "concerns": concerns,
            "summary": (
                f"{len(observations)} cognitive agents participated."
            ),
        }
