"""
DeDe - Reduction Agent

Phase 3 cognitive agent.

The Reduction Agent reads shared cognitive variables and semantic
structures from the CognitiveWorkspace to interpret reduction pressure,
hidden assumptions, missing dimensions, excessive reduction and
forgotten reduction.

Reduction itself is necessary to cognition.
The risk appears when the reduction becomes excessive, too narrow,
or forgotten as a reduction of reality.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ReductionAgent:
    """
    Cognitive agent responsible for interpreting reduction pressure.

    The agent distinguishes:

    - ordinary reduction
    - moderate reduction
    - excessive reduction
    - forgotten reduction

    Reduction is not treated as an error in itself.
    """

    name = "reduction"

    def analyze(
        self,
        workspace: CognitiveWorkspace,
    ) -> dict[str, Any]:
        """
        Interpret reduction pressure from the shared workspace.
        """

        grounding = workspace.get(
            "grounding"
        )

        integration = workspace.get(
            "integration"
        )

        closure = workspace.get(
            "closure"
        )

        reduction = workspace.get(
            "reduction"
        )

        # --------------------------------------------------
        # Defensive normalization
        # --------------------------------------------------

        grounding = self._safe_level(
            grounding
        )

        integration = self._safe_level(
            integration
        )

        closure = self._safe_level(
            closure
        )

        reduction = self._safe_level(
            reduction
        )

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

        uncertainties = semantic.get(
            "uncertainties",
            [],
        )

        alternative_hypotheses = semantic.get(
            "alternative_hypotheses",
            [],
        )

        if not isinstance(
            assumptions,
            list,
        ):
            assumptions = []

        if not isinstance(
            uncertainties,
            list,
        ):
            uncertainties = []

        if not isinstance(
            alternative_hypotheses,
            list,
        ):
            alternative_hypotheses = []

        assumption_count = len(
            assumptions
        )

        uncertainty_count = len(
            uncertainties
        )

        alternative_count = len(
            alternative_hypotheses
        )

        # --------------------------------------------------
        # Existing semantic reduction pressure
        # --------------------------------------------------

        semantic_reduction_pressure = max(
            0.0,
            min(
                0.25,
                (
                    assumption_count * 0.08
                    + max(
                        0,
                        2 - alternative_count,
                    ) * 0.04
                    - uncertainty_count * 0.03
                ),
            ),
        )

        # --------------------------------------------------
        # Hidden assumption pressure
        # --------------------------------------------------

        hidden_assumption_pressure = max(
            0.0,
            min(
                1.0,
                (
                    reduction * 0.55
                    + closure * 0.25
                    - integration * 0.20
                    - grounding * 0.10
                    + 0.20
                    + semantic_reduction_pressure
                ),
            ),
        )

        possible_hidden_assumptions = (
            hidden_assumption_pressure
            >= 0.60
        )

        # --------------------------------------------------
        # Alternative scarcity
        # --------------------------------------------------
        #
        # Alternatives help preserve cognitive breadth.
        #
        # 0 alternatives -> high scarcity
        # 3+ alternatives -> no scarcity pressure
        # --------------------------------------------------

        alternative_scarcity = max(
            0.0,
            min(
                1.0,
                (
                    1.0
                    - (
                        alternative_count
                        / 3.0
                    )
                ),
            ),
        )

        # --------------------------------------------------
        # Missing dimension pressure
        # --------------------------------------------------
        #
        # A reduced frame becomes problematic when
        # relevant dimensions are likely to be excluded.
        # --------------------------------------------------

        missing_dimension_pressure = max(
            0.0,
            min(
                1.0,
                (
                    reduction * 0.35
                    + hidden_assumption_pressure * 0.25
                    + (
                        1.0
                        - integration
                    ) * 0.25
                    + alternative_scarcity * 0.15
                ),
            ),
        )

        # --------------------------------------------------
        # Excessive reduction pressure
        # --------------------------------------------------
        #
        # Excessive reduction means that the cognitive
        # compression may have become too narrow relative
        # to the complexity of the represented reality.
        # --------------------------------------------------

        excessive_reduction_pressure = max(
            0.0,
            min(
                1.0,
                (
                    reduction * 0.35
                    + hidden_assumption_pressure * 0.30
                    + missing_dimension_pressure * 0.20
                    + closure * 0.15
                ),
            ),
        )

        excessive_reduction = (
            excessive_reduction_pressure
            >= 0.60
        )

        # --------------------------------------------------
        # Forgotten reduction pressure
        # --------------------------------------------------
        #
        # Forgotten reduction is more serious than
        # reduction itself.
        #
        # It appears when a reduced representation risks
        # being treated as if it were reality itself.
        #
        # Closure and lack of alternatives increase this
        # pressure.
        # --------------------------------------------------

        forgotten_reduction_pressure = max(
            0.0,
            min(
                1.0,
                (
                    excessive_reduction_pressure * 0.40
                    + closure * 0.30
                    + alternative_scarcity * 0.20
                    + (
                        1.0
                        - integration
                    ) * 0.10
                ),
            ),
        )

        forgotten_reduction = (
            forgotten_reduction_pressure
            >= 0.60
        )

        # --------------------------------------------------
        # Reduction state
        # --------------------------------------------------

        if forgotten_reduction:
            reduction_state = (
                "forgotten_reduction"
            )

        elif excessive_reduction:
            reduction_state = (
                "excessive_reduction"
            )

        elif hidden_assumption_pressure >= 0.40:
            reduction_state = (
                "moderate_reduction"
            )

        else:
            reduction_state = (
                "ordinary_reduction"
            )

        # --------------------------------------------------
        # Interpretation
        # --------------------------------------------------

        if forgotten_reduction:
            summary = (
                "Possible forgotten reduction detected."
            )

            committee_reply = (
                "The current frame may be treating a reduced "
                "representation as if it were sufficiently complete. "
                "Missing dimensions and alternative interpretations "
                "should be restored before certainty increases."
            )

        elif excessive_reduction:
            summary = (
                "Excessive reduction pressure detected."
            )

            committee_reply = (
                "The current interpretation may compress too many "
                "relevant dimensions. Expand context, alternatives "
                "and integrated understanding."
            )

        elif hidden_assumption_pressure >= 0.40:
            summary = (
                "Moderate reduction pressure detected."
            )

            committee_reply = (
                "Some simplification may be present and should "
                "be checked against context and alternative hypotheses."
            )

        else:
            summary = (
                "Ordinary cognitive reduction detected."
            )

            committee_reply = (
                "Reduction remains compatible with revisability. "
                "No strong excessive or forgotten reduction "
                "is currently detected."
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        result = {
            "agent": self.name,

            "reduction_level": (
                hidden_assumption_pressure
            ),

            "hidden_assumption_pressure": (
                hidden_assumption_pressure
            ),

            "semantic_reduction_pressure": (
                semantic_reduction_pressure
            ),

            "possible_hidden_assumptions": (
                possible_hidden_assumptions
            ),

            # ----------------------------------------------
            # New reduction mechanics
            # ----------------------------------------------

            "reduction_state": (
                reduction_state
            ),

            "alternative_scarcity": (
                alternative_scarcity
            ),

            "missing_dimension_pressure": (
                missing_dimension_pressure
            ),

            "excessive_reduction_pressure": (
                excessive_reduction_pressure
            ),

            "forgotten_reduction_pressure": (
                forgotten_reduction_pressure
            ),

            "excessive_reduction": (
                excessive_reduction
            ),

            "forgotten_reduction": (
                forgotten_reduction
            ),

            # ----------------------------------------------
            # Cognitive variables
            # ----------------------------------------------

            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,

            # ----------------------------------------------
            # Semantic evidence
            # ----------------------------------------------

            "semantic_assumptions": (
                assumption_count
            ),

            "semantic_uncertainties": (
                uncertainty_count
            ),

            "semantic_alternatives": (
                alternative_count
            ),

            "assumptions": (
                assumptions
            ),

            "uncertainties": (
                uncertainties
            ),

            "alternative_hypotheses": (
                alternative_hypotheses
            ),

            # ----------------------------------------------
            # Interpretation
            # ----------------------------------------------

            "summary": summary,
            "committee_reply": (
                committee_reply
            ),

            "principle": (
                "Reduction is necessary to cognition. "
                "The principal risk appears when reduction "
                "becomes excessive or when a reduced representation "
                "is forgotten as a reduction and treated as if it "
                "were reality itself."
            ),
        }

        workspace.add_interpretation(
            self.name,
            result,
        )

        return result

    @staticmethod
    def _safe_level(
        value: Any,
        fallback: float = 0.0,
    ) -> float:
        """
        Safely convert a value to DeDe's internal 0..1 scale.
        """

        if value is None:
            return fallback

        try:
            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return fallback

        return max(
            0.0,
            min(
                1.0,
                numeric_value,
            ),
        )
