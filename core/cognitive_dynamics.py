"""
Cognitive Dynamics

Defines abstract cognitive dynamics used by DeDe to transform
signals into structural influences on Gnosis, Nous, Doxa,
Reduction and Revisability.

This layer does not replace agents.
It provides deeper cognitive forces that agents and committees
can later use without depending directly on language markers.
"""

from dataclasses import dataclass


@dataclass
class CognitiveDynamicResult:
    name: str
    value: float
    affects: dict[str, float]
    description: str


class BaseCognitiveDynamic:
    """
    Base class for cognitive dynamics.
    A dynamic receives abstract signals and returns a value
    between 0.0 and 1.0 with its influence on cognitive dimensions.
    """

    name = "base_dynamic"

    def evaluate(
        self,
        signals: dict,
    ) -> CognitiveDynamicResult:
        return CognitiveDynamicResult(
            name=self.name,
            value=0.0,
            affects={},
            description="No dynamic effect detected.",
        )


class ClosureDynamic(BaseCognitiveDynamic):
    """
    Measures how strongly a discourse reduces the space
    of possible revision, alternatives or uncertainty.
    """

    name = "closure"

    def evaluate(
        self,
        signals: dict,
    ) -> CognitiveDynamicResult:
        value = signals.get(
            "closure_signal",
            0.0,
        )

        value = self._clamp(value)

        return CognitiveDynamicResult(
            name=self.name,
            value=value,
            affects={
                "doxa": value * 0.20,
                "revisability": -value * 0.15,
                "nous": -value * 0.05,
            },
            description=(
                "Closure increases Doxa pressure, reduces revisability "
                "and may weaken integrated understanding."
            ),
        )

    def _clamp(
        self,
        value: float,
    ) -> float:
        return max(
            0.0,
            min(
                1.0,
                value,
            ),
        )


class IntegrationDynamic(BaseCognitiveDynamic):
    """
    Measures whether the elements of a discourse are genuinely
    connected, contextualized and conceptually integrated.
    """

    name = "integration"

    def evaluate(
        self,
        signals: dict,
    ) -> CognitiveDynamicResult:
        value = signals.get(
            "integration_signal",
            0.0,
        )

        value = self._clamp(value)

        return CognitiveDynamicResult(
            name=self.name,
            value=value,
            affects={
                "nous": value * 0.25,
                "revisability": value * 0.10,
                "reduction": -value * 0.10,
            },
            description=(
                "Integration strengthens Nous, supports revisability "
                "and reduces reduction pressure."
            ),
        )

    def _clamp(
        self,
        value: float,
    ) -> float:
        return max(
            0.0,
            min(
                1.0,
                value,
            ),
        )


class ReductionDynamic(BaseCognitiveDynamic):
    """
    Measures whether a discourse removes dimensions, alternatives
    or contextual complexity without acknowledging the reduction.
    """

    name = "reduction"

    def evaluate(
        self,
        signals: dict,
    ) -> CognitiveDynamicResult:
        value = signals.get(
            "reduction_signal",
            0.0,
        )

        value = self._clamp(value)

        return CognitiveDynamicResult(
            name=self.name,
            value=value,
            affects={
                "reduction": value * 0.25,
                "nous": -value * 0.10,
                "doxa": value * 0.05,
            },
            description=(
                "Reduction increases reduction pressure, weakens Nous "
                "and may slightly increase Doxa through simplification."
            ),
        )

    def _clamp(
        self,
        value: float,
    ) -> float:
        return max(
            0.0,
            min(
                1.0,
                value,
            ),
        )


class CognitiveDynamicsEngine:
    """
    Runs cognitive dynamics and returns their combined influence.
    """

    def __init__(self):
        self.dynamics = [
            ClosureDynamic(),
            IntegrationDynamic(),
            ReductionDynamic(),
        ]

    def evaluate(
        self,
        signals: dict,
    ) -> dict:
        results = []
        combined_affects = {
            "gnosis": 0.0,
            "nous": 0.0,
            "doxa": 0.0,
            "reduction": 0.0,
            "revisability": 0.0,
        }

        for dynamic in self.dynamics:
            result = dynamic.evaluate(
                signals
            )

            results.append(
                result
            )

            for key, value in result.affects.items():
                combined_affects[key] += value

        return {
            "results": [
                {
                    "name": result.name,
                    "value": result.value,
                    "affects": result.affects,
                    "description": result.description,
                }
                for result in results
            ],
            "combined_affects": combined_affects,
        }
