"""
DeDe - Mecroyance Detector

Computes symbolic mecroyance indicators directly from text.

Mecroyance is not ignorance.
It appears when certainty and reduction exceed the integrated balance
of articulated knowledge, understanding and revisability.
"""

from typing import Any

from detectors.certainty_detector import CertaintyDetector
from detectors.gnosis_detector import GnosisDetector
from detectors.nous_detector import NousDetector
from detectors.reduction_detector import ReductionDetector
from detectors.revisability_detector import RevisabilityDetector


class MecroyanceDetector:
    """
    Computes mecroyance-related indicators from G, N, D, R and V.
    """

    def __init__(self):
        self.gnosis = GnosisDetector()
        self.nous = NousDetector()
        self.certainty = CertaintyDetector()
        self.reduction = ReductionDetector()
        self.revisability = RevisabilityDetector()

    def analyze(self, text: str) -> dict[str, Any]:
        """
        Analyze text and compute symbolic mecroyance indicators.
        """

        gnosis = self.gnosis.analyze(text)
        nous = self.nous.analyze(text)
        certainty = self.certainty.analyze(text)
        reduction = self.reduction.analyze(text)
        revisability = self.revisability.analyze(text)

        g = gnosis["gnosis_score"]
        n = nous["nous_score"]
        d = certainty["certainty_score"]
        r = reduction["reduction_score"]
        v = revisability["revisability_score"]

        mecroyance_raw = (g + n + v) - (d + r)

        overconfidence = max(0.0, d - (g + n))
        cognitive_closure = max(0.0, d - v)
        forgotten_reduction = reduction["forgotten_reduction"]

        mecroyance_risk = max(
            0.0,
            min(
                1.0,
                (d + r + overconfidence + cognitive_closure - v) / 3,
            ),
        )

        return {
            "scores": {
                "gnosis": g,
                "nous": n,
                "doxa": d,
                "reduction": r,
                "revisability": v,
                "mecroyance_raw": mecroyance_raw,
                "mecroyance_risk": mecroyance_risk,
                "overconfidence": overconfidence,
                "cognitive_closure": cognitive_closure,
            },
            "signals": {
                "gnosis": gnosis,
                "nous": nous,
                "certainty": certainty,
                "reduction": reduction,
                "revisability": revisability,
            },
            "forgotten_reduction": forgotten_reduction,
            "summary": self._summarize(
                mecroyance_risk=mecroyance_risk,
                forgotten_reduction=forgotten_reduction,
                mecroyance_raw=mecroyance_raw,
            ),
        }

    def _summarize(
        self,
        mecroyance_risk: float,
        forgotten_reduction: bool,
        mecroyance_raw: float,
    ) -> str:
        """
        Build a symbolic mecroyance summary.
        """

        if mecroyance_risk > 0.70:
            return "High mecroyance risk detected."

        if forgotten_reduction:
            return "Possible mecroyance through forgotten reduction."

        if mecroyance_risk > 0.40:
            return "Moderate mecroyance risk detected."

        if mecroyance_raw > 0:
            return "Low mecroyance risk: knowledge, understanding and revisability exceed certainty and reduction."

        return "Low to moderate mecroyance risk detected."
