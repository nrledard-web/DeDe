"""
DeDe - Detector Engine

Coordinates all symbolic cognitive detectors, the cognitive vector
and core cognitive metrics.
"""

from typing import Any

from core.cognitive_state import CognitiveState
from core.cognitive_vector import CognitiveVector
from processing.text_preprocessor import TextPreprocessor

from detectors.certainty_detector import CertaintyDetector
from detectors.gnosis_detector import GnosisDetector
from detectors.nous_detector import NousDetector
from detectors.reduction_detector import ReductionDetector
from detectors.revisability_detector import RevisabilityDetector
from detectors.mecroyance_detector import MecroyanceDetector
from detectors.cognitive_balance_detector import CognitiveBalanceDetector

from metrics.cognitive_metrics import CognitiveMetrics


class DetectorEngine:
    """
    Central coordinator for symbolic detectors and cognitive mechanics.
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()

        self.certainty = CertaintyDetector()
        self.gnosis = GnosisDetector()
        self.nous = NousDetector()
        self.reduction = ReductionDetector()
        self.revisability = RevisabilityDetector()
        self.mecroyance = MecroyanceDetector()
        self.balance = CognitiveBalanceDetector()
        self.metrics = CognitiveMetrics()

    def analyze(self, state: CognitiveState) -> dict[str, Any]:
        """
        Run detectors, build a cognitive vector and compute metrics.
        """

        processed = self.preprocessor.process(state.user_input)
        text = processed.normalized_text

        certainty = self.certainty.analyze(text)
        gnosis = self.gnosis.analyze(text)
        nous = self.nous.analyze(text)
        reduction = self.reduction.analyze(text)
        revisability = self.revisability.analyze(text)
        mecroyance = self.mecroyance.analyze(text)

        vector = CognitiveVector(
            gnosis=gnosis["gnosis_score"],
            nous=nous["nous_score"],
            doxa=certainty["certainty_score"],
            reduction=reduction["reduction_score"],
            revisability=revisability["revisability_score"],
        ).clamp()

        balance = self.balance.analyze(
            gnosis=vector.gnosis,
            nous=vector.nous,
            doxa=vector.doxa,
            reduction=vector.reduction,
            revisability=vector.revisability,
        )

        metrics = self.metrics.compute(
            gnosis=vector.gnosis,
            nous=vector.nous,
            doxa=vector.doxa,
            reduction=vector.reduction,
            revisability=vector.revisability,
        )

        return {
            "processed_text": {
                "char_count": processed.char_count,
                "word_count": processed.word_count,
                "sentence_count": processed.sentence_count,
                "paragraph_count": processed.paragraph_count,
                "unique_word_count": processed.unique_word_count,
                "lexical_diversity": processed.lexical_diversity,
            },
            "cognitive_vector": vector.to_dict(),
            "certainty": certainty,
            "gnosis": gnosis,
            "nous": nous,
            "reduction": reduction,
            "revisability": revisability,
            "mecroyance": mecroyance,
            "balance": balance,
            "metrics": metrics,
        }
