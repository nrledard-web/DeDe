"""
DeDe - Concept Extractor

Language-neutral symbolic concept extraction component.

The ConceptExtractor extracts lightweight candidate concepts
from text and available knowledge, then writes them into the
CognitiveWorkspace.

It deliberately avoids language-specific stopword lists.

This component does not claim that every extracted token is a
fully resolved semantic concept. It provides a neutral structural
representation for later semantic reasoning.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class ConceptExtractor:
    """
    Extracts lightweight concept candidates.

    The extractor is intentionally language-neutral.

    It does not use English, French or other language-specific
    stopword lists.

    Semantic interpretation belongs to later cognitive layers.
    """

    name = "concepts"

    # ======================================================
    # Text normalization
    # ======================================================

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        """
        Normalize Unicode and case without translating
        or imposing a language.
        """

        text = str(
            text or ""
        )

        text = unicodedata.normalize(
            "NFKC",
            text,
        )

        return text.casefold()

    # ======================================================
    # Token extraction
    # ======================================================

    def extract_from_text(
        self,
        text: str,
    ) -> list[str]:
        """
        Extract language-neutral candidate concepts.

        Rules are structural rather than lexical:

        - Unicode words are accepted;
        - punctuation is ignored;
        - very short tokens are ignored;
        - pure punctuation is ignored;
        - duplicates are removed while preserving order.

        No language-specific stopwords are used.
        """

        normalized = self._normalize_text(
            text
        )

        # Unicode-aware word extraction.
        #
        # Python's \w includes letters from many writing
        # systems, digits and underscore.
        tokens = re.findall(
            r"[^\W_]+(?:['’\-][^\W_]+)*",
            normalized,
            flags=re.UNICODE,
        )

        concepts = []

        seen = set()

        for token in tokens:

            token = token.strip(
                "'’-"
            )

            if not token:
                continue

            # ----------------------------------------------
            # Structural filtering
            # ----------------------------------------------

            # Very short tokens generally carry too little
            # conceptual information at this primitive layer.
            if len(token) <= 2:
                continue

            # Pure numbers are not treated as concepts here.
            # They may still be represented later as evidence,
            # quantities or dates by specialized components.
            if token.isdigit():
                continue

            if token in seen:
                continue

            seen.add(
                token
            )

            concepts.append(
                token
            )

        return concepts

    # ======================================================
    # Relations
    # ======================================================

    def build_relations(
        self,
        concepts: list[str],
    ) -> list[dict[str, str]]:
        """
        Build lightweight adjacency relations.

        Adjacency does not imply causality, truth or semantic
        equivalence. It only preserves local structural order.
        """

        relations = []

        for index in range(
            len(concepts) - 1
        ):

            relations.append(
                {
                    "source": (
                        concepts[index]
                    ),
                    "target": (
                        concepts[index + 1]
                    ),
                    "type": (
                        "adjacent_concept"
                    ),
                }
            )

        return relations

    # ======================================================
    # Main pipeline
    # ======================================================

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:
        """
        Extract candidate concepts from user text and
        available knowledge.
        """

        text_concepts = (
            self.extract_from_text(
                workspace.text
            )
        )

        knowledge = (
            workspace.interpretations.get(
                "knowledge",
                {},
            )
        )

        if not isinstance(
            knowledge,
            dict,
        ):
            knowledge = {}

        knowledge_answer = str(
            knowledge.get(
                "answer",
                "",
            )
            or ""
        )

        knowledge_concepts = []

        if (
            knowledge.get(
                "found",
                False,
            )
            and knowledge_answer
        ):

            knowledge_concepts = (
                self.extract_from_text(
                    knowledge_answer
                )
            )

        # --------------------------------------------------
        # Merge while preserving order
        # --------------------------------------------------

        all_concepts = list(
            dict.fromkeys(
                text_concepts
                + knowledge_concepts
            )
        )

        relations = (
            self.build_relations(
                all_concepts
            )
        )

        concept_count = len(
            all_concepts
        )

        relation_count = len(
            relations
        )

        concept_density = min(
            1.0,
            relation_count
            / max(
                1,
                concept_count,
            ),
        )

        result = {
            "extractor": self.name,

            "text_concepts": (
                text_concepts
            ),

            "knowledge_concepts": (
                knowledge_concepts
            ),

            "main_concepts": (
                all_concepts
            ),

            "relations": (
                relations
            ),

            "concept_count": (
                concept_count
            ),

            "relation_count": (
                relation_count
            ),

            "concept_density": (
                concept_density
            ),

            "language_specific_filtering": (
                False
            ),

            "summary": (
                "Language-neutral concept candidates extracted "
                "from text and available knowledge."
            ),
        }

        workspace.set_raw(
            "concept_count",
            concept_count,
            {
                "extractor": self.name,
                "summary": (
                    "Number of extracted "
                    "concept candidates."
                ),
            },
        )

        workspace.set_raw(
            "relation_count",
            relation_count,
            {
                "extractor": self.name,
                "summary": (
                    "Number of lightweight "
                    "concept relations."
                ),
            },
        )

        workspace.set(
            "concept_density",
            concept_density,
            {
                "extractor": self.name,
                "summary": (
                    "Structural concept relation density."
                ),
            },
        )

        workspace.add_interpretation(
            self.name,
            result,
        )

        return workspace
