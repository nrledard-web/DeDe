"""
DeDe - Detector Engine

Coordinates all symbolic detectors.
"""

from detectors.certainty_detector import CertaintyDetector
from detectors.gnosis_detector import GnosisDetector
from detectors.nous_detector import NousDetector
from detectors.reduction_detector import ReductionDetector
from detectors.revisability_detector import RevisabilityDetector
from detectors.mecroyance_detector import MecroyanceDetector
from detectors.cognitive_balance_detector import CognitiveBalanceDetector


class DetectorEngine:

    def __init__(self):

        self.certainty = CertaintyDetector()
        self.gnosis = GnosisDetector()
        self.nous = NousDetector()
        self.reduction = ReductionDetector()
        self.revisability = RevisabilityDetector()
        self.mecroyance = MecroyanceDetector()
        self.balance = CognitiveBalanceDetector()
