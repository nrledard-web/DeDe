"""
DeDe - Cognitive Committee

Phase 2 committee layer.

The Cognitive Committee reads agent interpretations stored in the
CognitiveWorkspace and produces a synthetic cognitive judgment.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class CognitiveCommittee:
    """
    Synthesizes cognitive agent interpretations.

    The committee does not estimate variables.
    The committee does not compute formulas.
    The committee listens to agents and produces a shared diagnosis.
    """

    def synthesize(self, workspace: CognitiveWorkspace) -> dict[str, Any]:
        """
        Build a committee synthesis from workspace interpretations.
        """

        interpretations = workspace.interpretations

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        closure = workspace.get("closure")
        reduction = workspace.get("reduction")

        nous = interpretations.get("nous", {})
        doxa = interpretations.get("doxa", {})
        reduction_view = interpretations.get("reduction", {})
        nouscope = interpretations.get("nouscope", {})
        therapy = interpretations.get("cognitive_therapy", {})

        concerns = []
        recommendations = []

        if nous.get("integrated_understanding_needed"):
            concerns.append("integration")
            recommendations.append(
                "Strengthen conceptual integration before stabilizing interpretation."
            )

        if doxa.get("cognitive_closure"):
            concerns.append("closure")
            recommendations.append(
                "Lower certainty pressure and preserve alternative hypotheses."
            )

        if reduction_view.get("possible_hidden_assumptions"):
            concerns.append("reduction")
            recommendations.append(
                "Expand the frame and examine hidden assumptions."
            )

        if nouscope.get("possible_filter_influence"):
            concerns.append("filter")
            recommendations.append(
                "Examine possible cognitive filters shaping interpretation."
            )

        if therapy.get("recalibration_needed"):
            concerns.append("recalibration")
            recommendations.extend(
                therapy.get("strategies", [])
            )

        if not recommendations:
            recommendations.append(
                "Maintain revisability while preserving the current cognitive structure."
            )

        support = grounding + integration
        pressure = closure + reduction

        if support > pressure:
            dominant_orientation = "support"
        elif pressure > support:
            dominant_orientation = "pressure"
        else:
            dominant_orientation = "balanced"

        confidence = max(
            0.0,
            min(
                1.0,
                0.50
                + abs(support - pressure) * 0.25
                - len(concerns) * 0.05,
            ),
        )

        if concerns:
            diagnosis = (
                "The committee detects cognitive tensions requiring review."
            )
        else:
            diagnosis = (
                "The committee finds the cognitive structure currently revisable."
            )

        result = {
            "committee": "cognitive_committee",
            "agent_count": len(interpretations),
            "concerns": concerns,
            "recommendations": recommendations,
            "dominant_orientation": dominant_orientation,
            "confidence": confidence,
            "diagnosis": diagnosis,
            "inputs": {
                "grounding": grounding,
                "integration": integration,
                "closure": closure,
                "reduction": reduction,
            },
            "agent_positions": {
                "nous": nous.get("summary"),
                "doxa": doxa.get("summary"),
                "reduction": reduction_view.get("summary"),
                "nouscope": nouscope.get("summary"),
                "cognitive_therapy": therapy.get("summary"),
            },
        }

        workspace.add_observation(result)

        return result
