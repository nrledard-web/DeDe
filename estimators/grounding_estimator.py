"""
DeDe - Grounding Estimator

Estimates factual grounding from available cognitive evidence.

Grounding must not depend on language-specific words used by
the speaker. Mentioning "proof", "study", "source" or equivalent
terms does not itself constitute grounding.

The estimator therefore uses available knowledge and evaluated
source material when present.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class GroundingEstimator:
    """
    Estimates factual grounding.

    Grounding represents available evidential support,
    not the vocabulary used by the speaker.
    """

    name = "grounding"

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        # --------------------------------------------------
        # Knowledge contribution
        # --------------------------------------------------

        knowledge = workspace.interpretations.get(
            "knowledge",
            {},
        )

        if not isinstance(
            knowledge,
            dict,
        ):
            knowledge = {}

        knowledge_found = bool(
            knowledge.get(
                "found",
                False,
            )
        )

        knowledge_confidence = self._safe_level(
            knowledge.get(
                "confidence",
                0.0,
            )
        )

        if knowledge_found:
            knowledge_grounding = (
                0.20
                + knowledge_confidence * 0.35
            )
        else:
            knowledge_grounding = 0.0

        # --------------------------------------------------
        # Source-analysis contribution
        # --------------------------------------------------

        source_analysis = workspace.interpretations.get(
            "source_analysis",
            {},
        )

        if not isinstance(
            source_analysis,
            dict,
        ):
            source_analysis = {}

        sources = source_analysis.get(
            "sources",
            [],
        )

        if not isinstance(
            sources,
            list,
        ):
            sources = []

        evidence_values = []
        relevance_values = []
        independence_values = []

        for source in sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            analysis = source.get(
                "analysis",
                {},
            )

            if not isinstance(
                analysis,
                dict,
            ):
                continue

            evidence_values.append(
                self._safe_level(
                    analysis.get(
                        "evidence_level",
                        0.0,
                    )
                )
            )

            relevance_values.append(
                self._safe_level(
                    analysis.get(
                        "relevance",
                        0.0,
                    )
                )
            )

            independence_values.append(
                self._safe_level(
                    analysis.get(
                        "independence",
                        0.0,
                    )
                )
            )

        evidence = self._average(
            evidence_values
        )

        relevance = self._average(
            relevance_values
        )

        independence = self._average(
            independence_values
        )

        source_count = len(
            evidence_values
        )

        source_presence = min(
            1.0,
            source_count / 4.0,
        )

        source_grounding = (
            evidence * 0.45
            + relevance * 0.20
            + independence * 0.20
            + source_presence * 0.15
        )

        # --------------------------------------------------
        # Final grounding
        # --------------------------------------------------
        #
        # A small neutral floor means "not yet grounded",
        # not "false".
        # --------------------------------------------------

        neutral_floor = 0.10

        score = max(
            neutral_floor,
            knowledge_grounding,
            source_grounding,
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

                "knowledge_found": (
                    knowledge_found
                ),

                "knowledge_confidence": (
                    knowledge_confidence
                ),

                "knowledge_grounding": round(
                    knowledge_grounding,
                    3,
                ),

                "source_count": (
                    source_count
                ),

                "visible_evidence": round(
                    evidence,
                    3,
                ),

                "source_relevance": round(
                    relevance,
                    3,
                ),

                "source_independence": round(
                    independence,
                    3,
                ),

                "source_grounding": round(
                    source_grounding,
                    3,
                ),

                "summary": (
                    "Grounding estimated from available knowledge "
                    "and evaluated evidence, independently of the "
                    "language used by the speaker."
                ),
            },
        )

        return workspace

    @staticmethod
    def _average(
        values: list[float],
    ) -> float:

        if not values:
            return 0.0

        return sum(
            values
        ) / len(
            values
        )

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
