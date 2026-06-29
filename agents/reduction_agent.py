"""
DeDe - Reduction Agent

Phase 2 cognitive agent.

The Reduction Agent no longer estimates reduction directly from text.
It reads shared cognitive variables from the CognitiveWorkspace
and interprets reduction pressure, hidden assumptions and missing dimensions.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ReductionAgent:
    """
    Cognitive agent responsible for interpreting reduction pressure.

    Reduction reads:
    - Reduction
    - Grounding
    - Integration
    - Closure

    It produces an interpretation of possible hidden assumptions
    and forgotten reductions.
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

        hidden_assumption_pressure = max(
            0.0,
            min(
                1.0,
                (reduction * 0.55)
                + (closure * 0.25)
                - (integration * 0.20)
                - (grounding * 0.10)
                + 0.20,
            ),
        )

        possible_hidden_assumptions = hidden_assumption_pressure >= 0.60

        if hidden_assumption_pressure >= 0.70:
            summary = "Strong reduction pressure detected."
            committee_reply = (
                "The interpretation may be shaped by hidden assumptions or missing dimensions."
            )
        elif hidden_assumption_pressure >= 0.40:
            summary = "Moderate reduction pressure detected."
            committee_reply = (
                "Some simplification may be present and should be checked against context."
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
            "possible_hidden_assumptions": possible_hidden_assumptions,
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(self.name, result)

        return result
