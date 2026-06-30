"""
DeDe - Semantic Engine

First symbolic semantic engine.

The SemanticEngine builds a lightweight meaning representation
from the CognitiveWorkspace.

It does not answer the user.
It extracts semantic structures:
- claims
- concepts
- relations
- assumptions
- uncertainties
- alternative hypotheses

Future versions may use LLMs, embeddings or semantic graphs.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class SemanticEngine:
    """
    Builds a first semantic representation of the analyzed text.
    """

    name = "semantic"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        """
        Build semantic structures from knowledge and concepts.
        """

        text = workspace.text

        knowledge = workspace.interpretations.get("knowledge", {})
        concepts = workspace.interpretations.get("concepts", {})

        answer = knowledge.get("answer", "")
        found = knowledge.get("found", False)

        main_concepts = concepts.get("main_concepts", [])
        concept_relations = concepts.get("relations", [])

        claims = []

        if found and answer:
            claims.append(answer)

        elif text:
            claims.append(text)

        semantic_relations = []

        for relation in concept_relations:
            semantic_relations.append(
                {
                    "source": relation.get("source"),
                    "relation": relation.get("type", "related_to"),
                    "target": relation.get("target"),
                }
            )

        assumptions = []

        uncertainties = []

        if not found:
            uncertainties.append(
                "Knowledge could not be found in the available providers."
            )

        alternative_hypotheses = []

        result = {
            "engine": self.name,
            "claims": claims,
            "main_concepts": main_concepts,
            "relations": semantic_relations,
            "assumptions": assumptions,
            "uncertainties": uncertainties,
            "alternative_hypotheses": alternative_hypotheses,
            "claim_count": len(claims),
            "concept_count": len(main_concepts),
            "relation_count": len(semantic_relations),
            "uncertainty_count": len(uncertainties),
            "summary": "Semantic representation built from knowledge and concepts.",
        }

        workspace.set_raw(
            "claim_count",
            len(claims),
            {
                "engine": self.name,
                "summary": "Number of semantic claims.",
            },
        )

        workspace.set_raw(
            "semantic_relation_count",
            len(semantic_relations),
            {
                "engine": self.name,
                "summary": "Number of semantic relations.",
            },
        )

        workspace.set_raw(
            "uncertainty_count",
            len(uncertainties),
            {
                "engine": self.name,
                "summary": "Number of semantic uncertainties.",
            },
        )

        workspace.add_interpretation(
            self.name,
            result,
        )

        return workspace
