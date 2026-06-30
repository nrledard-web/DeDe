"""
DeDe - Semantic Reasoner

First symbolic semantic reasoning component.

The SemanticReasoner enriches the semantic representation by deriving:
- assumptions
- uncertainties
- alternative hypotheses

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

        claims = semantic.get("claims", [])
        concepts = semantic.get("main_concepts", [])
        relations = semantic.get("relations", [])

        assumptions = []
        uncertainties = []
        alternative_hypotheses = []

        concept_set = set(concepts)

        if "certainty" in concept_set and "understanding" in concept_set:
            assumptions.append(
                "Certainty and understanding can evolve independently."
            )

            alternative_hypotheses.append(
                "Mecroyance may also emerge from emotional pressure, social reinforcement or contextual reduction."
            )

        if claims and not workspace.interpretations.get("knowledge", {}).get("sources"):
            uncertainties.append(
                "The claim is not connected to an explicit source."
            )

        if claims and len(relations) < 2:
            uncertainties.append(
                "The semantic relation structure is weak or underdeveloped."
            )

        if not alternative_hypotheses:
            alternative_hypotheses.append(
                "Alternative explanations should be explored if the claim becomes central to the diagnosis."
            )

        result = {
            "engine": self.name,
            "assumptions": assumptions,
            "uncertainties": uncertainties,
            "alternative_hypotheses": alternative_hypotheses,
            "assumption_count": len(assumptions),
            "uncertainty_count": len(uncertainties),
            "alternative_count": len(alternative_hypotheses),
            "source_semantic_claims": claims,
            "source_concepts": concepts,
            "source_relations": relations,
            "summary": "Semantic reasoning derived assumptions, uncertainties and alternatives.",
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

        workspace.add_interpretation(
            self.name,
            result,
        )

        return workspace
