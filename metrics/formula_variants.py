"""
DeDe - Formula Variants

Defines the main variants of DeDe's cognitive mechanics formulas.

These formulas are not detectors.
They express different theoretical configurations of mecroyance,
certainty pressure, reduction pressure and cognitive balance.
"""

from typing import Any


class FormulaVariants:
    """
    Computes the main formula variants used by DeDe.
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

        m0_base = (g + n) - d
        m1_revisable = (g + n + v) - d
        m2_reduction_aware = (g + n + v) - (d + r)

        surconfidence = d - (g + n)
        cognitive_closure = d - v
        forgotten_reduction = r - v

        grounding = g + n + v
        closure_pressure = d + r
        cognitive_balance = grounding - closure_pressure

        return {
            "inputs": {
                "G": g,
                "N": n,
                "D": d,
                "R": r,
                "V": v,
            },
            "mecroyance_variants": {
                "M0_base": m0_base,
                "M1_revisable": m1_revisable,
                "M2_reduction_aware": m2_reduction_aware,
            },
            "pressure_variants": {
                "surconfidence": surconfidence,
                "cognitive_closure": cognitive_closure,
                "forgotten_reduction": forgotten_reduction,
            },
            "balance_variants": {
                "grounding": grounding,
                "closure_pressure": closure_pressure,
                "cognitive_balance": cognitive_balance,
            },
        }

    def _clamp(self, value: float | None) -> float:
        if value is None:
            return 0.0
        return max(0.0, min(1.0, float(value)))
