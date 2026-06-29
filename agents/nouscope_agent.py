"""
DeDe - NOUSCOPE Agent

Phase 2 cognitive agent.

The NOUSCOPE Agent no longer estimates cognitive filters directly from text.
It reads shared cognitive variables from the CognitiveWorkspace
and interprets possible filter influence, perspective distortion
and calibration pressure.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class NOUSCOPEAgent:
    """
    Cognitive agent responsible for interpreting cognitive filter influence.

    NOUSCOPE reads:
    - Grounding
    - Integration
    - Closure
    - Reduction

    It produces an interpretation of possible filter influence
    shaping perception and interpretation.
    """

    name = "nouscope"

    def analyze(self, workspace: CognitiveWorkspace) -> dict[str, Any]:
        """
        Interpret cognitive filter influence from the shared workspace.
        """

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        cognitive_filter_level = max(
            0.0,
            min(
                1.0,
                (closure * 0.35)
                + (reduction * 0.35)
                - (grounding * 0.15)
                - (integration * 0.10)
                + 0.25,
            ),
        )

        possible_filter_influence = cognitive_filter_level >= 0.60

        if cognitive_filter_level >= 0.70:
            summary = "Strong cognitive filter influence detected."
            committee_reply = (
                "The interpretation may be significantly shaped by cognitive filters."
            )
        elif cognitive_filter_level >= 0.40:
            summary = "Moderate cognitive filter influence detected."
            committee_reply = (
                "Some interpretive filtering may be present and should remain visible."
            )
        else:
            summary = "Low cognitive filter influence detected."
            committee_reply = (
                "Current cognitive filters do not appear to strongly distort interpretation."
            )

        result = {
            "agent": self.name,
            "cognitive_filter_level": cognitive_filter_level,
            "possible_filter_influence": possible_filter_influence,
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(self.name, result)

        return result
