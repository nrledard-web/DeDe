"""
DeDe - Revisability Detector

Detects markers of epistemic openness, uncertainty,
self-correction and willingness to revise a belief.
"""

from typing import Any


class RevisabilityDetector:
    """
    Detects whether a statement remains cognitively revisable.
    """

    revisability_markers = [
        "i may be wrong",
        "i could be wrong",
        "maybe",
        "perhaps",
        "possibly",
        "it seems",
        "it appears",
        "as far as i know",
        "according to current evidence",
        "based on available data",
        "unless new evidence appears",
        "open question",
        "to verify",
        "could change",
        "may evolve",
        "i would revise",
        "subject to revision",
    ]

    closure_markers = [
        "no debate",
        "cannot be questioned",
        "case closed",
        "end of discussion",
        "obviously true",
        "undeniable",
        "impossible to deny",
        "everyone knows",
        "there is no alternative",
    ]

    def analyze(self, text: str) -> dict[str, Any]:
        normalized = text.lower()

        revisability_hits = self._find(normalized, self.revisability_markers)
        closure_hits = self._find(normalized, self.closure_markers)

        revisability_score = min(
            1.0,
            max(
                0.0,
                0.35
                + len(revisability_hits) * 0.12
                - len(closure_hits) * 0.10,
            ),
        )

        low_revisability = revisability_score < 0.35 and len(closure_hits) > 0

        return {
            "revisability_hits": revisability_hits,
            "closure_hits": closure_hits,
            "revisability_score": revisability_score,
            "low_revisability": low_revisability,
            "summary": (
                "Low revisability detected."
                if low_revisability
                else "The statement retains some degree of cognitive revisability."
            ),
        }

    def _find(self, text: str, markers: list[str]) -> list[str]:
        return [marker for marker in markers if marker in text]
