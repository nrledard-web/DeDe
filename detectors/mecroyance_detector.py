"""
DeDe - Mecroyance Detector

Computes the first symbolic mecroyance indicators from cognitive signals.

Mecroyance is not ignorance.
It appears when certainty exceeds the integrated balance of articulated
knowledge, understanding and revisability.
"""

from typing import Any

from detectors.certainty_detector import CertaintyDetector
from detectors.reduction_detector import ReductionDetector
from detectors.revisability_detector import RevisabilityDetector


class MecroyanceDetector:
    """
    Computes symbolic mecroyance-related indicators.
    """

    def __init__(self):
        self.certainty_detector = CertaintyDetector()
        self.reduction_detector = ReductionDetector()
        self.revisability_detector = RevisabilityDetector()

    def analyze(
        self,
        text: str,
        gnosis_level: float = 0.0,
        nous_level: float = 0.0,
    ) -> dict[str, Any]:
        certainty = self.certainty_detector.analyze(text)
        reduction = self.reduction_detector.analyze(text)
        revisability = self.revisability_detector.analyze(text)

        d = certainty["certainty_score"]
        r = reduction["reduction_score"]
        v = revisability["revisability_score"]

        g = gnosis_level
        n = nous_level

        mecroyance_raw = (g + n + v) - (d + r)

        overconfidence = max(0.0, d - (g + n))
        cognitive_closure = max(0.0, d - v)
        forgotten_reduction = reduction["forgotten_reduction"]

        mecroyance_risk = max(
            0.0,
            min(
                1.0,
                (d + r + overconfidence + cognitive_closure) / 4,
            ),
        )

        return {
            "gnosis_level": g,
            "nous_level": n,
            "doxa_level": d,
            "reduction_level": r,
            "revisability_level": v,
            "mecroyance_raw": mecroyance_raw,
            "mecroyance_risk": mecroyance_risk,
            "overconfidence": overconfidence,
            "cognitive_closure": cognitive_closure,
            "forgotten_reduction": forgotten_reduction,
            "certainty": certainty,
            "reduction": reduction,
            "revisability": revisability,
            "summary": self._summarize(mecroyance_risk, forgotten_reduction),
        }

    def _summarize(
        self,
        mecroyance_risk: float,
        forgotten_reduction: bool,
    ) -> str:
        if mecroyance_risk > 0.70:
            return "High mecroyance risk detected."
        if forgotten_reduction:
            return "Possible mecroyance through forgotten reduction."
        if mecroyance_risk > 0.40:
            return "Moderate mecroyance risk detected."
        return "Low mecroyance risk detected."
