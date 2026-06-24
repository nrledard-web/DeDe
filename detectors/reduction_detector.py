"""
DeDe - Reduction Detector

Detects cognitive reductions, oversimplifications and missing dimensions.
"""

from typing import Any


class ReductionDetector:
    """
    Detects possible cognitive reductions in reasoning.
    """

    generalization_markers = [
        "all",
        "every",
        "everyone",
        "everything",
        "always",
        "never",
        "none",
        "nobody",
        "only",
        "entirely",
    ]

    simplification_markers = [
        "because",
        "therefore",
        "simply",
        "just",
        "only because",
        "nothing but",
        "explains everything",
    ]

    limitation_markers = [
        "however",
        "although",
        "except",
        "unless",
        "on the other hand",
        "depends",
        "under certain conditions",
        "one possibility",
        "among others",
    ]

    def analyze(self, text: str) -> dict[str, Any]:

        text = text.lower()

        generalizations = self._find(text, self.generalization_markers)
        simplifications = self._find(text, self.simplification_markers)
        limitations = self._find(text, self.limitation_markers)

        reduction_score = min(
            1.0,
            (
                len(generalizations) * 0.10
                + len(simplifications) * 0.15
                - len(limitations) * 0.08
            )
            + 0.25,
        )

        reduction_score = max(0.0, reduction_score)

        forgotten_reduction = (
            reduction_score > 0.70
            and len(limitations) == 0
        )

        return {
            "generalizations": generalizations,
            "simplifications": simplifications,
            "limitations": limitations,
            "reduction_score": reduction_score,
            "forgotten_reduction": forgotten_reduction,
            "summary": (
                "Possible forgotten reduction detected."
                if forgotten_reduction
                else "No major forgotten reduction detected."
            ),
        }

    def _find(self, text: str, markers: list[str]) -> list[str]:
        return [m for m in markers if m in text]
