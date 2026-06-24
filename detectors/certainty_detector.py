"""
DeDe - Certainty Detector

Detects linguistic markers of certainty, rigidity and epistemic closure.
"""

from typing import Any


class CertaintyDetector:
    """
    Detects explicit certainty and nuance markers in a text.
    """

    certainty_markers = [
        "always",
        "never",
        "obviously",
        "clearly",
        "undeniable",
        "certain",
        "certainly",
        "definitely",
        "absolutely",
        "impossible",
        "cannot",
        "must",
        "everyone knows",
        "no one can deny",
        "without doubt",
    ]

    nuance_markers = [
        "maybe",
        "perhaps",
        "possibly",
        "possible",
        "might",
        "could",
        "sometimes",
        "it depends",
        "uncertain",
        "hypothesis",
        "open question",
        "to verify",
    ]

    def analyze(self, text: str) -> dict[str, Any]:
        normalized = text.lower()

        certainty_hits = self._find_markers(normalized, self.certainty_markers)
        nuance_hits = self._find_markers(normalized, self.nuance_markers)

        certainty_score = min(
            1.0,
            max(
                0.0,
                0.30
                + len(certainty_hits) * 0.10
                - len(nuance_hits) * 0.06,
            ),
        )

        closure_risk = certainty_score > 0.75 and len(nuance_hits) == 0

        return {
            "certainty_hits": certainty_hits,
            "nuance_hits": nuance_hits,
            "certainty_score": certainty_score,
            "closure_risk": closure_risk,
            "summary": (
                "High certainty with low nuance detected."
                if closure_risk
                else "Certainty appears moderated by nuance or remains below closure threshold."
            ),
        }

    def _find_markers(self, text: str, markers: list[str]) -> list[str]:
        return [marker for marker in markers if marker in text]
