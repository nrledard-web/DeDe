"""
DeDe - Nous Agent

Phase 3 cognitive agent.

Nous interprets integrated understanding from the shared
CognitiveWorkspace.

It combines cognitive variables with the semantic layer.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class NousAgent:
    """
    Cognitive agent responsible for interpreting integrated understanding.
    """

    name = "nous"

    def analyze(
        self,
        workspace: CognitiveWorkspace,
    ) -> dict[str, Any]:

        grounding = workspace.get("grounding")
        integration = workspace.get("integration")
        reduction = workspace.get("reduction")

        # ---------------------------------------------
        # Semantic layer
        # ---------------------------------------------

        semantic = workspace.interpretations.get(
            "semantic",
            {},
        )

        claim_count = semantic.get(
            "claim_count",
            0,
        )

        relation_count = semantic.get(
            "relation_count",
            0,
        )

        semantic_bonus = min(
            0.20,
            relation_count * 0.02,
        )

        # ---------------------------------------------
        # Cognitive mechanics
        # ---------------------------------------------

        nous_level = max(
            0.0,
            min(
                1.0,
                (
                    grounding * 0.35
                    + integration * 0.50
                    - reduction * 0.20
                    + 0.15
                    + semantic_bonus
                ),
            ),
        )

        # ---------------------------------------------
        # Interpretation
        # ---------------------------------------------

        if nous_level >= 0.75:

            summary = (
                "Integrated understanding appears strong."
            )

            committee_reply = (
                "Conceptual and semantic relations appear well integrated."
            )

        elif nous_level >= 0.45:

            summary = (
                "Integrated understanding appears partial."
            )

            committee_reply = (
                "Semantic structure exists, but conceptual integration could be improved."
            )

        else:

            summary = (
                "Integrated understanding appears weak."
            )

            committee_reply = (
                "The committee recommends strengthening conceptual integration."
            )

        result = {

            "agent": self.name,

            "nous_level": nous_level,

            "grounding": grounding,
            "integration": integration,
            "reduction": reduction,

            "semantic_claims": claim_count,
            "semantic_relations": relation_count,
            "semantic_bonus": semantic_bonus,

            "integrated_understanding_needed":
                nous_level < 0.75,

            "summary": summary,

            "committee_reply": committee_reply,

        }

        workspace.add_interpretation(
            self.name,
            result,
        )

        return result
