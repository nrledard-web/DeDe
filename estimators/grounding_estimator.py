"""
DeDe - Grounding Estimator
"""

from core.cognitive_workspace import CognitiveWorkspace


class GroundingEstimator:
    """
    Estimates factual grounding.

    Grounding combines:

    - linguistic evidence markers
    - available knowledge
    - source confidence

    Future versions will also integrate:
    - Web search
    - LLM providers
    - PDF knowledge
    - Scientific databases
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

        hits = [
            marker
            for marker in markers
            if marker in text
        ]

        linguistic_score = min(
            1.0,
            0.20 + len(hits) * 0.08,
        )

        # ----------------------------------------
        # Knowledge contribution
        # ----------------------------------------

        knowledge = workspace.interpretations.get(
            "knowledge",
            {},
        )

        knowledge_found = knowledge.get(
            "found",
            False,
        )

        knowledge_confidence = knowledge.get(
            "confidence",
            0.0,
        )

        if knowledge_found:

            knowledge_bonus = (
                0.25 * knowledge_confidence
            )

        else:

            knowledge_bonus = 0.0

        score = min(
            1.0,
            linguistic_score + knowledge_bonus,
        )

        workspace.set(
            self.name,
            score,
            {
                "estimator": self.name,

                "hits": hits,

                "hit_count": len(hits),

                "linguistic_score": linguistic_score,

                "knowledge_found": knowledge_found,

                "knowledge_confidence": knowledge_confidence,

                "knowledge_bonus": knowledge_bonus,

                "summary":
                    (
                        "Grounding estimated from linguistic "
                        "markers and available knowledge."
                    ),
            },
        )

        return workspace
