"""
Cognitive Dynamics

Defines abstract cognitive dynamics used by DeDe to transform
signals into structural cognitive values.

Dynamics do not decide how they affect Gnosis, Nous, Doxa,
Reduction or Revisability.

They only produce normalized cognitive forces.
Agents decide how to use those forces.
"""

from dataclasses import dataclass


@dataclass
class CognitiveDynamicResult:
    name: str
    value: float
    description: str


class BaseCognitiveDynamic:
    """
    Base class for cognitive dynamics.
    A dynamic receives abstract signals and returns a value
    between 0.0 and 1.0.
    """

    name = "base_dynamic"

    def evaluate(
        self,
        signals: dict,
    ) -> CognitiveDynamicResult:
        return CognitiveDynamicResult(
            name=self.name,
            value=0.0,
            description="No dynamic effect detected.",
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


class GroundingDynamic(BaseCognitiveDynamic):
    """
    Measures how strongly a discourse is constrained by factual,
    empirical, contextual or verifiable grounding.
    """

    name = "grounding"

    def evaluate(
        self,
        signals: dict,
    ) -> CognitiveDynamicResult:
        value = signals.get(
            "grounding_signal",
            0.0,
        )

        value = self._clamp(value)

        return CognitiveDynamicResult(
            name=self.name,
            value=value,
            description=(
                "Grounding measures how strongly a discourse remains "
                "constrained by facts, sources, evidence, context or verification."
            ),
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
            description=(
                "Closure measures the reduction of open alternatives, "
                "revision space and uncertainty tolerance."
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
            description=(
                "Integration measures how strongly facts, context "
                "and meaning are connected."
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
            description=(
                "Reduction measures how much complexity, alternatives "
                "or missing dimensions disappear from the discourse."
            ),
        )


class CognitiveDynamicsEngine:
    """
    Runs cognitive dynamics and returns their normalized values.
    """

    def __init__(self):
        self.dynamics = [
            GroundingDynamic(),
            ClosureDynamic(),
            IntegrationDynamic(),
            ReductionDynamic(),
        ]

    def evaluate(
        self,
        signals: dict,
    ) -> dict:
        results = []

        for dynamic in self.dynamics:
            result = dynamic.evaluate(
                signals
            )

            results.append(
                result
            )

        return {
            "results": [
                {
                    "name": result.name,
                    "value": result.value,
                    "description": result.description,
                }
                for result in results
            ],
            "values": {
                result.name: result.value
                for result in results
            },
        }
