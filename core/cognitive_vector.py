"""
DeDe - Cognitive Vector

Represents the fundamental cognitive state vector used by DeDe.

All future detectors, gauges and cognitive modules should progressively
influence this vector instead of directly computing final conclusions.
"""

from dataclasses import dataclass


@dataclass
class CognitiveVector:
    """
    Fundamental cognitive vector.

    G = Gnosis
    N = Nous
    D = Doxa
    R = Reduction
    V = Revisability
    """

    gnosis: float = 0.0
    nous: float = 0.0
    doxa: float = 0.0
    reduction: float = 0.0
    revisability: float = 0.0

    def clamp(self) -> "CognitiveVector":
        """
        Clamp every dimension between 0 and 1.
        """

        self.gnosis = self._clamp(self.gnosis)
        self.nous = self._clamp(self.nous)
        self.doxa = self._clamp(self.doxa)
        self.reduction = self._clamp(self.reduction)
        self.revisability = self._clamp(self.revisability)

        return self

    def apply_delta(
        self,
        gnosis: float = 0.0,
        nous: float = 0.0,
        doxa: float = 0.0,
        reduction: float = 0.0,
        revisability: float = 0.0,
    ) -> "CognitiveVector":
        """
        Apply a cognitive influence to the vector.
        """

        self.gnosis += gnosis
        self.nous += nous
        self.doxa += doxa
        self.reduction += reduction
        self.revisability += revisability

        return self.clamp()

    def to_dict(self) -> dict:
        """
        Convert the vector into a dictionary.
        """

        return {
            "gnosis": self.gnosis,
            "nous": self.nous,
            "doxa": self.doxa,
            "reduction": self.reduction,
            "revisability": self.revisability,
        }

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))
