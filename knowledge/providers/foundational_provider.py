"""
DeDe - Foundational Knowledge Provider

Provides DeDe's official cognitive concepts from the
stable foundational knowledge constitution.

The provider does not perform language-specific semantic
classification.

Semantic interpretation belongs upstream.

This provider resolves canonical DeDe concepts and returns
their official foundational definitions.
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
    Resolve DeDe's official foundational concepts.

    The provider accepts:
    - canonical concept identifiers produced upstream;
    - direct references to DeDe-specific proper concepts;
    - official formulas and symbolic identifiers.

    It deliberately avoids multilingual lexical alias lists.
    """

    name = "dede_foundational_knowledge"

    def __init__(
        self,
    ) -> None:

        self.concept_keys = set(
            FOUNDATIONAL_KNOWLEDGE.keys()
        )

        # --------------------------------------------------
        # Stable DeDe-specific surface identifiers
        # --------------------------------------------------
        #
        # These are not language translations.
        # They are project names, coined terms or canonical
        # symbolic forms that remain stable across languages.
        # --------------------------------------------------

        self.surface_identifiers = {
            "dede": "project",
            "daimon": "daimon",
            "nouscope": "nouscope",
            "mecroyance": "mecroyance",
            "mécroyance": "mecroyance",
            "mecroire": "mecroyance",
            "mécroire": "mecroyance",
            "anti-coherence loop": (
                "anti_coherence_loop"
            ),
            "anti coherence loop": (
                "anti_coherence_loop"
            ),
        }

    # ======================================================
    # Public search
    # ======================================================

    def search(
        self,
        query: str,
        canonical_concepts: (
            list[str] | None
        ) = None,
    ) -> dict[str, Any]:
        """
        Resolve foundational knowledge.

        canonical_concepts should contain semantic concept
        identifiers produced by an upstream classifier.

        The raw query is used only for direct references to
        stable DeDe-specific terms, formulas or canonical keys.
        """

        normalized_query = self._normalize(
            query
        )

        normalized_concepts = (
            self._normalize_canonical_concepts(
                canonical_concepts
            )
        )

        matched_key = (
            self._find_from_canonical_concepts(
                normalized_concepts
            )
        )

        resolution_method = (
            "canonical_concept"
            if matched_key
            else None
        )

        if not matched_key:
            matched_key = (
                self._find_from_direct_reference(
                    normalized_query
                )
            )

            if matched_key:
                resolution_method = (
                    "direct_reference"
                )

        if not matched_key:
            matched_key = (
                self._find_from_formula(
                    query
                )
            )

            if matched_key:
                resolution_method = (
                    "formula"
                )

        if not matched_key:
            return self._not_found(
                query=normalized_query,
                canonical_concepts=(
                    normalized_concepts
                ),
            )

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
            "found": bool(
                answer
            ),
            "confidence": 0.98,
            "concept": matched_key,
            "canonical_concepts": (
                normalized_concepts
            ),
            "resolution_method": (
                resolution_method
            ),
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

    # ======================================================
    # Canonical semantic resolution
    # ======================================================

    def _find_from_canonical_concepts(
        self,
        canonical_concepts: list[str],
    ) -> str | None:
        """
        Resolve concepts already classified upstream.

        No linguistic interpretation occurs here.
        """

        for concept in canonical_concepts:

            normalized_key = (
                self._normalize_identifier(
                    concept
                )
            )

            if normalized_key in self.concept_keys:
                return normalized_key

        return None

    # ======================================================
    # Direct DeDe-specific references
    # ======================================================

    def _find_from_direct_reference(
        self,
        normalized_query: str,
    ) -> str | None:
        """
        Recognize only stable DeDe-specific identifiers.

        This is not intended to translate ordinary language.
        """

        if not normalized_query:
            return None

        # ----------------------------------------------
        # Canonical dictionary keys
        # ----------------------------------------------

        key_matches = []

        for concept_key in self.concept_keys:

            surface_key = self._normalize(
                concept_key.replace(
                    "_",
                    " ",
                )
            )

            if (
                surface_key
                and self._contains_phrase(
                    normalized_query,
                    surface_key,
                )
            ):
                key_matches.append(
                    (
                        len(surface_key),
                        concept_key,
                    )
                )

        # ----------------------------------------------
        # Stable project terms
        # ----------------------------------------------

        for surface, concept_key in (
            self.surface_identifiers.items()
        ):

            normalized_surface = (
                self._normalize(
                    surface
                )
            )

            if (
                normalized_surface
                and self._contains_phrase(
                    normalized_query,
                    normalized_surface,
                )
            ):
                key_matches.append(
                    (
                        len(normalized_surface),
                        concept_key,
                    )
                )

        if not key_matches:
            return None

        key_matches.sort(
            reverse=True
        )

        return key_matches[0][1]

    # ======================================================
    # Formula resolution
    # ======================================================

    def _find_from_formula(
        self,
        query: str,
    ) -> str | None:
        """
        Recognize DeDe's symbolic formulas independently
        of the surrounding language.
        """

        compact = re.sub(
            r"\s+",
            "",
            str(query or "").upper(),
        )

        if not compact:
            return None

        mechanics_signatures = [
            "M=(G+N)-D",
            "M=G+N-D",
        ]

        if any(
            signature in compact
            for signature
            in mechanics_signatures
        ):
            return "cognitive_mechanics"

        derived_signatures = [
            "SC=D-(G+N)",
            "CR=D/(G+N)",
            "RV=(G+N+V)-D",
            "CC=MAX(0,D-(G_DRIFT+N))",
            "PS=MAX(0,(G_DRIFT+D)-N)",
            "ID=MAX(0,(N+D)-G_DRIFT)",
        ]

        if any(
            signature in compact
            for signature
            in derived_signatures
        ):
            return "derived_formulas"

        return None

    # ======================================================
    # Answer construction
    # ======================================================

    def _build_answer(
        self,
        concept_key: str,
        entry: Any,
    ) -> str:
        """
        Build a deterministic foundational answer.

        Translation or conversational reformulation belongs
        to the reasoning model downstream.
        """

        concept_label = (
            concept_key.replace(
                "_",
                " ",
            ).title()
        )

        if isinstance(
            entry,
            str,
        ):
            return entry

        if isinstance(
            entry,
            list,
        ):
            return (
                f"{concept_label}: "
                + " ".join(
                    str(item)
                    for item in entry
                )
            )

        if not isinstance(
            entry,
            dict,
        ):
            return str(
                entry
            )

        answer_parts = []

        preferred_fields = [
            "definition",
            "identity",
            "principle",
            "purpose",
            "mission",
            "objective",
            "official_formula",
            "general_mecroyance",
            "cognitive_closure_mecroyance",
            "spectrum_principle",
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

        if isinstance(
            variables,
            dict,
        ):
            for variable, meaning in (
                variables.items()
            ):
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

    # ======================================================
    # Helpers
    # ======================================================

    def _normalize_canonical_concepts(
        self,
        concepts: list[str] | None,
    ) -> list[str]:
        """
        Normalize structured semantic identifiers.
        """

        if not isinstance(
            concepts,
            list,
        ):
            return []

        normalized = []

        seen = set()

        for concept in concepts:

            identifier = (
                self._normalize_identifier(
                    concept
                )
            )

            if (
                not identifier
                or identifier in seen
            ):
                continue

            seen.add(
                identifier
            )

            normalized.append(
                identifier
            )

        return normalized

    def _normalize_identifier(
        self,
        value: Any,
    ) -> str:
        """
        Normalize a canonical concept identifier.
        """

        normalized = str(
            value or ""
        ).strip().casefold()

        normalized = re.sub(
            r"[\s\-]+",
            "_",
            normalized,
        )

        normalized = re.sub(
            r"_+",
            "_",
            normalized,
        )

        return normalized.strip(
            "_"
        )

    def _normalize(
        self,
        text: Any,
    ) -> str:
        """
        Unicode-preserving normalization.

        Unlike the previous implementation, this does not
        remove non-Latin writing systems.
        """

        normalized = unicodedata.normalize(
            "NFKC",
            str(
                text or ""
            ),
        ).casefold()

        normalized = re.sub(
            r"[^\w]+",
            " ",
            normalized,
            flags=re.UNICODE,
        )

        return " ".join(
            normalized.split()
        )

    def _contains_phrase(
        self,
        text: str,
        phrase: str,
    ) -> bool:
        """
        Structural phrase containment after normalization.
        """

        if not text or not phrase:
            return False

        padded_text = (
            f" {text} "
        )

        padded_phrase = (
            f" {phrase} "
        )

        return (
            padded_phrase
            in padded_text
        )

    def _not_found(
        self,
        query: str,
        canonical_concepts: list[str],
    ) -> dict[str, Any]:
        """
        Return a normalized empty result.
        """

        return {
            "provider": self.name,
            "query": query,
            "answer": (
                "Knowledge not found in "
                "DeDe foundational knowledge."
            ),
            "found": False,
            "confidence": 0.0,
            "concept": None,
            "canonical_concepts": (
                canonical_concepts
            ),
            "resolution_method": None,
            "entry": {},
            "sources": [
                {
                    "type": "foundational",
                    "name": self.name,
                    "confidence": 0.0,
                }
            ],
        }
