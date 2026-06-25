"""
DeDe - Cognitive Metrics

Pure mathematical definitions for DeDe's central cognitive mechanics.

This module does not detect markers.
It only computes relationships between Gnosis, Nous, Doxa,
Reduction and Revisability.
"""

from typing import Any


class CognitiveMetrics:
    """
    Computes DeDe's core cognitive formulas.
    """

    def compute(
        self,
        gnosis: float,
        nous: float,
        doxa: float,
        reduction: float,
        revisability: float,
    ) -> dict[str, Any]:
        g = self._clamp(gnosis)
        n = self._clamp(nous)
        d = self._clamp(doxa)
        r = self._clamp(reduction)
        v = self._clamp(revisability)

        grounding = g + n + v
        closure_pressure = d + r

        mecroyance_raw = grounding - closure_pressure
        mecroyance_pressure = closure_pressure - grounding

        surconfidence = max(0.0, d - (g + n))
        cognitive_closure = max(0.0, d - v)
        forgotten_reduction_pressure = max(0.0, r - v)

        cognitive_balance = grounding - closure_pressure
        balance_ratio = grounding / (closure_pressure + 0.01)

        mecroyance_risk = self._clamp(
            (mecroyance_pressure + surconfidence + cognitive_closure + forgotten_reduction_pressure)
            / 4
        )

        return {
            "inputs": {
                "gnosis": g,
                "nous": n,
                "doxa": d,
                "reduction": r,
                "revisability": v,
            },
            "core": {
                "grounding": grounding,
                "closure_pressure": closure_pressure,
                "mecroyance_raw": mecroyance_raw,
                "mecroyance_pressure": mecroyance_pressure,
                "mecroyance_risk": mecroyance_risk,
                "cognitive_balance": cognitive_balance,
                "balance_ratio": balance_ratio,
            },
            "derived": {
                "surconfidence": surconfidence,
                "cognitive_closure": cognitive_closure,
                "forgotten_reduction_pressure": forgotten_reduction_pressure,
            },
            "diagnosis": self._diagnose(
                mecroyance_risk=mecroyance_risk,
                cognitive_balance=cognitive_balance,
                surconfidence=surconfidence,
                cognitive_closure=cognitive_closure,
                forgotten_reduction_pressure=forgotten_reduction_pressure,
            ),
        }

    def _clamp(self, value: float | None) -> float:
        if value is None:
            return 0.0
        return max(0.0, min(1.0, float(value)))

    def _diagnose(
        self,
        mecroyance_risk: float,
        cognitive_balance: float,
        surconfidence: float,
        cognitive_closure: float,
        forgotten_reduction_pressure: float,
    ) -> str:
        if mecroyance_risk >= 0.70:
            return "High mecroyance pressure."

        if cognitive_closure >= 0.40:
            return "Significant cognitive closure."

        if surconfidence >= 0.40:
            return "Unsupported certainty exceeds grounding."

        if forgotten_reduction_pressure >= 0.40:
            return "Forgotten reduction pressure detected."

        if cognitive_balance >= 0:
            return "Grounding exceeds closure pressure."

        return "Mild cognitive imbalance."
