"""
DeDe - Cognitive Balance Detector

Computes the balance between knowledge, understanding, revisability,
certainty and reduction.
"""

from typing import Any


class CognitiveBalanceDetector:
    """
    Evaluates the global cognitive balance of a reasoning state.
    """

    def analyze(
        self,
        gnosis: float,
        nous: float,
        doxa: float,
        reduction: float,
        revisability: float,
    ) -> dict[str, Any]:
        """
        Compute cognitive balance indicators.
        """

        grounding = gnosis + nous + revisability
        closure_pressure = doxa + reduction

        balance_raw = grounding - closure_pressure

        balance_ratio = grounding / (closure_pressure + 0.01)

        overclosure = max(0.0, closure_pressure - grounding)

        unsupported_certainty = max(0.0, doxa - (gnosis + nous))

        forgotten_reduction_pressure = max(0.0, reduction - revisability)

        if balance_raw >= 0.50:
            diagnosis = "Cognitively balanced or strongly revisable."
        elif balance_raw >= 0.0:
            diagnosis = "Moderately balanced cognitive state."
        elif overclosure < 0.40:
            diagnosis = "Mild cognitive closure pressure."
        else:
            diagnosis = "Strong cognitive imbalance: certainty and reduction exceed grounding."

        return {
            "grounding": grounding,
            "closure_pressure": closure_pressure,
            "balance_raw": balance_raw,
            "balance_ratio": balance_ratio,
            "overclosure": overclosure,
            "unsupported_certainty": unsupported_certainty,
            "forgotten_reduction_pressure": forgotten_reduction_pressure,
            "diagnosis": diagnosis,
        }
