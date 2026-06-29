"""
DeDe - Reduction Estimator
"""

from core.cognitive_workspace import CognitiveWorkspace


class ReductionEstimator:
    """
    Estimates reduction pressure.

    Reduction measures simplification, flattening,
    narrowing of dimensions and possible forgotten reductions.
    """

    name = "reduction"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        text = workspace.text.lower()

        markers = [
            "simplement",
            "juste",
            "rien que",
            "ne fait que",
            "tout est",
            "ce n'est que",
            "réduit à",
            "réduire à",
            "uniquement",
            "seulement",
            "en gros",
            "il suffit de",
            "tout revient à",
            "ce n'est rien d'autre que",
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
                "summary": "Reduction estimated from simplification and narrowing markers.",
            },
        )

        return workspace
