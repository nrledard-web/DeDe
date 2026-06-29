"""
DeDe - Nous Agent

Phase 2 cognitive agent.

The Nous Agent no longer estimates integration directly from text.
It reads shared cognitive variables from the CognitiveWorkspace
and interprets the quality of integrated understanding.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class NousAgent:
    """
    Cognitive agent responsible for interpreting integrated understanding.

    Nous reads:
    - Grounding
    - Integration
    - Reduction

    It produces an interpretation of conceptual understanding.
    """

    name = "nous"

    def analyze(self, workspace: CognitiveWorkspace) -> dict[str, Any]:
        """
        Interpret integrated understanding from the shared workspace.
        """

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        reduction = workspace.get("reduction")

        nous_level = max(
            0.0,
            min(
                1.0,
                (grounding * 0.35)
                + (integration * 0.50)
                - (reduction * 0.20)
                + 0.15,
            ),
        )

        if nous_level >= 0.70:
            summary = "Integrated understanding appears strong."
            committee_reply = (
                "Conceptual relations appear sufficiently integrated."
            )
        elif nous_level >= 0.40:
            summary = "Integrated understanding appears partial."
            committee_reply = (
                "Some integration is present, but conceptual links may need strengthening."
            )
        else:
            summary = "Integrated understanding appears weak."
            committee_reply = (
                "The committee should request stronger conceptual integration."
            )

        result = {
            "agent": self.name,
            "nous_level": nous_level,
            "grounding": grounding,
            "integration": integration,
            "reduction": reduction,
            "integrated_understanding_needed": nous_level < 0.70,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(self.name, result)

        return result
