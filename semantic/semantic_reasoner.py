"""
DeDe - Semantic Reasoner

Symbolic semantic reasoning component.

The SemanticReasoner enriches the semantic representation by deriving:
- assumptions
- uncertainties
- alternative hypotheses
- missing dimensions
- causal links
- reasoning notes

It is the first step from semantic description toward semantic reasoning.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class SemanticReasoner:
    """
    Produces first-level semantic reasoning from claims and concepts.
    """

    name = "semantic_reasoner"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        semantic = workspace.interpretations.get("semantic", {})
        knowledge = workspace.interpretations.get("knowledge", {})

        claims = semantic.get("claims", [])
        concepts = semantic.get("main_concepts", [])
        relations = semantic.get("relations", [])

        concept_set = set(concepts)

        assumptions = []
        uncertainties = []
        alternative_hypotheses = []
        missing_dimensions = []
        causal_links = []
        reasoning_notes = []

        # -------------------------------------------------
        # Assumptions
        # -------------------------------------------------

        if "certainty" in concept_set and "understanding" in concept_set:
            assumptions.append(
                "Certainty and understanding can evolve independently."
            )

            causal_links.append(
                {
                    "source": "certainty",
                    "relation": "can_stabilize_faster_than",
                    "target": "understanding",
                }
            )

            alternative_hypotheses.append(
                "Mecroyance may also emerge from emotional pressure, social reinforcement or contextual reduction."
            )

        if "cognitive" in concept_set and "condition" in concept_set:
            assumptions.append(
                "Mecroyance is treated as a cognitive condition rather than a moral fault."
            )

        # -------------------------------------------------
        # Missing dimensions
        # -------------------------------------------------

        if "certainty" in concept_set and "source" not in concept_set:
            missing_dimensions.append(
                "The source or validation path of certainty is not yet explicit."
            )

        if "understanding" in concept_set and "context" not in concept_set:
            missing_dimensions.append(
                "The contextual conditions shaping understanding are not yet explicit."
            )

        if "mecroyance" in concept_set and "reduction" not in concept_set:
            missing_dimensions.append(
                "The role of reduction in mecroyance is not yet represented."
            )

        # -------------------------------------------------
        # Uncertainties
        # -------------------------------------------------

        if claims and not knowledge.get("sources"):
            uncertainties.append(
                "The claim is not connected to an explicit source."
            )

        if claims and len(relations) < 2:
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

        if not alternative_hypotheses:
            alternative_hypotheses.append(
                "Alternative explanations should be explored if the claim becomes central to the diagnosis."
            )

        # -------------------------------------------------
        # Reasoning notes
        # -------------------------------------------------

        if assumptions:
            reasoning_notes.append(
                "The semantic layer inferred implicit assumptions from concept co-presence."
            )

        if missing_dimensions:
            reasoning_notes.append(
                "Some dimensions appear absent from the current semantic representation."
            )

        if alternative_hypotheses:
            reasoning_notes.append(
                "At least one alternative hypothesis is available for revisability."
            )

        result = {
            "engine": self.name,
            "assumptions": assumptions,
            "uncertainties": uncertainties,
            "alternative_hypotheses": alternative_hypotheses,
            "missing_dimensions": missing_dimensions,
            "causal_links": causal_links,
            "reasoning_notes": reasoning_notes,
            "assumption_count": len(assumptions),
            "uncertainty_count": len(uncertainties),
            "alternative_count": len(alternative_hypotheses),
            "missing_dimension_count": len(missing_dimensions),
            "causal_link_count": len(causal_links),
            "reasoning_note_count": len(reasoning_notes),
            "source_semantic_claims": claims,
            "source_concepts": concepts,
            "source_relations": relations,
            "summary": (
                "Semantic reasoning derived assumptions, uncertainties, "
                "alternatives, missing dimensions and causal links."
            ),
        }

        workspace.set_raw(
            "assumption_count",
            len(assumptions),
            {
                "engine": self.name,
                "summary": "Number of inferred semantic assumptions.",
            },
        )

        workspace.set_raw(
            "alternative_count",
            len(alternative_hypotheses),
            {
                "engine": self.name,
                "summary": "Number of generated alternative hypotheses.",
            },
        )

        workspace.set_raw(
            "reasoning_uncertainty_count",
            len(uncertainties),
            {
                "engine": self.name,
                "summary": "Number of reasoning uncertainties.",
            },
        )

        workspace.set_raw(
            "missing_dimension_count",
            len(missing_dimensions),
            {
                "engine": self.name,
                "summary": "Number of missing semantic dimensions.",
            },
        )

        workspace.set_raw(
            "causal_link_count",
            len(causal_links),
            {
                "engine": self.name,
                "summary": "Number of inferred causal links.",
            },
        )

        workspace.add_interpretation(
            self.name,
            result,
        )

        return workspace
