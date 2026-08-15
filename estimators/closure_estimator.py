"""
DeDe - Closure Estimator

Estimates cognitive closure from structural cognitive signals.

Closure measures certainty pressure, reduced revisability
and resistance to alternative interpretations.

The estimator is language-neutral and does not rely on
language-specific certainty markers.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ClosureEstimator:
    """
    Estimates structural cognitive closure.

    Closure pressure rises when:
    - alternatives are scarce;
    - reduction is elevated;
    - integration is weak;
    - grounding is weak;
    - uncertainty is suppressed or poorly represented.
    """

    name = "closure"

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        reduction = self._safe_level(
            workspace.get(
                "reduction"
            )
        )

        integration = self._safe_level(
            workspace.get(
                "integration"
            )
        )

        grounding = self._safe_level(
            workspace.get(
                "grounding"
            )
        )

        semantic = workspace.interpretations.get(
            "semantic_reasoner",
            {},
        )

        if not isinstance(
            semantic,
            dict,
        ):
            semantic = {}

        alternatives = semantic.get(
            "alternative_hypotheses",
            [],
        )

        uncertainties = semantic.get(
            "uncertainties",
            [],
        )

        missing_dimensions = semantic.get(
            "missing_dimensions",
            [],
        )

        if not isinstance(
            alternatives,
            list,
        ):
            alternatives = []

        if not isinstance(
            uncertainties,
            list,
        ):
            uncertainties = []

        if not isinstance(
            missing_dimensions,
            list,
        ):
            missing_dimensions = []

        alternative_presence = min(
            1.0,
            len(
                alternatives
            ) / 3.0,
        )

        alternative_scarcity = (
            1.0
            - alternative_presence
        )

        uncertainty_presence = min(
            1.0,
            len(
                uncertainties
            ) / 3.0,
        )

        missing_dimension_pressure = min(
            1.0,
            len(
                missing_dimensions
            ) / 3.0,
        )

        integration_gap = (
            1.0
            - integration
        )

        grounding_gap = (
            1.0
            - grounding
        )

        score = (
            reduction * 0.25
            + alternative_scarcity * 0.25
            + integration_gap * 0.20
            + grounding_gap * 0.15
            + missing_dimension_pressure * 0.10
            + (
                1.0
                - uncertainty_presence
            ) * 0.05
        )

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        workspace.set(
            self.name,
            score,
            {
                "estimator": self.name,

                "reduction": (
                    reduction
                ),

                "alternative_scarcity": round(
                    alternative_scarcity,
                    3,
                ),

                "integration_gap": round(
                    integration_gap,
                    3,
                ),

                "grounding_gap": round(
                    grounding_gap,
                    3,
                ),

                "missing_dimension_pressure": round(
                    missing_dimension_pressure,
                    3,
                ),

                "uncertainty_presence": round(
                    uncertainty_presence,
                    3,
                ),

                "summary": (
                    "Closure estimated from reduction, alternative scarcity, "
                    "integration, grounding and uncertainty structure rather "
                    "than language-specific certainty markers."
                ),
            },
        )

        return workspace

    @staticmethod
    def _safe_level(
        value: Any,
    ) -> float:

        try:
            level = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                level,
            ),
        )
