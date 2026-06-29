"""
DeDe - Doxa Agent

Phase 2 cognitive agent.

The Doxa Agent no longer estimates certainty directly from text.
It reads shared cognitive variables from the CognitiveWorkspace
and interprets certainty pressure, closure and epistemic rigidity.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class DoxaAgent:
    """
    Cognitive agent responsible for interpreting certainty pressure.

    Doxa reads:
    - Grounding
    - Integration
    - Closure
    - Reduction

    It produces an interpretation of doxastic pressure.
    """

    name = "doxa"

    def analyze(self, workspace: CognitiveWorkspace) -> dict[str, Any]:
        """
        Interpret doxastic pressure from the shared workspace.
        """

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        doxa_level = max(
            0.0,
            min(
                1.0,
                (closure * 0.55)
                + (reduction * 0.25)
                - (grounding * 0.15)
                - (integration * 0.10)
                + 0.20,
            ),
        )

        cognitive_closure = doxa_level >= 0.70

        if doxa_level >= 0.70:
            summary = "High doxastic pressure detected."
            committee_reply = (
                "Certainty pressure may exceed grounding and integration."
            )
        elif doxa_level >= 0.40:
            summary = "Moderate doxastic pressure detected."
            committee_reply = (
                "Certainty remains present but still partly revisable."
            )
        else:
            summary = "Low doxastic pressure detected."
            committee_reply = (
                "Certainty appears cognitively revisable."
            )

        result = {
            "agent": self.name,
            "doxa_level": doxa_level,
            "cognitive_closure": cognitive_closure,
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(self.name, result)

        return result
