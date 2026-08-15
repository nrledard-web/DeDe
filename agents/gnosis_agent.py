"""
DeDe - Gnosis Agent

Language-neutral Gnosis agent.

The Gnosis Agent evaluates articulated knowledge and grounding
from structured cognitive state rather than language-specific
keywords.

It deliberately avoids textual markers such as:
- fact
- source
- evidence
- maybe
- true
- false

Mentioning such words does not itself constitute knowledge
or grounding.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_state import CognitiveState
from core.cognitive_dynamics import GroundingDynamic
from interfaces.cognitive_agent import CognitiveAgent


class GnosisAgent(CognitiveAgent):
    """
    Cognitive agent responsible for interpreting knowledge grounding.

    This legacy-state agent remains compatible with CognitiveState,
    but no longer estimates Gnosis from vocabulary.
    """

    name = "gnosis"

    def can_handle(
        self,
        state: CognitiveState,
    ) -> bool:
        """
        Gnosis can evaluate any non-empty cognitive state.

        Whether factual verification is required should be decided
        by the knowledge/search/governor layers, not by English words
        contained in the user's message.
        """

        user_input = str(
            getattr(
                state,
                "user_input",
                "",
            )
            or ""
        ).strip()

        return bool(
            user_input
        )

    def analyze(
        self,
        state: CognitiveState,
    ) -> dict[str, Any]:
        """
        Produce a language-neutral Gnosis analysis.

        Priority:
        1. structured grounding already available in CognitiveState;
        2. structured knowledge confidence if available;
        3. conservative fallback when no grounding signal exists.
        """

        # --------------------------------------------------
        # Structured state signals
        # --------------------------------------------------

        grounding_signal = self._first_level(
            state,
            [
                "grounding",
                "grounding_level",
                "grounding_score",
                "knowledge_grounding",
                "source_confidence",
            ],
        )

        knowledge_confidence = self._first_level(
            state,
            [
                "knowledge_confidence",
                "factual_confidence",
                "evidence_confidence",
            ],
        )

        existing_gnosis = self._first_level(
            state,
            [
                "gnosis_level",
                "gnosis",
            ],
        )

        # --------------------------------------------------
        # Determine base Gnosis
        # --------------------------------------------------
        #
        # Absence of structured grounding is NOT interpreted
        # as falsehood. It simply means insufficient evidence
        # for a strong Gnosis score.
        # --------------------------------------------------

        available_signals = [
            value
            for value in [
                grounding_signal,
                knowledge_confidence,
                existing_gnosis,
            ]
            if value is not None
        ]

        if available_signals:

            base_gnosis_level = (
                sum(
                    available_signals
                )
                / len(
                    available_signals
                )
            )

            grounding_available = True

        else:

            base_gnosis_level = 0.20

            grounding_available = False

        base_gnosis_level = self._safe_level(
            base_gnosis_level
        )

        # --------------------------------------------------
        # Grounding Dynamic
        # --------------------------------------------------

        grounding_dynamic = (
            GroundingDynamic().evaluate(
                {
                    "grounding_signal": (
                        base_gnosis_level
                    ),
                }
            )
        )

        dynamic_value = self._safe_level(
            getattr(
                grounding_dynamic,
                "value",
                0.0,
            )
        )

        gnosis_effect = (
            dynamic_value
            * 0.20
        )

        gnosis_level = self._safe_level(
            base_gnosis_level
            + gnosis_effect
        )

        # --------------------------------------------------
        # Verification state
        # --------------------------------------------------
        #
        # Verification is needed when grounding is absent
        # or still weak.
        #
        # This decision is structural, not lexical.
        # --------------------------------------------------

        verification_needed = (
            not grounding_available
            or gnosis_level < 0.45
        )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        result = {
            "agent": self.name,

            "gnosis_level": (
                gnosis_level
            ),

            "base_gnosis_level": (
                base_gnosis_level
            ),

            "grounding_available": (
                grounding_available
            ),

            "grounding_signal": (
                grounding_signal
            ),

            "knowledge_confidence": (
                knowledge_confidence
            ),

            "verification_needed": (
                verification_needed
            ),

            "language_specific_markers": (
                False
            ),

            "summary": (
                "Knowledge grounding remains insufficient "
                "and verification is recommended."
                if verification_needed
                else
                "Available structured grounding supports "
                "the current Gnosis estimate."
            ),

            "grounding_dynamic": {
                "value": (
                    dynamic_value
                ),

                "gnosis_effect": (
                    gnosis_effect
                ),

                "description": str(
                    getattr(
                        grounding_dynamic,
                        "description",
                        "",
                    )
                    or ""
                ),
            },
        }

        # --------------------------------------------------
        # Preserve legacy CognitiveState behavior
        # --------------------------------------------------

        try:
            state.gnosis_level = (
                gnosis_level
            )

        except Exception:
            pass

        return result

    # ======================================================
    # Helpers
    # ======================================================

    def _first_level(
        self,
        state: CognitiveState,
        names: list[str],
    ) -> float | None:
        """
        Return the first usable structured numeric signal.
        """

        for name in names:

            value = getattr(
                state,
                name,
                None,
            )

            if value is None:
                continue

            try:
                numeric = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            return self._safe_level(
                numeric
            )

        return None

    @staticmethod
    def _safe_level(
        value: Any,
    ) -> float:
        """
        Normalize a numeric value to DeDe's 0..1 scale.
        """

        try:
            level = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if level > 1.0:
            level = (
                level / 100.0
            )

        return max(
            0.0,
            min(
                1.0,
                level,
            ),
        )
