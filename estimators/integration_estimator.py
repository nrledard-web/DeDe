"""
DeDe - Integration Estimator
"""

from core.cognitive_workspace import CognitiveWorkspace


class IntegrationEstimator:
    """
    Estimates conceptual integration.

    Integration combines linguistic structure with conceptual structure.
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

        hits = [
            marker
            for marker in markers
            if marker in text
        ]

        linguistic_score = min(
            1.0,
            0.20 + len(hits) * 0.08,
        )

        concept_count = workspace.get("concept_count") or 0
        relation_count = workspace.get("relation_count") or 0
        concept_density = workspace.get("concept_density") or 0.0

        concept_bonus = min(
            0.40,
            concept_count * 0.03
            + relation_count * 0.02
            + concept_density * 0.10,
        )

        score = min(
            1.0,
            linguistic_score + concept_bonus,
        )

        workspace.set(
            self.name,
            score,
            {
                "estimator": self.name,
                "hits": hits,
                "hit_count": len(hits),
                "linguistic_score": linguistic_score,
                "concept_count": concept_count,
                "relation_count": relation_count,
                "concept_density": concept_density,
                "concept_bonus": concept_bonus,
                "summary": (
                    "Integration estimated from linguistic "
                    "and conceptual structure."
                ),
            },
        )

        return workspace
