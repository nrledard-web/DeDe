"""
DeDe - Cognitive Feedback

Extracts structured cognitive feedback from an LLM response.

Preferred architecture:

LLM Response
    ↓
Structured JSON
    ↓
Cognitive feedback

When structured JSON is unavailable, the fallback remains
deliberately conservative and language-neutral.

The fallback does not attempt to infer cognitive concepts,
hypotheses or counterfactuals from language-specific markers.
"""

from __future__ import annotations

from typing import Any


class CognitiveFeedback:

    name = "cognitive_feedback"

    def analyze(
        self,
        llm_response: str | None,
        parsed_json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Preferred path: structured JSON from the LLM
        # --------------------------------------------------

        if isinstance(
            parsed_json,
            dict,
        ) and parsed_json:

            return {
                "engine": self.name,
                "status": "ready_from_json",

                "new_concepts": self._safe_list(
                    parsed_json.get(
                        "concepts",
                        [],
                    )
                ),

                "new_relations": self._safe_list(
                    parsed_json.get(
                        "relations",
                        [],
                    )
                ),

                "new_hypotheses": self._safe_list(
                    parsed_json.get(
                        "hypotheses",
                        [],
                    )
                ),

                "new_questions": self._safe_list(
                    parsed_json.get(
                        "questions",
                        [],
                    )
                ),

                "new_missing_dimensions": self._safe_list(
                    parsed_json.get(
                        "missing_dimensions",
                        [],
                    )
                ),

                "new_counterfactuals": self._safe_list(
                    parsed_json.get(
                        "counterfactuals",
                        [],
                    )
                ),

                "confidence": self._safe_level(
                    parsed_json.get(
                        "confidence",
                        0.0,
                    )
                ),

                "summary": str(
                    parsed_json.get(
                        "summary",
                        "Structured LLM feedback extracted from JSON.",
                    )
                    or "Structured LLM feedback extracted from JSON."
                ),

                "recommendations": self._safe_list(
                    parsed_json.get(
                        "recommendations",
                        [],
                    )
                ),

                "contradictions": self._safe_list(
                    parsed_json.get(
                        "contradictions",
                        [],
                    )
                ),

                "source": "llm_json",

                "language_specific_markers": False,
            }

        # --------------------------------------------------
        # No response
        # --------------------------------------------------

        if not llm_response:

            return self._empty_result(
                status="no_llm_response",
                summary=(
                    "No LLM response available "
                    "for feedback extraction."
                ),
                source="none",
            )

        # --------------------------------------------------
        # Language-neutral fallback
        # --------------------------------------------------
        #
        # We deliberately do NOT infer:
        #
        # - concepts from words such as "certainty"
        # - hypotheses from "may", "might", "could"
        # - missing dimensions from English phrases
        # - counterfactuals from "if", "unless", "would"
        #
        # Without structured JSON, these distinctions cannot
        # be extracted reliably across arbitrary languages.
        #
        # The raw response is preserved for later semantic
        # processing, but no cognitive inference is invented.
        # --------------------------------------------------

        cleaned_response = str(
            llm_response
        ).strip()

        sentence_count = self._estimate_sentence_count(
            cleaned_response
        )

        structural_confidence = min(
            0.25,
            sentence_count * 0.03,
        )

        return {
            "engine": self.name,
            "status": "fallback_unstructured",

            "new_concepts": [],
            "new_relations": [],
            "new_hypotheses": [],
            "new_questions": [],
            "new_missing_dimensions": [],
            "new_counterfactuals": [],

            "confidence": round(
                structural_confidence,
                3,
            ),

            "summary": (
                "Unstructured LLM feedback is available, "
                "but no language-specific cognitive inference "
                "was performed."
            ),

            "recommendations": [],
            "contradictions": [],

            "source": "llm_text_unstructured",

            "raw_feedback": (
                cleaned_response
            ),

            "sentence_count": (
                sentence_count
            ),

            "language_specific_markers": False,

            "structured_feedback_required": True,
        }

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _safe_list(
        value: Any,
    ) -> list[Any]:

        if isinstance(
            value,
            list,
        ):
            return value

        return []

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

    @staticmethod
    def _estimate_sentence_count(
        text: str,
    ) -> int:
        """
        Estimate textual segmentation structurally.

        This is not semantic inference.
        It only provides a conservative measure of response size.
        """

        if not text:
            return 0

        separators = (
            ".",
            "!",
            "?",
            "。",
            "！",
            "？",
        )

        count = sum(
            text.count(
                separator
            )
            for separator in separators
        )

        if count <= 0:
            return 1

        return count

    def _empty_result(
        self,
        status: str,
        summary: str,
        source: str,
    ) -> dict[str, Any]:

        return {
            "engine": self.name,
            "status": status,
            "new_concepts": [],
            "new_relations": [],
            "new_hypotheses": [],
            "new_questions": [],
            "new_missing_dimensions": [],
            "new_counterfactuals": [],
            "confidence": 0.0,
            "summary": summary,
            "recommendations": [],
            "contradictions": [],
            "source": source,
            "language_specific_markers": False,
        }
