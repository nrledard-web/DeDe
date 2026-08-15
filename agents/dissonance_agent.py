"""
DeDe - Dissonance Agent

Cognitive agent responsible for detecting possible tensions
between claims, principles, certainty, reduction and collective
stabilization.

Dissonance is not treated as pathology.

The agent does not decide whether a belief is true or false.
It evaluates whether the current cognitive frame contains
tensions that may be difficult to reconcile or revise.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class DissonanceAgent:
    """
    Interpret possible cognitive dissonance from the shared workspace.

    Main dimensions:
    - internal contradiction pressure
    - reduction pressure
    - closure / doxa
    - alternative scarcity
    - consensus stabilization
    - consensus dependency
    - grounding

    Consensus never acts as a truth score.
    """

    name = "dissonance"

    def analyze(
        self,
        workspace: CognitiveWorkspace,
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Core cognitive variables
        # --------------------------------------------------

        grounding = self._safe_level(
            workspace.get(
                "grounding"
            )
        )

        integration = self._safe_level(
            workspace.get(
                "integration"
            )
        )

        closure = self._safe_level(
            workspace.get(
                "closure"
            )
        )

        reduction = self._safe_level(
            workspace.get(
                "reduction"
            )
        )

        consensus_trend = self._safe_level(
            workspace.get(
                "consensus_trend"
            )
        )

        # --------------------------------------------------
        # Semantic structures
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

        alternatives = semantic.get(
            "alternative_hypotheses",
            [],
        )

        missing_dimensions = semantic.get(
            "missing_dimensions",
            [],
        )

        claims = semantic.get(
            "source_semantic_claims",
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
            alternatives,
            list,
        ):
            alternatives = []

        if not isinstance(
            missing_dimensions,
            list,
        ):
            missing_dimensions = []

        if not isinstance(
            claims,
            list,
        ):
            claims = []

        # --------------------------------------------------
        # Reduction Agent context
        # --------------------------------------------------

        reduction_view = (
            workspace.interpretations.get(
                "reduction",
                {},
            )
        )

        if not isinstance(
            reduction_view,
            dict,
        ):
            reduction_view = {}

        excessive_reduction_pressure = self._safe_level(
            reduction_view.get(
                "excessive_reduction_pressure",
                reduction,
            )
        )

        forgotten_reduction_pressure = self._safe_level(
            reduction_view.get(
                "forgotten_reduction_pressure",
                0.0,
            )
        )

        alternative_scarcity = self._safe_level(
            reduction_view.get(
                "alternative_scarcity",
                0.0,
            )
        )

        # --------------------------------------------------
        # Consensus Trend context
        # --------------------------------------------------

        consensus_view = (
            workspace.interpretations.get(
                "consensus_trend",
                {},
            )
        )

        if not isinstance(
            consensus_view,
            dict,
        ):
            consensus_view = {}

        consensus_available = bool(
            consensus_view.get(
                "consensus_available",
                False,
            )
        )

        consensus_dependency = self._safe_level(
            consensus_view.get(
                "consensus_dependency",
                0.0,
            )
        )

        independent_convergence = self._safe_level(
            consensus_view.get(
                "independent_convergence",
                0.0,
            )
        )

        epistemic_relation = str(
            consensus_view.get(
                "epistemic_relation",
                "consensus_not_established",
            )
        )

        # --------------------------------------------------
        # Structural contradiction pressure
        # --------------------------------------------------
        #
        # At this stage DeDe does not yet perform full
        # proposition-to-proposition logical contradiction.
        #
        # We therefore estimate tension from:
        # - claims present
        # - assumptions
        # - uncertainties
        # - missing dimensions
        # - weak integration
        #
        # This can later be replaced by a dedicated
        # contradiction engine.
        # --------------------------------------------------

        claim_density = min(
            1.0,
            len(claims) / 3.0,
        )

        assumption_pressure = min(
            1.0,
            len(assumptions) / 3.0,
        )

        uncertainty_pressure = min(
            1.0,
            len(uncertainties) / 3.0,
        )

        missing_dimension_pressure = min(
            1.0,
            len(missing_dimensions) / 3.0,
        )

        integration_gap = (
            1.0
            - integration
        )

        contradiction_pressure = max(
            0.0,
            min(
                1.0,
                (
                    claim_density * 0.15
                    + assumption_pressure * 0.20
                    + uncertainty_pressure * 0.20
                    + missing_dimension_pressure * 0.20
                    + integration_gap * 0.25
                ),
            ),
        )

        # --------------------------------------------------
        # Revision resistance
        # --------------------------------------------------

        revision_resistance = max(
            0.0,
            min(
                1.0,
                (
                    closure * 0.35
                    + forgotten_reduction_pressure * 0.25
                    + excessive_reduction_pressure * 0.15
                    + alternative_scarcity * 0.15
                    + consensus_dependency * 0.10
                ),
            ),
        )

        # --------------------------------------------------
        # Collective stabilization pressure
        # --------------------------------------------------
        #
        # Consensus contributes only when available.
        #
        # Consensus dependency matters more than consensus
        # itself because repetition / low independence may
        # make revision harder without increasing truth.
        # --------------------------------------------------

        if consensus_available:

            collective_stabilization_pressure = max(
                0.0,
                min(
                    1.0,
                    (
                        consensus_trend * 0.35
                        + consensus_dependency * 0.45
                        + (
                            1.0
                            - independent_convergence
                        ) * 0.20
                    ),
                ),
            )

        else:

            collective_stabilization_pressure = 0.0

        # --------------------------------------------------
        # Dissonance score
        # --------------------------------------------------
        #
        # Dissonance rises when:
        # - internal tension exists
        # - revision resistance is high
        # - reduction narrows alternatives
        # - collective stabilization reinforces closure
        #
        # Grounding and integration reduce pressure.
        # --------------------------------------------------

        dissonance_score = max(
            0.0,
            min(
                1.0,
                (
                    contradiction_pressure * 0.35
                    + revision_resistance * 0.30
                    + excessive_reduction_pressure * 0.15
                    + collective_stabilization_pressure * 0.10
                    + closure * 0.10
                    - grounding * 0.10
                    - integration * 0.10
                ),
            ),
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if dissonance_score >= 0.75:
            level = "very_high"

        elif dissonance_score >= 0.55:
            level = "high"

        elif dissonance_score >= 0.35:
            level = "moderate"

        elif dissonance_score >= 0.15:
            level = "low"

        else:
            level = "minimal"

        dissonance_detected = (
            dissonance_score >= 0.35
        )

        # --------------------------------------------------
        # Interpretation
        # --------------------------------------------------

        if dissonance_score >= 0.75:

            summary = (
                "Strong cognitive dissonance pressure detected."
            )

            committee_reply = (
                "Several cognitive pressures appear difficult to "
                "reconcile. The current frame may benefit from "
                "separating claims, assumptions, evidence, certainty "
                "and group consensus before further stabilization."
            )

        elif dissonance_score >= 0.55:

            summary = (
                "Elevated cognitive dissonance pressure detected."
            )

            committee_reply = (
                "The current reasoning contains tensions that may "
                "become difficult to revise if certainty, reduction "
                "or collective reinforcement continue to increase."
            )

        elif dissonance_score >= 0.35:

            summary = (
                "Moderate cognitive dissonance pressure detected."
            )

            committee_reply = (
                "Some tensions are present between the current frame, "
                "its assumptions and its available alternatives."
            )

        else:

            summary = (
                "Low cognitive dissonance pressure detected."
            )

            committee_reply = (
                "No strong unresolved cognitive tension is currently "
                "detected."
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        result = {
            "agent": self.name,

            "dissonance_detected": (
                dissonance_detected
            ),

            "dissonance_score": round(
                dissonance_score,
                3,
            ),

            "level": level,

            "contradiction_pressure": round(
                contradiction_pressure,
                3,
            ),

            "revision_resistance": round(
                revision_resistance,
                3,
            ),

            "collective_stabilization_pressure": round(
                collective_stabilization_pressure,
                3,
            ),

            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,

            "excessive_reduction_pressure": round(
                excessive_reduction_pressure,
                3,
            ),

            "forgotten_reduction_pressure": round(
                forgotten_reduction_pressure,
                3,
            ),

            "alternative_scarcity": round(
                alternative_scarcity,
                3,
            ),

            "consensus_trend": round(
                consensus_trend,
                3,
            ),

            "consensus_available": (
                consensus_available
            ),

            "consensus_dependency": round(
                consensus_dependency,
                3,
            ),

            "independent_convergence": round(
                independent_convergence,
                3,
            ),

            "consensus_epistemic_relation": (
                epistemic_relation
            ),

            "semantic_assumptions": (
                len(assumptions)
            ),

            "semantic_uncertainties": (
                len(uncertainties)
            ),

            "semantic_alternatives": (
                len(alternatives)
            ),

            "semantic_missing_dimensions": (
                len(missing_dimensions)
            ),

            "summary": summary,

            "committee_reply": (
                committee_reply
            ),

            "principle": (
                "Cognitive dissonance is treated as a tension between "
                "cognitive commitments, not as pathology. Consensus "
                "does not determine truth; it may only contribute to "
                "stabilization or resistance to revision."
            ),
        }

        workspace.add_interpretation(
            self.name,
            result,
        )

        workspace.set(
            "dissonance",
            dissonance_score,
            signals=result,
        )

        return result

    @staticmethod
    def _safe_level(
        value: Any,
        fallback: float = 0.0,
    ) -> float:

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
