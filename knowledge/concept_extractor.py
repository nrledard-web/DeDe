"""
DeDe - Concept Extractor

First symbolic concept extraction component.

The ConceptExtractor extracts simple concepts from text and knowledge
results, then writes them into the CognitiveWorkspace.

This is the first step toward a future Concept Graph.
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ConceptExtractor:
    """
    Extracts simple cognitive concepts.

    This is not yet a semantic graph.
    It produces a lightweight concept structure that future agents,
    especially NousAgent, will be able to use.
    """

    name = "concepts"

    def __init__(self):
        self.stopwords = {
            "what",
            "is",
            "the",
            "a",
            "an",
            "of",
            "and",
            "or",
            "to",
            "in",
            "on",
            "for",
            "with",
            "by",
            "from",
            "that",
            "this",
            "it",
            "as",
            "are",
            "be",
            "between",
            "which",
            "who",
            "why",
            "how",
        }

    def extract_from_text(self, text: str) -> list[str]:
        """
        Extract simple concepts from raw text.
        """

        cleaned = (
            text.lower()
            .replace(".", " ")
            .replace(",", " ")
            .replace("?", " ")
            .replace("!", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("(", " ")
            .replace(")", " ")
        )

        words = [
            word.strip()
            for word in cleaned.split()
            if word.strip()
        ]

        concepts = [
            word
            for word in words
            if word not in self.stopwords
            and len(word) > 2
        ]

        return list(dict.fromkeys(concepts))

    def build_relations(self, concepts: list[str]) -> list[dict[str, str]]:
        """
        Build very simple adjacent concept relations.
        """

        relations = []

        for index in range(len(concepts) - 1):
            relations.append(
                {
                    "source": concepts[index],
                    "target": concepts[index + 1],
                    "type": "adjacent_concept",
                }
            )

        return relations

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        """
        Extract concepts from the input text and available knowledge.
        """

        text_concepts = self.extract_from_text(workspace.text)

        knowledge = workspace.interpretations.get("knowledge", {})
        knowledge_answer = knowledge.get("answer", "")

        knowledge_concepts = []

        if knowledge.get("found") and knowledge_answer:
            knowledge_concepts = self.extract_from_text(knowledge_answer)

        all_concepts = list(
            dict.fromkeys(
                text_concepts + knowledge_concepts
            )
        )

        relations = self.build_relations(all_concepts)

        result = {
            "extractor": self.name,
            "text_concepts": text_concepts,
            "knowledge_concepts": knowledge_concepts,
            "main_concepts": all_concepts,
            "relations": relations,
            "concept_count": len(all_concepts),
            "relation_count": len(relations),
            "concept_density": min(
                1.0,
                len(relations) / max(1, len(all_concepts)),
            ),
            "summary": "Concepts extracted from text and available knowledge.",
        }

        workspace.set(
            "concept_count",
            len(all_concepts),
            {
                "extractor": self.name,
                "summary": "Number of extracted concepts.",
            },
        )
        
        workspace.set(
            "relation_count",
            len(relations),
            {
                "extractor": self.name,
                "summary": "Number of extracted concept relations.",
            },
        )
        
        workspace.set(
            "concept_density",
            min(
                1.0,
                len(relations) / max(1, len(all_concepts)),
            ),
            {
                "extractor": self.name,
                "summary": "Concept relation density.",
            },
        )

        workspace.add_interpretation(self.name, result)

        return workspace
