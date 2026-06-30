"""
DeDe - NOUSCOPE Agent

Phase 3 cognitive agent.

The NOUSCOPE Agent interprets possible cognitive filter influence
using both cognitive variables and semantic reasoning.

It combines symbolic cognitive mechanics with semantic structures.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class NOUSCOPEAgent:
    """
    Cognitive agent responsible for interpreting cognitive filter influence.
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

        # -------------------------------------------------
        # Semantic Reasoner
        # -------------------------------------------------

        semantic = workspace.interpretations.get(
            "semantic_reasoner",
            {},
        )

        assumptions = semantic.get(
            "assumptions",
            [],
        )

        uncertainties = semantic.get(
            "uncertainties",
            [],
        )

        alternatives = semantic.get(
            "alternative_hypotheses",
            [],
        )

        assumption_count = len(assumptions)
        uncertainty_count = len(uncertainties)
        alternative_count = len(alternatives)

        semantic_filter_pressure = max(
            0.0,
            min(
                0.20,
                assumption_count * 0.05
                + max(0, 2 - alternative_count) * 0.04
                - uncertainty_count * 0.03,
            ),
        )

        # -------------------------------------------------
        # Cognitive mechanics
        # -------------------------------------------------

        cognitive_filter_level = max(
            0.0,
            min(
                1.0,
                (
                    closure * 0.35
                    + reduction * 0.35
                    - grounding * 0.15
                    - integration * 0.10
                    + 0.25
                    + semantic_filter_pressure
                ),
            ),
        )

        possible_filter_influence = (
            cognitive_filter_level >= 0.60
        )

        # -------------------------------------------------
        # Interpretation
        # -------------------------------------------------

        if cognitive_filter_level >= 0.70:

            summary = (
                "Strong cognitive filter influence detected."
            )

            committee_reply = (
                "The interpretation may be significantly shaped by "
                "cognitive filters and implicit assumptions."
            )

        elif cognitive_filter_level >= 0.40:

            summary = (
                "Moderate cognitive filter influence detected."
            )

            committee_reply = (
                "Some interpretive filtering may be present. "
                "Alternative perspectives should remain visible."
            )

        else:

            summary = (
                "Low cognitive filter influence detected."
            )

            committee_reply = (
                "Current cognitive filters do not appear to strongly "
                "distort interpretation."
            )

        result = {

            "agent": self.name,

            "cognitive_filter_level":
                cognitive_filter_level,

            "semantic_filter_pressure":
                semantic_filter_pressure,

            "possible_filter_influence":
                possible_filter_influence,

            "grounding": grounding,
            "integration": integration,
            "closure": closure,
            "reduction": reduction,

            "semantic_assumptions":
                assumption_count,

            "semantic_uncertainties":
                uncertainty_count,

            "semantic_alternatives":
                alternative_count,

            "summary": summary,

            "committee_reply": committee_reply,
        }

        workspace.add_interpretation(
            self.name,
            result,
        )

        return result
