"""
DeDe - Integration Estimator

Estimates conceptual integration from semantic structure.

Integration represents how strongly concepts, claims and relations
form a connected representation.

The estimator is language-neutral and does not rely on discourse
connectors from any particular language.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class IntegrationEstimator:
    """
    Estimates conceptual integration.

    Integration increases when:
    - concepts are present;
    - relations connect them;
    - semantic density is coherent;
    - claims are supported by relational structure.
    """

    name = "integration"

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        concept_count = self._safe_number(
            workspace.get(
                "concept_count"
            )
        )

        relation_count = self._safe_number(
            workspace.get(
                "relation_count"
            )
        )

        concept_density = self._safe_level(
            workspace.get(
                "concept_density"
            )
        )

        semantic = workspace.interpretations.get(
            "semantic",
            {},
        )

        if not isinstance(
            semantic,
            dict,
        ):
            semantic = {}

        claims = semantic.get(
            "claims",
            [],
        )

        relations = semantic.get(
            "relations",
            [],
        )

        if not isinstance(
            claims,
            list,
        ):
            claims = []

        if not isinstance(
            relations,
            list,
        ):
            relations = []

        claim_count = len(
            claims
        )

        semantic_relation_count = len(
            relations
        )

        # --------------------------------------------------
        # Structural richness
        # --------------------------------------------------

        concept_presence = min(
            1.0,
            concept_count / 8.0,
        )

        relation_presence = min(
            1.0,
            relation_count / 8.0,
        )

        semantic_relation_presence = min(
            1.0,
            semantic_relation_count
            / max(
                1,
                concept_count,
            ),
        )

        claim_structure = min(
            1.0,
            semantic_relation_count
            / max(
                1,
                claim_count,
            ),
        )

        # --------------------------------------------------
        # Final integration
        # --------------------------------------------------

        score = (
            concept_presence * 0.20
            + relation_presence * 0.25
            + concept_density * 0.25
            + semantic_relation_presence * 0.20
            + claim_structure * 0.10
        )

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        workspace.set(
            self.name,
            score,
            {
                "estimator": self.name,

                "concept_count": (
                    concept_count
                ),

                "relation_count": (
                    relation_count
                ),

                "concept_density": (
                    concept_density
                ),

                "claim_count": (
                    claim_count
                ),

                "semantic_relation_count": (
                    semantic_relation_count
                ),

                "concept_presence": round(
                    concept_presence,
                    3,
                ),

                "relation_presence": round(
                    relation_presence,
                    3,
                ),

                "semantic_relation_presence": round(
                    semantic_relation_presence,
                    3,
                ),

                "claim_structure": round(
                    claim_structure,
                    3,
                ),

                "summary": (
                    "Integration estimated from language-neutral "
                    "conceptual and relational structure."
                ),
            },
        )

        return workspace

    @staticmethod
    def _safe_number(
        value: Any,
    ) -> float:

        try:
            return max(
                0.0,
                float(
                    value
                ),
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _safe_level(
        value: Any,
    ) -> float:

        try:
            level = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                level,
            ),
        )
