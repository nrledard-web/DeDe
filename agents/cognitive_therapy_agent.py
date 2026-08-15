"""
DeDe - Cognitive Therapy Agent

Phase 3 cognitive agent.

The Cognitive Therapy Agent reads the CognitiveWorkspace and proposes
recalibration strategies, alternative hypotheses and revisability
improvements.

It now uses both agent interpretations and semantic reasoning.

It also computes the Mécroyance state:

    M = (G + N) - D

where:

    G = gnosis / articulated grounded knowledge
    N = nous / integrated understanding
    D = doxa / certainty and closure pressure

G, N and D are expressed on a 0..10 scale.

Therefore:

    -10 <= M <= 20

Mécroyance is not treated as a condition cognition can completely leave.
The score represents the current position within the permanent condition
of finite cognition.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class CognitiveTherapyAgent:
    """
    Cognitive agent responsible for restoring revisability
    and cognitive balance.

    The agent also computes the current Mécroyance position
    according to:

        M = (G + N) - D
    """

    name = "cognitive_therapy"

    @staticmethod
    def _safe_level(
        value: Any,
        fallback: float = 0.0,
    ) -> float:
        """
        Safely convert a cognitive estimator value
        to the 0..1 range used internally by DeDe.
        """

        if value is None:
            return fallback

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return fallback

        return max(
            0.0,
            min(
                1.0,
                numeric_value,
            ),
        )

    @staticmethod
    def _interpret_mecroyance(
        m_value: float,
    ) -> dict[str, str]:
        """
        Interpret the Mécroyance spectrum.

        Spectrum:

            M < 0
                Cognitive closure

            0 <= M <= 10
                Revisable stability

            10 < M <= 17
                Growing lucidity

            17 < M < 19
                Rare zone

            19 <= M < 20
                Hypothetical pan-sapience

            M == 20
                Ideal asymptote
        """

        if m_value < 0:
            return {
                "zone": "cognitive_closure",
                "label": "Clôture cognitive",
                "interpretation": (
                    "Zone de clôture cognitive : "
                    "la certitude excède l’ancrage cognitif."
                ),
            }

        if 0 <= m_value <= 10:
            return {
                "zone": "revisable_stability",
                "label": "Stabilité révisable",
                "interpretation": (
                    "Zone de stabilité révisable : "
                    "la mécroyance accompagne sans dominer."
                ),
            }

        if 10 < m_value <= 17:
            return {
                "zone": "growing_lucidity",
                "label": "Lucidité croissante",
                "interpretation": (
                    "Zone de lucidité croissante : "
                    "le doute structure la cognition."
                ),
            }

        if 17 < m_value < 19:
            return {
                "zone": "rare_zone",
                "label": "Zone rare",
                "interpretation": (
                    "Zone rare : cognition hautement "
                    "intégrée et réflexive."
                ),
            }

        if 19 <= m_value < 20:
            return {
                "zone": "hypothetical_pan_sapience",
                "label": "Pan-sapience hypothétique",
                "interpretation": (
                    "Pan-sapience hypothétique : "
                    "horizon limite d’une cognition presque "
                    "totalement révisable."
                ),
            }

        if m_value >= 20:
            return {
                "zone": "ideal_asymptote",
                "label": "Asymptote idéale",
                "interpretation": (
                    "Asymptote idéale : totalité du savoir "
                    "et de l’intégration, sans rigidification."
                ),
            }

        return {
            "zone": "unknown",
            "label": "Hors spectre",
            "interpretation": (
                "Valeur hors spectre théorique."
            ),
        }

    def analyze(
        self,
        workspace: CognitiveWorkspace,
    ) -> dict[str, Any]:
        """
        Propose cognitive recalibration from the shared workspace.
        """

        # -------------------------------------------------
        # CORE COGNITIVE ESTIMATORS
        # -------------------------------------------------

        grounding = self._safe_level(
            workspace.get("grounding")
        )

        integration = self._safe_level(
            workspace.get("integration")
        )

        closure = self._safe_level(
            workspace.get("closure")
        )

        reduction = self._safe_level(
            workspace.get("reduction")
        )

        # -------------------------------------------------
        # AGENT INTERPRETATIONS
        # -------------------------------------------------

        interpretations = workspace.interpretations

        conversation_context = interpretations.get(
            "conversation_context",
            {},
        )
        
        therapy_trend = conversation_context.get(
            "therapy_trend",
            {},
        )

        nous = interpretations.get(
            "nous",
            {},
        )

        doxa = interpretations.get(
            "doxa",
            {},
        )

        reduction_view = interpretations.get(
            "reduction",
            {},
        )

        nouscope = interpretations.get(
            "nouscope",
            {},
        )

        dissonance_view = interpretations.get(
            "dissonance",
            {},
        )

        if not isinstance(
            dissonance_view,
            dict,
        ):
            dissonance_view = {}

        semantic_reasoner = interpretations.get(
            "semantic_reasoner",
            {},
        )

        nous_level = nous.get(
            "nous_level"
        )

        doxa_level = doxa.get(
            "doxa_level"
        )

        reduction_level = reduction_view.get(
            "reduction_level"
        )

        # -------------------------------------------------
        # REDUCTION MECHANICS
        # -------------------------------------------------

        reduction_state = reduction_view.get(
            "reduction_state",
            "ordinary_reduction",
        )

        excessive_reduction_pressure = self._safe_level(
            reduction_view.get(
                "excessive_reduction_pressure"
            )
        )

        forgotten_reduction_pressure = self._safe_level(
            reduction_view.get(
                "forgotten_reduction_pressure"
            )
        )

        missing_dimension_pressure = self._safe_level(
            reduction_view.get(
                "missing_dimension_pressure"
            )
        )

        alternative_scarcity = self._safe_level(
            reduction_view.get(
                "alternative_scarcity"
            )
        )

        excessive_reduction = bool(
            reduction_view.get(
                "excessive_reduction",
                False,
            )
        )

        forgotten_reduction = bool(
            reduction_view.get(
                "forgotten_reduction",
                False,
            )
        )

        # -------------------------------------------------
        # DISSONANCE MECHANICS
        # -------------------------------------------------

        dissonance_score = self._safe_level(
            dissonance_view.get(
                "dissonance_score"
            )
        )

        contradiction_pressure = self._safe_level(
            dissonance_view.get(
                "contradiction_pressure"
            )
        )

        revision_resistance = self._safe_level(
            dissonance_view.get(
                "revision_resistance"
            )
        )

        collective_stabilization_pressure = self._safe_level(
            dissonance_view.get(
                "collective_stabilization_pressure"
            )
        )

        consensus_dependency = self._safe_level(
            dissonance_view.get(
                "consensus_dependency"
            )
        )

        dissonance_detected = bool(
            dissonance_view.get(
                "dissonance_detected",
                False,
            )
        )

        cognitive_filter_level = nouscope.get(
            "cognitive_filter_level"
        )

        assumptions = semantic_reasoner.get(
            "assumptions",
            [],
        )

        uncertainties = semantic_reasoner.get(
            "uncertainties",
            [],
        )

        alternative_hypotheses = semantic_reasoner.get(
            "alternative_hypotheses",
            [],
        )

        assumption_count = len(
            assumptions
        )

        uncertainty_count = len(
            uncertainties
        )

        alternative_count = len(
            alternative_hypotheses
        )

        # -------------------------------------------------
        # EXISTING RECALIBRATION LOGIC
        # -------------------------------------------------

        semantic_recalibration_pressure = max(
            0.0,
            min(
                0.20,
                assumption_count * 0.04
                + uncertainty_count * 0.05
                - alternative_count * 0.02,
            ),
        )

        recalibration_pressure = max(
            0.0,
            min(
                1.0,
                (closure * 0.30)
                + (reduction * 0.20)
                + (
                    excessive_reduction_pressure
                    * 0.15
                )
                + (
                    forgotten_reduction_pressure
                    * 0.20
                )
                - (grounding * 0.10)
                - (integration * 0.10)
                + 0.20
                + semantic_recalibration_pressure,
            ),
        )

        recalibration_needed = (
            recalibration_pressure >= 0.50
        )

        # -------------------------------------------------
        # THERAPEUTIC STRATEGIES
        # -------------------------------------------------

        strategies = []

        if closure >= 0.60:
            strategies.append(
                "Reduce certainty pressure by introducing "
                "alternative interpretations."
            )

        if reduction >= 0.60:
            strategies.append(
                "Expand the frame by identifying hidden "
                "assumptions and missing dimensions."
            )

        if grounding < 0.40:
            strategies.append(
                "Strengthen factual grounding through "
                "verification, sources and evidence."
            )

        if integration < 0.40:
            strategies.append(
                "Improve integrated understanding by "
                "connecting facts, context and meaning."
            )

        if (
            cognitive_filter_level is not None
            and cognitive_filter_level >= 0.60
        ):
            strategies.append(
                "Examine possible cognitive filters "
                "influencing interpretation."
            )

        if (
            doxa_level is not None
            and doxa_level >= 0.60
        ):
            strategies.append(
                "Preserve revisability by lowering "
                "doxastic pressure."
            )

        if excessive_reduction:
            strategies.append(
                "Expand the cognitive frame because the current "
                "representation may be compressing too many "
                "relevant dimensions."
            )

        if forgotten_reduction:
            strategies.append(
                "Restore awareness that the current representation "
                "is a reduction of reality rather than reality itself."
            )

        if missing_dimension_pressure >= 0.60:
            strategies.append(
                "Identify important dimensions that may have been "
                "excluded from the current frame."
            )

        if alternative_scarcity >= 0.60:
            strategies.append(
                "Introduce additional plausible alternatives before "
                "allowing the interpretation to stabilize."
            )

        if assumptions:
            strategies.append(
                "Make implicit assumptions explicit before "
                "stabilizing the interpretation."
            )

        if uncertainties:
            strategies.append(
                "Clarify unresolved uncertainties before "
                "increasing confidence."
            )

        if alternative_hypotheses:
            strategies.append(
                "Compare the current interpretation with "
                "available alternative hypotheses."
            )

        if not strategies:
            strategies.append(
                "Maintain cognitive revisability while "
                "preserving the current interpretive structure."
            )

        # -------------------------------------------------
        # EXISTING REVISABILITY SCORE
        # -------------------------------------------------

        revisability_level = max(
            0.0,
            min(
                1.0,
                (grounding * 0.25)
                + (integration * 0.30)
                - (closure * 0.20)
                - (reduction * 0.15)
                + 0.45,
            ),
        )

        # =================================================
        # MECROYANCE
        #
        # M = (G + N) - D
        #
        # Internal DeDe estimators use 0..1.
        # Mécroyance Lab uses G / N / D on 0..10.
        #
        # Therefore we convert ONLY for this model.
        #
        # We do NOT modify the original estimator values.
        # =================================================

        gnosis_internal = grounding

        if nous_level is not None:
            nous_internal = self._safe_level(
                nous_level,
                integration,
            )
        else:
            nous_internal = integration

        if doxa_level is not None:
            doxa_internal = self._safe_level(
                doxa_level,
                closure,
            )
        else:
            doxa_internal = closure

        # Convert 0..1 internal scale
        # to the historical 0..10 Mécroyance scale.

        gnosis_value = (
            gnosis_internal * 10.0
        )

        nous_value = (
            nous_internal * 10.0
        )

        doxa_value = (
            doxa_internal * 10.0
        )

        # Core formula:
        #
        #     M = (G + N) - D

        mecroyance_score = (
            gnosis_value
            + nous_value
            - doxa_value
        )

        # Keep theoretical spectrum strict.

        mecroyance_score = max(
            -10.0,
            min(
                20.0,
                mecroyance_score,
            ),
        )

        # -------------------------------------------------
        # BAR POSITION
        #
        # Historical spectrum:
        #
        #     -10 ................. 20
        #
        # The normalized value exists ONLY for graphical
        # representation.
        #
        # 0.0 means the left edge of the spectrum.
        # 1.0 means the right edge.
        #
        # It does NOT mean absence/presence of Mécroyance.
        # -------------------------------------------------

        mecroyance_bar_position = (
            mecroyance_score + 10.0
        ) / 30.0

        mecroyance_bar_position = max(
            0.0,
            min(
                1.0,
                mecroyance_bar_position,
            ),
        )

        mecroyance_interpretation = (
            self._interpret_mecroyance(
                mecroyance_score
            )
        )

        mecroyance = {
            "formula": "M = (G + N) - D",

            "G": round(
                gnosis_value,
                3,
            ),

            "N": round(
                nous_value,
                3,
            ),

            "D": round(
                doxa_value,
                3,
            ),

            "M": round(
                mecroyance_score,
                3,
            ),

            "bar_position": round(
                mecroyance_bar_position,
                4,
            ),

            "minimum": -10.0,
            "maximum": 20.0,

            "zone": (
                mecroyance_interpretation[
                    "zone"
                ]
            ),

            "zone_label": (
                mecroyance_interpretation[
                    "label"
                ]
            ),

            "interpretation": (
                mecroyance_interpretation[
                    "interpretation"
                ]
            ),

            "principle": (
                "Mécroyance is a permanent condition "
                "of finite cognition. The score represents "
                "a position within Mécroyance, not an exit "
                "from it."
            ),
        }
        
        # -------------------------------------------------
        # TEMPORAL THERAPY EVOLUTION
        # -------------------------------------------------
        #
        # conversation_context contains only PREVIOUS turns.
        #
        # Therefore:
        #
        # therapy_trend["current"]
        #     = latest historical therapy snapshot
        #
        # mecroyance
        #     = therapy state of the CURRENT user turn
        #
        # Temporal comparison must therefore be:
        #
        #     current turn - previous historical turn
        #
        # and NOT:
        #
        #     previous turn - turn before previous
        # -------------------------------------------------

        previous_therapy_state = therapy_trend.get(
            "current",
            {},
        )

        if not isinstance(
            previous_therapy_state,
            dict,
        ):
            previous_therapy_state = {}

        current_therapy_state = dict(
            mecroyance
        )

        therapy_delta = {}

        if previous_therapy_state:

            for key in [
                "G",
                "N",
                "D",
                "M",
            ]:
                current_value = (
                    current_therapy_state.get(
                        key
                    )
                )

                previous_value = (
                    previous_therapy_state.get(
                        key
                    )
                )

                if not isinstance(
                    current_value,
                    (int, float),
                ):
                    continue

                if not isinstance(
                    previous_value,
                    (int, float),
                ):
                    continue

                therapy_delta[key] = round(
                    current_value
                    - previous_value,
                    3,
                )

        delta_m = therapy_delta.get(
            "M"
        )

        if not previous_therapy_state:
            therapy_direction = "baseline"
            therapy_orientation = "baseline"

        elif delta_m is None:
            therapy_direction = "unavailable"
            therapy_orientation = "unavailable"

        elif abs(delta_m) < 0.10:
            therapy_direction = "stable"
            therapy_orientation = "stable"

        elif delta_m > 0:
            therapy_direction = "increasing"
            therapy_orientation = (
                "toward_greater_revisability"
            )

        else:
            therapy_direction = "decreasing"
            therapy_orientation = (
                "toward_cognitive_closure"
            )

        temporal_analysis = {
            "status": (
                "ready"
                if previous_therapy_state
                else "baseline"
            ),

            "sample_count": (
                therapy_trend.get(
                    "sample_count",
                    0,
                )
                + 1
            ),

            "previous": previous_therapy_state,

            "current": current_therapy_state,

            "delta_G": therapy_delta.get(
                "G"
            ),

            "delta_N": therapy_delta.get(
                "N"
            ),

            "delta_D": therapy_delta.get(
                "D"
            ),

            "delta_M": therapy_delta.get(
                "M"
            ),

            "direction": therapy_direction,

            "orientation": therapy_orientation,

            "principle": (
                "Temporal movement describes a change of position "
                "within the Mécroyance spectrum. A positive delta_M "
                "moves cognition toward greater revisability on this "
                "spectrum. A negative delta_M moves cognition toward "
                "cognitive closure. Mécroyance itself does not disappear."
            ),
        }
        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        if recalibration_needed:
            summary = (
                "Cognitive recalibration is recommended."
            )

            committee_reply = (
                "The committee should preserve revisability "
                "before stabilizing interpretation."
            )

        else:
            summary = (
                "Cognitive state appears sufficiently revisable."
            )

            committee_reply = (
                "Current revisability is sufficient, while "
                "semantic alternatives should remain available."
            )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        result = {
            "agent": self.name,

            "recalibration_needed": (
                recalibration_needed
            ),

            "recalibration_pressure": (
                recalibration_pressure
            ),

            "semantic_recalibration_pressure": (
                semantic_recalibration_pressure
            ),

            "revisability_level": (
                revisability_level
            ),

            "strategies": strategies,

            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,

            "nous_level": nous_level,

            "doxa_level_from_committee": (
                doxa_level
            ),

            "reduction_level_from_committee": (
                reduction_level
            ),

            "reduction_state": (
                reduction_state
            ),

            "excessive_reduction_pressure": (
                excessive_reduction_pressure
            ),

            "forgotten_reduction_pressure": (
                forgotten_reduction_pressure
            ),

            "missing_dimension_pressure": (
                missing_dimension_pressure
            ),

            "alternative_scarcity": (
                alternative_scarcity
            ),

            "excessive_reduction": (
                excessive_reduction
            ),

            "forgotten_reduction": (
                forgotten_reduction
            ),

            "cognitive_filter_level": (
                cognitive_filter_level
            ),

            "semantic_assumptions": (
                assumption_count
            ),

            "semantic_uncertainties": (
                uncertainty_count
            ),

            "semantic_alternatives": (
                alternative_count
            ),

            # ---------------------------------------------
            # MECROYANCE
            # ---------------------------------------------

            "mecroyance": mecroyance,

            "mecroyance_score": (
                mecroyance_score
            ),

            "mecroyance_bar_position": (
                mecroyance_bar_position
            ),

            "mecroyance_zone": (
                mecroyance_interpretation[
                    "zone"
                ]
            ),

            "mecroyance_zone_label": (
                mecroyance_interpretation[
                    "label"
                ]
            ),

            "mecroyance_interpretation": (
                mecroyance_interpretation[
                    "interpretation"
                ]
            ),

            # ---------------------------------------------
            # TEMPORAL THERAPY ANALYSIS
            # ---------------------------------------------

            "therapy_temporal_analysis": (
                temporal_analysis
            ),

            "therapy_delta_G": (
                temporal_analysis.get(
                    "delta_G"
                )
            ),

            "therapy_delta_N": (
                temporal_analysis.get(
                    "delta_N"
                )
            ),

            "therapy_delta_D": (
                temporal_analysis.get(
                    "delta_D"
                )
            ),

            "therapy_delta_M": (
                temporal_analysis.get(
                    "delta_M"
                )
            ),

            "therapy_direction": (
                temporal_analysis.get(
                    "direction"
                )
            ),

            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(
            self.name,
            result,
        )

        return result
