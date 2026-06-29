"""
DeDe - Grounding Estimator
"""

from core.cognitive_workspace import CognitiveWorkspace


class GroundingEstimator:
    """
    Estimates factual grounding.

    Grounding measures sources, evidence, facts,
    verification markers and concrete anchors.
    """

    name = "grounding"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        text = workspace.text.lower()

        markers = [
            "source",
            "preuve",
            "preuves",
            "donnée",
            "données",
            "étude",
            "études",
            "document",
            "documents",
            "selon",
            "vérifier",
            "vérification",
            "factuel",
            "factuelle",
            "citation",
            "exemple",
            "exemples",
            "observation",
            "observations",
            "mesure",
            "mesures",
            "statistique",
            "statistiques",
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
                "summary": "Grounding estimated from factual and evidential markers.",
            },
        )

        return workspace
