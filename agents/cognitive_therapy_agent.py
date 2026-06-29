"""
DeDe - Cognitive Therapy Agent

Phase 2 cognitive agent.

The Cognitive Therapy Agent no longer depends on CognitiveState
or previous symbolic agent chains.

It reads the CognitiveWorkspace and proposes recalibration strategies,
alternative hypotheses and revisability improvements.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class CognitiveTherapyAgent:
    """
    Cognitive agent responsible for restoring revisability
    and cognitive balance.

    Cognitive Therapy reads:
    - Grounding
    - Integration
    - Closure
    - Reduction
    - Agent interpretations already stored in the workspace
    """

    name = "cognitive_therapy"

    def analyze(self, workspace: CognitiveWorkspace) -> dict[str, Any]:
        """
        Propose cognitive recalibration from the shared workspace.
        """

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        interpretations = workspace.interpretations

        nous = interpretations.get("nous", {})
        doxa = interpretations.get("doxa", {})
        reduction_view = interpretations.get("reduction", {})
        nouscope = interpretations.get("nouscope", {})

        nous_level = nous.get("nous_level")
        doxa_level = doxa.get("doxa_level")
        reduction_level = reduction_view.get("reduction_level")
        cognitive_filter_level = nouscope.get("cognitive_filter_level")

        recalibration_pressure = max(
            0.0,
            min(
                1.0,
                (closure * 0.35)
                + (reduction * 0.30)
                - (grounding * 0.15)
                - (integration * 0.15)
                + 0.25,
            ),
        )

        recalibration_needed = recalibration_pressure >= 0.50

        strategies = []

        if closure >= 0.60:
            strategies.append(
                "Reduce certainty pressure by introducing alternative interpretations."
            )

        if reduction >= 0.60:
            strategies.append(
                "Expand the frame by identifying hidden assumptions and missing dimensions."
            )

        if grounding < 0.40:
            strategies.append(
                "Strengthen factual grounding through verification, sources and evidence."
            )

        if integration < 0.40:
            strategies.append(
                "Improve integrated understanding by connecting facts, context and meaning."
            )

        if cognitive_filter_level is not None and cognitive_filter_level >= 0.60:
            strategies.append(
                "Examine possible cognitive filters influencing interpretation."
            )

        if doxa_level is not None and doxa_level >= 0.60:
            strategies.append(
                "Preserve revisability by lowering doxastic pressure."
            )

        if reduction_level is not None and reduction_level >= 0.60:
            strategies.append(
                "Check whether reduction pressure is hiding relevant dimensions."
            )

        if not strategies:
            strategies.append(
                "Maintain cognitive revisability while preserving the current interpretive structure."
            )

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

        if recalibration_needed:
            summary = "Cognitive recalibration is recommended."
            committee_reply = (
                "The committee should preserve revisability before stabilizing interpretation."
            )
        else:
            summary = "Cognitive state appears sufficiently revisable."
            committee_reply = (
                "Current revisability is sufficient, but deeper integration may improve stability."
            )

        result = {
            "agent": self.name,
            "recalibration_needed": recalibration_needed,
            "recalibration_pressure": recalibration_pressure,
            "revisability_level": revisability_level,
            "strategies": strategies,
            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,
            "nous_level": nous_level,
            "doxa_level_from_committee": doxa_level,
            "reduction_level_from_committee": reduction_level,
            "cognitive_filter_level": cognitive_filter_level,
            "summary": summary,
            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(self.name, result)

        return result
