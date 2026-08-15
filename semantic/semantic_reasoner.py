"""
DeDe - Semantic Reasoner

Language-neutral symbolic semantic reasoning component.

The SemanticReasoner enriches the semantic representation by deriving:
- assumptions
- uncertainties
- alternative hypotheses
- missing dimensions
- causal links
- reasoning notes

It operates from semantic structure rather than language-specific
keywords.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class SemanticReasoner:
    """
    Produces first-level semantic reasoning from claims,
    concepts and relations.
    """

    name = "semantic_reasoner"

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        semantic = workspace.interpretations.get(
            "semantic",
            {},
        )

        knowledge = workspace.interpretations.get(
            "knowledge",
            {},
        )

        if not isinstance(
            semantic,
            dict,
        ):
            semantic = {}

        if not isinstance(
            knowledge,
            dict,
        ):
            knowledge = {}

        claims = semantic.get(
            "claims",
            [],
        )

        concepts = semantic.get(
            "main_concepts",
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
            concepts,
            list,
        ):
            concepts = []

        if not isinstance(
            relations,
            list,
        ):
            relations = []

        assumptions = []
        uncertainties = []
        alternative_hypotheses = []
        missing_dimensions = []
        causal_links = []
        reasoning_notes = []

        # -------------------------------------------------
        # Structural indicators
        # -------------------------------------------------

        claim_count = len(
            claims
        )

        concept_count = len(
            concepts
        )

        relation_count = len(
            relations
        )

        relation_density = min(
            1.0,
            relation_count
            / max(
                1,
                concept_count,
            ),
        )

        knowledge_sources = knowledge.get(
            "sources",
            [],
        )

        if not isinstance(
            knowledge_sources,
            list,
        ):
            knowledge_sources = []

        source_count = len(
            knowledge_sources
        )

        # -------------------------------------------------
        # Assumptions
        # -------------------------------------------------

        if (
            claim_count > 0
            and relation_density < 0.50
        ):
            assumptions.append(
                "The current interpretation may depend on implicit "
                "relations that are not yet represented explicitly."
            )

        if (
            claim_count > 1
            and relation_count < claim_count
        ):
            assumptions.append(
                "Multiple claims are present but their relationships "
                "are not yet fully articulated."
            )

        # -------------------------------------------------
        # Missing dimensions
        # -------------------------------------------------

        if (
            claim_count > 0
            and source_count == 0
        ):
            missing_dimensions.append(
                "The validation path of the current claim is not yet explicit."
            )

        if (
            concept_count > 0
            and relation_density < 0.35
        ):
            missing_dimensions.append(
                "The contextual and relational structure remains incomplete."
            )

        if (
            claim_count > 0
            and concept_count <= 2
        ):
            missing_dimensions.append(
                "The current representation contains few explicit dimensions."
            )

        # -------------------------------------------------
        # Uncertainties
        # -------------------------------------------------

        if (
            claim_count > 0
            and source_count == 0
        ):
            uncertainties.append(
                "The claim is not connected to an explicit source."
            )

        if (
            claim_count > 0
            and relation_count < 2
        ):
            uncertainties.append(
                "The semantic relation structure is weak or underdeveloped."
            )

        if not claims:
            uncertainties.append(
                "No semantic claim was available for reasoning."
            )

        # -------------------------------------------------
        # Alternative hypotheses
        # -------------------------------------------------

        if claim_count > 0:
            alternative_hypotheses.append(
                "Alternative explanations should remain available "
                "until the current interpretation is sufficiently grounded."
            )

        # -------------------------------------------------
        # Causal links
        # -------------------------------------------------

        for relation in relations:

            if not isinstance(
                relation,
                dict,
            ):
                continue

            relation_type = str(
                relation.get(
                    "relation",
                    relation.get(
                        "type",
                        "",
                    ),
                )
            )

            if relation_type and relation_type != "adjacent_concept":
                causal_links.append(
                    relation
                )

        # -------------------------------------------------
        # Reasoning notes
        # -------------------------------------------------

        if assumptions:
            reasoning_notes.append(
                "Implicit assumptions were inferred from structural gaps "
                "between claims and relations."
            )

        if missing_dimensions:
            reasoning_notes.append(
                "Some dimensions appear absent from the current "
                "semantic representation."
            )

        if alternative_hypotheses:
            reasoning_notes.append(
                "At least one alternative hypothesis is preserved "
                "for revisability."
            )

        result = {
            "engine": self.name,
            "assumptions": assumptions,
            "uncertainties": uncertainties,
            "alternative_hypotheses": alternative_hypotheses,
            "missing_dimensions": missing_dimensions,
            "causal_links": causal_links,
            "reasoning_notes": reasoning_notes,
            "assumption_count": len(
                assumptions
            ),
            "uncertainty_count": len(
                uncertainties
            ),
            "alternative_count": len(
                alternative_hypotheses
            ),
            "missing_dimension_count": len(
                missing_dimensions
            ),
            "causal_link_count": len(
                causal_links
            ),
            "reasoning_note_count": len(
                reasoning_notes
            ),
            "source_semantic_claims": claims,
            "source_concepts": concepts,
            "source_relations": relations,
            "relation_density": relation_density,
            "source_count": source_count,
            "summary": (
                "Semantic reasoning derived assumptions, uncertainties, "
                "alternatives and missing dimensions from language-neutral "
                "semantic structure."
            ),
        }

        workspace.set_raw(
            "assumption_count",
            len(
                assumptions
            ),
            {
                "engine": self.name,
                "summary": (
                    "Number of inferred semantic assumptions."
                ),
            },
        )

        workspace.set_raw(
            "alternative_count",
            len(
                alternative_hypotheses
            ),
            {
                "engine": self.name,
                "summary": (
                    "Number of generated alternative hypotheses."
                ),
            },
        )

        workspace.set_raw(
            "reasoning_uncertainty_count",
            len(
                uncertainties
            ),
            {
                "engine": self.name,
                "summary": (
                    "Number of reasoning uncertainties."
                ),
            },
        )

        workspace.set_raw(
            "missing_dimension_count",
            len(
                missing_dimensions
            ),
            {
                "engine": self.name,
                "summary": (
                    "Number of missing semantic dimensions."
                ),
            },
        )

        workspace.set_raw(
            "causal_link_count",
            len(
                causal_links
            ),
            {
                "engine": self.name,
                "summary": (
                    "Number of inferred causal links."
                ),
            },
        )

        workspace.add_interpretation(
            self.name,
            result,
        )

        return workspace
