"""
DeDe - Reduction Agent

Phase 3 cognitive agent.

The Reduction Agent reads shared cognitive variables and semantic
structures from the CognitiveWorkspace to interpret reduction pressure,
hidden assumptions and missing dimensions.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ReductionAgent:
    """
    Cognitive agent responsible for interpreting reduction pressure.
    """

    name = "reduction"

    def analyze(self, workspace: CognitiveWorkspace) -> dict[str, Any]:
        """
        Interpret reduction pressure from the shared workspace.
        """

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        semantic = workspace.interpretations.get("semantic", {})

        assumptions = semantic.get("assumptions", [])
        uncertainties = semantic.get("uncertainties", [])
        alternative_hypotheses = semantic.get(
            "alternative_hypotheses",
            [],
        )

        assumption_count = len(assumptions)
        uncertainty_count = len(uncertainties)
        alternative_count = len(alternative_hypotheses)

        semantic_reduction_pressure = max(
            0.0,
            min(
                0.25,
                assumption_count * 0.08
                + max(0, 2 - alternative_count) * 0.04
                - uncertainty_count * 0.03,
            ),
        )

        hidden_assumption_pressure = max(
            0.0,
            min(
                1.0,
                (reduction * 0.55)
                + (closure * 0.25)
                - (integration * 0.20)
                - (grounding * 0.10)
                + 0.20
                + semantic_reduction_pressure,
            ),
        )

        possible_hidden_assumptions = (
            hidden_assumption_pressure >= 0.60
        )

        if hidden_assumption_pressure >= 0.70:
            summary = "Strong reduction pressure detected."
            committee_reply = (
                "The interpretation may be shaped by hidden assumptions "
                "or missing dimensions."
            )

        elif hidden_assumption_pressure >= 0.40:
            summary = "Moderate reduction pressure detected."
            committee_reply = (
                "Some simplification may be present and should be checked "
                "against context and alternative hypotheses."
            )

        else:
            summary = "Low reduction pressure detected."
            committee_reply = (
                "No significant forgotten reduction is currently detected."
            )

        result = {
            "agent": self.name,
            "reduction_level": hidden_assumption_pressure,
            "hidden_assumption_pressure": hidden_assumption_pressure,
            "semantic_reduction_pressure": semantic_reduction_pressure,
            "possible_hidden_assumptions": possible_hidden_assumptions,
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "semantic_assumptions": assumption_count,
            "semantic_uncertainties": uncertainty_count,
            "semantic_alternatives": alternative_count,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(self.name, result)

        return result
