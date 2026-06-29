"""
DeDe - Closure Estimator
"""

from core.cognitive_workspace import CognitiveWorkspace


class ClosureEstimator:
    """
    Estimates cognitive closure.

    Closure measures certainty pressure, reduced revisability,
    and resistance to alternative interpretations.
    """

    name = "closure"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        text = workspace.text.lower()

        markers = [
            "évident",
            "évidente",
            "certain",
            "certaine",
            "impossible",
            "toujours",
            "jamais",
            "personne ne peut nier",
            "sans aucun doute",
            "la vérité",
            "forcément",
            "nécessairement",
            "il est clair que",
            "tout le monde sait",
            "aucune alternative",
            "indiscutable",
            "incontestable",
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
                "summary": "Closure estimated from certainty and non-revisability markers.",
            },
        )

        return workspace
