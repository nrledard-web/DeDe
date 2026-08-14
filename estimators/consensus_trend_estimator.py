"""
DeDe - Consensus Trend Estimator

Estimates collective stabilization around a claim or representation.

Consensus Trend does NOT measure truth.

It measures how strongly a representation appears collectively
supported, repeated or stabilized, while preserving a distinction
between:

- collective agreement
- source independence
- empirical grounding
- ideological pressure
- availability of alternatives

A strong consensus may be well grounded or poorly grounded.
Those dimensions must remain separate.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ConsensusTrendEstimator:
    """
    Estimate collective consensus pressure without equating
    consensus with truth.
    """

    name = "consensus_trend"

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        # --------------------------------------------------
        # Existing source analysis
        # --------------------------------------------------

        source_analysis = (
            workspace.interpretations.get(
                "source_analysis",
                {},
            )
        )

        if not isinstance(
            source_analysis,
            dict,
        ):
            source_analysis = {}

        sources = source_analysis.get(
            "sources",
            [],
        )

        if not isinstance(
            sources,
            list,
        ):
            sources = []

        source_count = len(
            sources
        )

        # --------------------------------------------------
        # Semantic reasoning
        # --------------------------------------------------

        semantic_reasoning = (
            workspace.interpretations.get(
                "semantic_reasoner",
                {},
            )
        )

        if not isinstance(
            semantic_reasoning,
            dict,
        ):
            semantic_reasoning = {}

        alternative_count = self._safe_int(
            semantic_reasoning.get(
                "alternative_count",
                0,
            )
        )

        uncertainty_count = self._safe_int(
            semantic_reasoning.get(
                "uncertainty_count",
                0,
            )
        )

        # --------------------------------------------------
        # Source-level cognitive signals
        # --------------------------------------------------

        independence_values = []
        ideological_pressure_values = []
        relevance_values = []
        evidence_values = []

        for source in sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            analysis = source.get(
                "analysis",
                {},
            )

            if not isinstance(
                analysis,
                dict,
            ):
                continue

            independence_values.append(
                self._normalize_score(
                    analysis.get(
                        "independence",
                        0.0,
                    )
                )
            )

            ideological_pressure_values.append(
                self._normalize_score(
                    analysis.get(
                        "ideological_pressure",
                        0.0,
                    )
                )
            )

            relevance_values.append(
                self._normalize_score(
                    analysis.get(
                        "relevance",
                        0.0,
                    )
                )
            )

            evidence_values.append(
                self._normalize_score(
                    analysis.get(
                        "evidence_level",
                        0.0,
                    )
                )
            )

        independence = self._average(
            independence_values
        )

        ideological_pressure = self._average(
            ideological_pressure_values
        )

        relevance = self._average(
            relevance_values
        )

        evidence = self._average(
            evidence_values
        )

        # --------------------------------------------------
        # Quantity signal
        # --------------------------------------------------

        if source_count <= 0:
            source_quantity = 0.0

        elif source_count == 1:
            source_quantity = 0.20

        elif source_count == 2:
            source_quantity = 0.40

        elif source_count == 3:
            source_quantity = 0.60

        elif source_count == 4:
            source_quantity = 0.80

        else:
            source_quantity = 1.0

        # --------------------------------------------------
        # Alternative scarcity
        # --------------------------------------------------

        alternative_scarcity = max(
            0.0,
            min(
                1.0,
                1.0
                - min(
                    1.0,
                    alternative_count / 3.0,
                ),
            ),
        )

        # --------------------------------------------------
        # Uncertainty preservation
        # --------------------------------------------------

        uncertainty_presence = min(
            1.0,
            uncertainty_count / 3.0,
        )

        # --------------------------------------------------
        # Consensus availability
        # --------------------------------------------------
        #
        # Without external sources, DeDe should NOT pretend
        # to know the degree of collective consensus.
        # --------------------------------------------------

        consensus_available = (
            source_count >= 2
        )

        if consensus_available:

            # ----------------------------------------------
            # Collective stabilization
            # ----------------------------------------------
            #
            # Many relevant sources increase apparent
            # convergence.
            #
            # Low independence reduces the epistemic value
            # of that convergence, but does NOT erase the
            # fact that consensus exists.
            # ----------------------------------------------

            collective_stabilization = (
                source_quantity * 0.40
                + relevance * 0.25
                + alternative_scarcity * 0.20
                + ideological_pressure * 0.15
            )

            collective_stabilization = max(
                0.0,
                min(
                    1.0,
                    collective_stabilization,
                ),
            )

            # ----------------------------------------------
            # Independent convergence
            # ----------------------------------------------

            independent_convergence = (
                collective_stabilization
                * independence
            )

            # ----------------------------------------------
            # Consensus dependency
            # ----------------------------------------------
            #
            # High consensus + low independence suggests
            # repetition or shared framing rather than many
            # independent confirmations.
            # ----------------------------------------------

            consensus_dependency = (
                collective_stabilization
                * (
                    1.0
                    - independence
                )
            )

        else:

            collective_stabilization = 0.0
            independent_convergence = 0.0
            consensus_dependency = 0.0

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if not consensus_available:
            level = "unavailable"

        elif collective_stabilization >= 0.75:
            level = "very_high"

        elif collective_stabilization >= 0.55:
            level = "high"

        elif collective_stabilization >= 0.35:
            level = "moderate"

        else:
            level = "low"

        # --------------------------------------------------
        # Epistemic relation
        # --------------------------------------------------
        #
        # Consensus and grounding must remain separate.
        # --------------------------------------------------

        if not consensus_available:

            epistemic_relation = (
                "consensus_not_established"
            )

        elif (
            collective_stabilization >= 0.55
            and evidence >= 0.55
            and independence >= 0.55
        ):

            epistemic_relation = (
                "consensus_with_independent_grounding"
            )

        elif (
            collective_stabilization >= 0.55
            and (
                evidence < 0.40
                or independence < 0.40
            )
        ):

            epistemic_relation = (
                "consensus_exceeds_grounding"
            )

        elif (
            collective_stabilization < 0.35
            and evidence >= 0.55
        ):

            epistemic_relation = (
                "grounding_exceeds_consensus"
            )

        else:

            epistemic_relation = (
                "mixed"
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        result = {
            "estimator": self.name,
            "status": (
                "ready"
                if consensus_available
                else "unavailable"
            ),

            "score": round(
                collective_stabilization,
                3,
            ),

            "level": level,

            "consensus_available": (
                consensus_available
            ),

            "source_count": (
                source_count
            ),

            "components": {
                "source_quantity": round(
                    source_quantity,
                    3,
                ),

                "relevance": round(
                    relevance,
                    3,
                ),

                "independence": round(
                    independence,
                    3,
                ),

                "evidence": round(
                    evidence,
                    3,
                ),

                "ideological_pressure": round(
                    ideological_pressure,
                    3,
                ),

                "alternative_scarcity": round(
                    alternative_scarcity,
                    3,
                ),

                "uncertainty_presence": round(
                    uncertainty_presence,
                    3,
                ),
            },

            "independent_convergence": round(
                independent_convergence,
                3,
            ),

            "consensus_dependency": round(
                consensus_dependency,
                3,
            ),

            "epistemic_relation": (
                epistemic_relation
            ),

            "principle": (
                "Consensus Trend measures collective stabilization, "
                "not truth. Consensus, grounding and source independence "
                "must remain distinct cognitive dimensions."
            ),
        }

        # --------------------------------------------------
        # Workspace
        # --------------------------------------------------

        workspace.set(
            self.name,
            collective_stabilization,
            signals=result,
        )

        workspace.set_raw(
            "consensus_epistemic_relation",
            epistemic_relation,
        )

        workspace.set_raw(
            "consensus_independent_convergence",
            independent_convergence,
        )

        workspace.set_raw(
            "consensus_dependency",
            consensus_dependency,
        )

        workspace.add_interpretation(
            self.name,
            result,
        )

        return workspace

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _average(
        values: list[float],
    ) -> float:

        if not values:
            return 0.0

        return sum(
            values
        ) / len(
            values
        )

    @staticmethod
    def _safe_int(
        value: Any,
    ) -> int:

        try:
            return int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _normalize_score(
        value: Any,
    ) -> float:

        try:
            score = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if score > 1.0:
            score = (
                score / 100.0
            )

        return max(
            0.0,
            min(
                1.0,
                score,
            ),
        )
