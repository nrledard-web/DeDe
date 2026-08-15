"""
DeDe - Reduction Estimator

Estimates reduction pressure from semantic structure.

Reduction is a necessary operation of cognition.
The estimator therefore does not treat simplification itself
as an error.

It looks for structural signs that relevant dimensions,
alternatives or relations may be insufficiently represented.

The calculation is independent of the language used
by the speaker.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ReductionEstimator:
    """
    Estimates structural reduction pressure.

    Reduction pressure rises when:
    - relevant dimensions appear missing;
    - assumptions accumulate;
    - alternatives are scarce;
    - semantic relations are weak;
    - contextual integration is limited.

    It does not decide whether a claim is true or false.
    """

    name = "reduction"

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        # --------------------------------------------------
        # Semantic reasoning
        # --------------------------------------------------

        semantic = workspace.interpretations.get(
            "semantic_reasoner",
            {},
        )

        if not isinstance(
            semantic,
            dict,
        ):
            semantic = {}

        assumptions = semantic.get(
            "assumptions",
            [],
        )

        alternatives = semantic.get(
            "alternative_hypotheses",
            [],
        )

        missing_dimensions = semantic.get(
            "missing_dimensions",
            [],
        )

        uncertainties = semantic.get(
            "uncertainties",
            [],
        )

        causal_links = semantic.get(
            "causal_links",
            [],
        )

        assumptions = self._safe_list(
            assumptions
        )

        alternatives = self._safe_list(
            alternatives
        )

        missing_dimensions = self._safe_list(
            missing_dimensions
        )

        uncertainties = self._safe_list(
            uncertainties
        )

        causal_links = self._safe_list(
            causal_links
        )

        # --------------------------------------------------
        # Semantic representation
        # --------------------------------------------------

        semantic_representation = (
            workspace.interpretations.get(
                "semantic",
                {},
            )
        )

        if not isinstance(
            semantic_representation,
            dict,
        ):
            semantic_representation = {}

        claims = self._safe_list(
            semantic_representation.get(
                "claims",
                [],
            )
        )

        relations = self._safe_list(
            semantic_representation.get(
                "relations",
                [],
            )
        )

        # --------------------------------------------------
        # Structural pressures
        # --------------------------------------------------

        assumption_pressure = min(
            1.0,
            len(assumptions) / 3.0,
        )

        missing_dimension_pressure = min(
            1.0,
            len(missing_dimensions) / 3.0,
        )

        uncertainty_pressure = min(
            1.0,
            len(uncertainties) / 3.0,
        )

        # More alternatives = less reduction pressure.

        alternative_presence = min(
            1.0,
            len(alternatives) / 3.0,
        )

        alternative_scarcity = (
            1.0
            - alternative_presence
        )

        # --------------------------------------------------
        # Relational richness
        # --------------------------------------------------

        structural_items = max(
            1,
            len(claims)
            + len(causal_links),
        )

        relation_density = min(
            1.0,
            len(relations)
            / structural_items,
        )

        relational_scarcity = (
            1.0
            - relation_density
        )

        # --------------------------------------------------
        # Integration context
        # --------------------------------------------------

        integration = self._safe_level(
            workspace.get(
                "integration"
            )
        )

        integration_gap = (
            1.0
            - integration
        )

        # --------------------------------------------------
        # Final reduction pressure
        # --------------------------------------------------

        score = (
            assumption_pressure * 0.15
            + missing_dimension_pressure * 0.30
            + alternative_scarcity * 0.20
            + relational_scarcity * 0.15
            + integration_gap * 0.15
            + uncertainty_pressure * 0.05
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

                "assumption_pressure": round(
                    assumption_pressure,
                    3,
                ),

                "missing_dimension_pressure": round(
                    missing_dimension_pressure,
                    3,
                ),

                "alternative_scarcity": round(
                    alternative_scarcity,
                    3,
                ),

                "relational_scarcity": round(
                    relational_scarcity,
                    3,
                ),

                "integration_gap": round(
                    integration_gap,
                    3,
                ),

                "uncertainty_pressure": round(
                    uncertainty_pressure,
                    3,
                ),

                "assumption_count": (
                    len(assumptions)
                ),

                "missing_dimension_count": (
                    len(missing_dimensions)
                ),

                "alternative_count": (
                    len(alternatives)
                ),

                "relation_count": (
                    len(relations)
                ),

                "summary": (
                    "Reduction estimated from missing dimensions, "
                    "alternative scarcity, relational structure and "
                    "integration rather than language-specific markers."
                ),
            },
        )

        return workspace

    @staticmethod
    def _safe_list(
        value: Any,
    ) -> list[Any]:

        if isinstance(
            value,
            list,
        ):
            return value

        return []

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
