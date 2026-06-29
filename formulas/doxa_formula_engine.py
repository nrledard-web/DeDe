"""
DeDe - DOXA Formula Engine

Phase 2 formula engine.

This engine reads cognitive variables from the CognitiveWorkspace
and computes derived cognitive mechanics indicators.

Formulas do not estimate.
Formulas do not interpret.
They calculate.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class DoxaFormulaEngine:
    """
    Computes Phase 2 cognitive mechanics metrics from the workspace.

    Inputs
    ------
    - Grounding
    - Integration
    - Closure
    - Reduction

    Outputs
    -------
    - Mecroyance pressure
    - Mecroyance risk
    - Cognitive balance
    - Surconfidence
    - Cognitive closure
    - Forgotten reduction pressure
    - Revisability
    """

    def compute(
        self,
        workspace: CognitiveWorkspace,
    ) -> dict[str, Any]:

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        # -------------------------------------------------
        # Raw mechanics
        # -------------------------------------------------

        raw_support = grounding + integration
        raw_pressure = closure + reduction

        # -------------------------------------------------
        # Normalized values (UI)
        # -------------------------------------------------

        support = max(
            0.0,
            min(1.0, raw_support),
        )

        pressure = max(
            0.0,
            min(1.0, raw_pressure),
        )

        # -------------------------------------------------
        # Derived mechanics
        # -------------------------------------------------

        cognitive_balance = max(
            -1.0,
            min(
                1.0,
                raw_support - raw_pressure,
            ),
        )

        mecroyance_pressure = max(
            -1.0,
            min(
                1.0,
                raw_pressure - raw_support,
            ),
        )

        mecroyance_risk = max(
            0.0,
            min(
                1.0,
                mecroyance_pressure,
            ),
        )

        surconfidence = max(
            0.0,
            closure - (grounding * 0.5),
        )

        cognitive_closure = max(
            0.0,
            closure - (
                (grounding + integration) / 2.0
            ),
        )

        forgotten_reduction_pressure = max(
            0.0,
            reduction - integration,
        )

        revisability = max(
            0.0,
            min(
                1.0,
                (
                    grounding * 0.25
                    + integration * 0.35
                    - closure * 0.25
                    - reduction * 0.15
                    + 0.50
                ),
            ),
        )

        # -------------------------------------------------
        # Diagnosis
        # -------------------------------------------------

        if cognitive_balance >= 0.30:

            diagnosis = (
                "Grounding and integration exceed "
                "closure and reduction."
            )

        elif cognitive_balance >= 0.0:

            diagnosis = (
                "Cognitive structure appears "
                "moderately balanced."
            )

        else:

            diagnosis = (
                "Closure and reduction may exceed "
                "grounding and integration."
            )

        # -------------------------------------------------
        # Report
        # -------------------------------------------------

        return {

            "inputs": {

                "grounding": grounding,
                "integration": integration,
                "closure": closure,
                "reduction": reduction,

            },

            "core": {

                "raw_support": raw_support,
                "raw_pressure": raw_pressure,

                "support": support,
                "pressure": pressure,

                "cognitive_balance": cognitive_balance,

                "mecroyance_pressure": mecroyance_pressure,
                "mecroyance_risk": mecroyance_risk,

                "revisability": revisability,

            },

            "derived": {

                "surconfidence": surconfidence,

                "cognitive_closure": cognitive_closure,

                "forgotten_reduction_pressure":
                    forgotten_reduction_pressure,

            },

            "diagnosis": diagnosis,

        }
