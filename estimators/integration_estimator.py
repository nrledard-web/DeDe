"""
DeDe - Integration Estimator
"""

from core.cognitive_workspace import CognitiveWorkspace


class IntegrationEstimator:
    """
    Estimates conceptual integration.

    Integration measures relation, nuance, context,
    synthesis and explanatory structure.
    """

    name = "integration"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        text = workspace.text.lower()

        markers = [
            "donc",
            "car",
            "parce que",
            "cependant",
            "mais",
            "en revanche",
            "toutefois",
            "ainsi",
            "implique",
            "relation",
            "relations",
            "contexte",
            "nuance",
            "nuances",
            "hypothèse",
            "hypothèses",
            "structure",
            "cohérence",
            "articule",
            "articulation",
            "synthèse",
        ]

        hits = [marker for marker in markers if marker in text]
        score = min(1.0, 0.20 + len(hits) * 0.08)

        workspace.set(
            self.name,
            score,
            {
                "estimator": self.name,
                "hits": hits,
                "hit_count": len(hits),
                "summary": "Integration estimated from relational, contextual and synthetic markers.",
            },
        )

        return workspace
