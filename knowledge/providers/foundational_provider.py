"""
DeDe - Foundational Knowledge Provider

Provides DeDe's official cognitive concepts from the
stable foundational knowledge constitution.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from knowledge.foundational_knowledge import (
    FOUNDATIONAL_KNOWLEDGE,
)


class FoundationalProvider:
    """
    Search DeDe's official foundational concepts.
    """

    name = "dede_foundational_knowledge"

    def __init__(self) -> None:
        self.aliases = {
            "project": [
                "dede",
                "cognitive daimon",
            ],
            "cognitive_reduction": [
                "cognitive reduction",
                "reduction cognitive",
                "reduction",
            ],
            "nouscope": [
                "nouscope",
            ],
            "continuity_of_understanding": [
                "continuity of understanding",
                "continuite de la comprehension",
            ],
            "cognitive_mechanics": [
                "cognitive mechanics",
                "mecanique cognitive",
                "m g n d",
            ],
            "mecroyance": [
                "mecroyance",
                "mecroire",
            ],
            "derived_formulas": [
                "derived formulas",
                "formules derivees",
                "surconfidence",
                "relative calibration",
                "calibration relative",
            ],
            "revisability": [
                "revisability",
                "revisabilite",
            ],
            "anti_coherence_loop": [
                "anti coherence loop",
                "boucle anti coherence",
            ],
            "cognitive_therapy": [
                "cognitive therapy",
                "therapie cognitive",
            ],
            "daimon": [
                "daimon",
            ],
            "behavioral_rules": [
                "behavioral rules",
                "regles comportementales",
            ],
        }

    def search(
        self,
        query: str,
    ) -> dict[str, Any]:
        """
        Search foundational concepts without depending on
        fixed question formulations.
        """

        normalized_query = self._normalize(
            query
        )

        matched_key = self._find_concept_key(
            normalized_query
        )

        if not matched_key:
            return {
                "provider": self.name,
                "query": normalized_query,
                "answer": (
                    "Knowledge not found in "
                    "DeDe foundational knowledge."
                ),
                "found": False,
                "confidence": 0.0,
                "concept": None,
                "entry": {},
                "sources": [
                    {
                        "type": "foundational",
                        "name": self.name,
                        "confidence": 0.0,
                    }
                ],
            }

        entry = FOUNDATIONAL_KNOWLEDGE.get(
            matched_key,
            {},
        )

        answer = self._build_answer(
            concept_key=matched_key,
            entry=entry,
        )

        return {
            "provider": self.name,
            "query": normalized_query,
            "answer": answer,
            "found": bool(answer),
            "confidence": 0.98,
            "concept": matched_key,
            "entry": entry,
            "sources": [
                {
                    "type": "foundational",
                    "name": self.name,
                    "concept": matched_key,
                    "confidence": 0.98,
                }
            ],
        }

    def _find_concept_key(
        self,
        normalized_query: str,
    ) -> str | None:
        """
        Find the most specific matching concept.
        """

        matches = []

        for concept_key, aliases in self.aliases.items():
            candidates = [
                concept_key.replace(
                    "_",
                    " ",
                ),
                *aliases,
            ]

            for candidate in candidates:
                normalized_candidate = self._normalize(
                    candidate
                )

                if (
                    normalized_candidate
                    and normalized_candidate
                    in normalized_query
                ):
                    matches.append(
                        (
                            len(normalized_candidate),
                            concept_key,
                        )
                    )

        if not matches:
            return None

        matches.sort(
            reverse=True
        )

        return matches[0][1]

    def _build_answer(
        self,
        concept_key: str,
        entry: Any,
    ) -> str:
        """
        Build a deterministic answer without an LLM.
        """

        concept_label = concept_key.replace(
            "_",
            " ",
        ).title()

        if isinstance(entry, str):
            return entry

        if isinstance(entry, list):
            return (
                f"{concept_label}: "
                + " ".join(
                    str(item)
                    for item in entry
                )
            )

        if not isinstance(entry, dict):
            return str(entry)

        answer_parts = []

        preferred_fields = [
            "definition",
            "identity",
            "principle",
            "purpose",
            "mission",
            "objective",
            "official_formula",
            "root_cause",
        ]

        for field in preferred_fields:
            value = entry.get(
                field
            )

            if value:
                answer_parts.append(
                    str(value)
                )

        variables = entry.get(
            "variables",
            {},
        )

        if isinstance(variables, dict):
            for variable, meaning in variables.items():
                answer_parts.append(
                    f"{variable}: {meaning}"
                )

        if not answer_parts:
            for value in entry.values():
                if isinstance(
                    value,
                    str,
                ):
                    answer_parts.append(
                        value
                    )

        if not answer_parts:
            return (
                f"{concept_label} is present in "
                "DeDe foundational knowledge."
            )

        return " ".join(
            answer_parts
        )

    def _normalize(
        self,
        text: str,
    ) -> str:
        """
        Normalize accents, punctuation and spacing.
        """

        normalized = unicodedata.normalize(
            "NFKD",
            str(text or "").lower(),
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(
                character
            )
        )

        normalized = re.sub(
            r"[^a-z0-9]+",
            " ",
            normalized,
        )

        return " ".join(
            normalized.split()
        )
