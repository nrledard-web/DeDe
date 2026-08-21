"""
DeDe - Decision Threshold Agent

Evaluates whether the current cognitive state is sufficiently
grounded to support a decision while preserving revisability.

Core heuristic relations:

    Ca >= Sd
    Va > Vw

Ca = adjusted certainty
Sd = decision threshold
Va = expected value of acting
Vw = expected value of waiting
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class DecisionThresholdAgent:
    """
    Evaluate the threshold of revisable certainty.

    Possible states:

        NEEDS_CONTEXT
        WAIT_AND_VERIFY
        ACT_WITH_REVISION
        REOPEN_FRAMEWORK
    """

    name = "decision_threshold"

    REQUIRED_CONTEXT_FIELDS = (
        "gravity",
        "irreversibility",
        "error_cost",
        "urgency",
        "waiting_cost",
        "expected_information_gain",
    )

    @staticmethod
    def _safe_level(
        value: Any,
        fallback: float = 0.0,
    ) -> float:
        """
        Convert a value to DeDe's internal 0..1 scale.
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
    def _safe_mapping(
        value: Any,
    ) -> dict[str, Any]:
        """
        Return a dictionary without trusting its type.
        """

        if isinstance(value, dict):
            return value

        return {}

    def _resolve_decision_context(
        self,
        workspace: CognitiveWorkspace,
        decision_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Resolve explicit structured context.

        No linguistic decision markers are used.
        """

        if isinstance(
            decision_context,
            dict,
        ):
            return decision_context

        workspace_context = workspace.get(
            "decision_context"
        )

        if isinstance(
            workspace_context,
            dict,
        ):
            return workspace_context

        interpretations = (
            workspace.interpretations
        )

        if not isinstance(
            interpretations,
            dict,
        ):
            return {}

        stored_context = interpretations.get(
            "decision_context",
            {},
        )

        if isinstance(
            stored_context,
            dict,
        ):
            return stored_context

        return {}

    def _missing_context_fields(
        self,
        decision_context: dict[str, Any],
    ) -> list[str]:
        """
        Identify the information still required.
        """

        return [
            field
            for field
            in self.REQUIRED_CONTEXT_FIELDS
            if field not in decision_context
            or decision_context.get(field) is None
        ]

    def analyze(
        self,
        workspace: CognitiveWorkspace,
        decision_context: (
            dict[str, Any] | None
        ) = None,
    ) -> dict[str, Any]:
        """
        Evaluate whether cognition has reached
        a revisable decision threshold.
        """

        # ---------------------------------------------
        # COGNITIVE ESTIMATORS
        # ---------------------------------------------

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

        # ---------------------------------------------
        # COGNITIVE AGENT INTERPRETATIONS
        # ---------------------------------------------

        interpretations = (
            workspace.interpretations
        )

        if not isinstance(
            interpretations,
            dict,
        ):
            interpretations = {}

        nous_view = self._safe_mapping(
            interpretations.get("nous")
        )

        doxa_view = self._safe_mapping(
            interpretations.get("doxa")
        )

        dissonance_view = self._safe_mapping(
            interpretations.get("dissonance")
        )

        nous_level = self._safe_level(
            nous_view.get("nous_level"),
            integration,
        )

        doxa_level = self._safe_level(
            doxa_view.get("doxa_level"),
            closure,
        )

        revision_resistance = self._safe_level(
            dissonance_view.get(
                "revision_resistance"
            )
        )

        contradiction_pressure = (
            self._safe_level(
                dissonance_view.get(
                    "contradiction_pressure"
                )
            )
        )

        independent_convergence = (
            self._safe_level(
                dissonance_view.get(
                    "independent_convergence"
                )
            )
        )

        # ---------------------------------------------
        # EXPLICIT DECISION CONTEXT
        # ---------------------------------------------

        resolved_context = (
            self._resolve_decision_context(
                workspace=workspace,
                decision_context=(
                    decision_context
                ),
            )
        )

        missing_fields = (
            self._missing_context_fields(
                resolved_context
            )
        )

        if missing_fields:
            result = {
                "agent": self.name,
                "status": "needs_context",
                "decision_state": (
                    "NEEDS_CONTEXT"
                ),
                "decision_ready": False,
                "missing_context_fields": (
                    missing_fields
                ),
                "adjusted_certainty": None,
                "decision_threshold": None,
                "action_value": None,
                "waiting_value": None,
                "certainty_gap": None,
                "principle": (
                    "DeDe must not infer the gravity "
                    "or consequences of a personal "
                    "decision without explicit "
                    "structured context."
                ),
                "recommendation": (
                    "Collect the missing decision "
                    "context before recommending "
                    "action or delay."
                ),
            }

            workspace.add_interpretation(
                self.name,
                result,
            )

            return result

        gravity = self._safe_level(
            resolved_context.get("gravity")
        )

        irreversibility = self._safe_level(
            resolved_context.get(
                "irreversibility"
            )
        )

        error_cost = self._safe_level(
            resolved_context.get("error_cost")
        )

        urgency = self._safe_level(
            resolved_context.get("urgency")
        )

        waiting_cost = self._safe_level(
            resolved_context.get(
                "waiting_cost"
            )
        )

        expected_information_gain = (
            self._safe_level(
                resolved_context.get(
                    "expected_information_gain"
                )
            )
        )

        # ---------------------------------------------
        # ADJUSTED CERTAINTY
        #
        # Ca = cognitive support corrected by
        # closure, contradiction and resistance.
        # ---------------------------------------------

        epistemic_openness = max(
            0.0,
            1.0 - closure,
        )

        adjusted_certainty = (
            (grounding * 0.35)
            + (integration * 0.25)
            + (nous_level * 0.20)
            + (epistemic_openness * 0.10)
            + (
                independent_convergence
                * 0.10
            )
            - (
                revision_resistance
                * 0.10
            )
            - (
                contradiction_pressure
                * 0.05
            )
            - (reduction * 0.05)
        )

        adjusted_certainty = (
            self._safe_level(
                adjusted_certainty
            )
        )

        # ---------------------------------------------
        # DECISION THRESHOLD
        #
        # Serious, irreversible and costly decisions
        # require stronger certainty.
        #
        # Urgency and waiting cost lower the threshold.
        # ---------------------------------------------

        decision_threshold = (
            0.35
            + (gravity * 0.15)
            + (irreversibility * 0.15)
            + (error_cost * 0.15)
            + (
                expected_information_gain
                * 0.10
            )
            - (urgency * 0.10)
            - (waiting_cost * 0.10)
        )

        decision_threshold = max(
            0.20,
            min(
                0.90,
                decision_threshold,
            ),
        )

        # ---------------------------------------------
        # VALUE OF ACTION AND WAITING
        # ---------------------------------------------

        reversibility = max(
            0.0,
            1.0 - irreversibility,
        )

        action_value = (
            (urgency * 0.40)
            + (waiting_cost * 0.35)
            + (reversibility * 0.25)
        )

        waiting_value = (
            (
                expected_information_gain
                * 0.45
            )
            + (error_cost * 0.30)
            + (
                (1.0 - adjusted_certainty)
                * 0.25
            )
        )

        action_value = self._safe_level(
            action_value
        )

        waiting_value = self._safe_level(
            waiting_value
        )

        certainty_gap = (
            adjusted_certainty
            - decision_threshold
        )

        # ---------------------------------------------
        # EXCESSIVE CERTAINTY
        # ---------------------------------------------

        closure_risk = max(
            closure,
            doxa_level,
            revision_resistance,
        )

        excessive_certainty = (
            closure_risk >= 0.70
            and adjusted_certainty
            < decision_threshold + 0.15
        )

        threshold_reached = (
            adjusted_certainty
            >= decision_threshold
        )

        acting_preferred = (
            action_value
            > waiting_value
        )

        # ---------------------------------------------
        # DECISION STATE
        # ---------------------------------------------

        if excessive_certainty:
            decision_state = (
                "REOPEN_FRAMEWORK"
            )

            decision_ready = False

            recommendation = (
                "Reopen the cognitive framework "
                "before making the decision more "
                "difficult to reverse."
            )

        elif (
            threshold_reached
            and acting_preferred
        ):
            decision_state = (
                "ACT_WITH_REVISION"
            )

            decision_ready = True

            recommendation = (
                "The current certainty is sufficient "
                "for action. Act while preserving "
                "explicit conditions for revision."
            )

        else:
            decision_state = (
                "WAIT_AND_VERIFY"
            )

            decision_ready = False

            recommendation = (
                "Wait only for information that has "
                "a realistic chance of changing "
                "the decision."
            )

        # ---------------------------------------------
        # RESULT
        # ---------------------------------------------

        result = {
            "agent": self.name,

            "status": "ready",

            "formula": (
                "Ca >= Sd and Va > Vw"
            ),

            "decision_state": (
                decision_state
            ),

            "decision_ready": (
                decision_ready
            ),

            "threshold_reached": (
                threshold_reached
            ),

            "acting_preferred": (
                acting_preferred
            ),

            "excessive_certainty": (
                excessive_certainty
            ),

            "adjusted_certainty": round(
                adjusted_certainty,
                4,
            ),

            "decision_threshold": round(
                decision_threshold,
                4,
            ),

            "action_value": round(
                action_value,
                4,
            ),

            "waiting_value": round(
                waiting_value,
                4,
            ),

            "certainty_gap": round(
                certainty_gap,
                4,
            ),

            "closure_risk": round(
                closure_risk,
                4,
            ),

            "decision_context": {
                "gravity": gravity,
                "irreversibility": (
                    irreversibility
                ),
                "error_cost": error_cost,
                "urgency": urgency,
                "waiting_cost": (
                    waiting_cost
                ),
                "expected_information_gain": (
                    expected_information_gain
                ),
            },

            "cognitive_support": {
                "grounding": grounding,
                "integration": integration,
                "nous_level": nous_level,
                "doxa_level": doxa_level,
                "closure": closure,
                "reduction": reduction,
                "revision_resistance": (
                    revision_resistance
                ),
                "contradiction_pressure": (
                    contradiction_pressure
                ),
                "independent_convergence": (
                    independent_convergence
                ),
            },

            "recommendation": (
                recommendation
            ),

            "principle": (
                "The right certainty is sufficient "
                "for action without abolishing "
                "revision."
            ),
        }

        workspace.add_interpretation(
            self.name,
            result,
        )

        return result
