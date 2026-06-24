"""
DeDe - Detector Engine

Coordinates all symbolic cognitive detectors.
"""

from typing import Any

from core.cognitive_state import CognitiveState

from detectors.certainty_detector import CertaintyDetector
from detectors.gnosis_detector import GnosisDetector
from detectors.nous_detector import NousDetector
from detectors.reduction_detector import ReductionDetector
from detectors.revisability_detector import RevisabilityDetector
from detectors.mecroyance_detector import MecroyanceDetector
from detectors.cognitive_balance_detector import CognitiveBalanceDetector


class DetectorEngine:
    """
    Central coordinator for all symbolic cognitive detectors.
    """

    def __init__(self):
        self.certainty = CertaintyDetector()
        self.gnosis = GnosisDetector()
        self.nous = NousDetector()
        self.reduction = ReductionDetector()
        self.revisability = RevisabilityDetector()
        self.mecroyance = MecroyanceDetector()
        self.balance = CognitiveBalanceDetector()

    def analyze(self, state: CognitiveState) -> dict[str, Any]:
        """
        Run all symbolic detectors and return a unified signal report.
        """

        text = state.user_input

        certainty = self.certainty.analyze(text)
        gnosis = self.gnosis.analyze(text)
        nous = self.nous.analyze(text)
        reduction = self.reduction.analyze(text)
        revisability = self.revisability.analyze(text)
        mecroyance = self.mecroyance.analyze(text)

        balance = self.balance.analyze(
            gnosis=gnosis["gnosis_score"],
            nous=nous["nous_score"],
            doxa=certainty["certainty_score"],
            reduction=reduction["reduction_score"],
            revisability=revisability["revisability_score"],
        )

        return {
            "certainty": certainty,
            "gnosis": gnosis,
            "nous": nous,
            "reduction": reduction,
            "revisability": revisability,
            "mecroyance": mecroyance,
            "balance": balance,
        }
