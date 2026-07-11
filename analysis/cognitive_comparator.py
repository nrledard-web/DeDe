"""
DeDe - Cognitive Comparator

Compares the cognitive analysis of:
- the user message;
- retrieved web material;
- DeDe's final response.

The comparator detects shifts in grounding, certainty,
reduction and revisability without re-analyzing the texts.
"""

from __future__ import annotations

from typing import Any


class CognitiveComparator:

    name = "cognitive_comparator"

    VECTOR_KEYS = [
        "gnosis",
        "nous",
        "doxa",
        "reduction",
        "revisability",
    ]

    def compare(
        self,
        user_analysis: dict[str, Any] | None = None,
        web_analysis: dict[str, Any] | None = None,
        final_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        user_analysis = user_analysis or {}
        web_analysis = web_analysis or {}
        final_analysis = final_analysis or {}

        user_vector = self._extract_vector(
            user_analysis
        )

        web_vector = self._extract_web_vector(
            web_analysis
        )

        final_vector = self._extract_vector(
            final_analysis
        )

        source_to_response = self._compare_vectors(
            source=web_vector,
            target=final_vector,
        )

        user_to_response = self._compare_vectors(
            source=user_vector,
            target=final_vector,
        )

        warnings = self._build_warnings(
            web_vector=web_vector,
            final_vector=final_vector,
            source_to_response=source_to_response,
        )

        status = (
            "ready"
            if final_vector
            else "incomplete"
        )

        return {
            "engine": self.name,
            "status": status,
            "vectors": {
                "user": user_vector,
                "web": web_vector,
                "final_response": final_vector,
            },
            "source_to_response": source_to_response,
            "user_to_response": user_to_response,
            "warnings": warnings,
            "warning_count": len(warnings),
            "summary": self._build_summary(
                warnings=warnings,
                source_to_response=source_to_response,
            ),
        }

    def _extract_vector(
        self,
        analysis_result: dict[str, Any],
    ) -> dict[str, float]:

        vector = (
            analysis_result
            .get("analysis", {})
            .get("cognitive_vector", {})
        )

        return self._normalize_vector(
            vector
        )

    def _extract_web_vector(
        self,
        web_analysis: dict[str, Any],
    ) -> dict[str, float]:

        vector = (
            web_analysis
            .get("aggregate", {})
            .get("average_cognitive_vector", {})
        )

        return self._normalize_vector(
            vector
        )

    def _normalize_vector(
        self,
        vector: dict[str, Any],
    ) -> dict[str, float]:

        normalized = {}

        for key in self.VECTOR_KEYS:
            value = vector.get(key)

            if isinstance(value, (int, float)):
                normalized[key] = float(value)

        return normalized

    def _compare_vectors(
        self,
        source: dict[str, float],
        target: dict[str, float],
    ) -> dict[str, float | None]:

        comparison = {}

        for key in self.VECTOR_KEYS:
            source_value = source.get(key)
            target_value = target.get(key)

            if source_value is None or target_value is None:
                comparison[f"{key}_shift"] = None
                continue

            comparison[f"{key}_shift"] = (
                target_value - source_value
            )

        return comparison

    def _build_warnings(
        self,
        web_vector: dict[str, float],
        final_vector: dict[str, float],
        source_to_response: dict[str, float | None],
    ) -> list[dict[str, Any]]:

        warnings = []

        if not web_vector or not final_vector:
            return warnings

        doxa_shift = source_to_response.get(
            "doxa_shift"
        )

        gnosis_shift = source_to_response.get(
            "gnosis_shift"
        )

        reduction_shift = source_to_response.get(
            "reduction_shift"
        )

        revisability_shift = source_to_response.get(
            "revisability_shift"
        )

        if (
            isinstance(doxa_shift, float)
            and doxa_shift > 0.15
        ):
            warnings.append(
                {
                    "type": "certainty_amplification",
                    "severity": "medium",
                    "message": (
                        "The final response is significantly more "
                        "certain than the retrieved material."
                    ),
                    "value": doxa_shift,
                }
            )

        if (
            isinstance(gnosis_shift, float)
            and isinstance(doxa_shift, float)
            and doxa_shift > 0.10
            and gnosis_shift <= 0
        ):
            warnings.append(
                {
                    "type": "unsupported_certainty",
                    "severity": "high",
                    "message": (
                        "Certainty increased without a corresponding "
                        "increase in articulated knowledge."
                    ),
                    "value": doxa_shift,
                }
            )

        if (
            isinstance(reduction_shift, float)
            and reduction_shift > 0.15
        ):
            warnings.append(
                {
                    "type": "reduction_increase",
                    "severity": "medium",
                    "message": (
                        "The final response appears more reductive "
                        "than the retrieved material."
                    ),
                    "value": reduction_shift,
                }
            )

        if (
            isinstance(revisability_shift, float)
            and revisability_shift < -0.15
        ):
            warnings.append(
                {
                    "type": "revisability_loss",
                    "severity": "high",
                    "message": (
                        "The final response is less revisable than "
                        "the retrieved material."
                    ),
                    "value": revisability_shift,
                }
            )

        return warnings

    def _build_summary(
        self,
        warnings: list[dict[str, Any]],
        source_to_response: dict[str, float | None],
    ) -> str:

        if not source_to_response:
            return (
                "Cognitive comparison could not be completed."
            )

        if not warnings:
            return (
                "No major cognitive distortion was detected between "
                "the retrieved material and DeDe's final response."
            )

        return (
            f"{len(warnings)} cognitive warning(s) detected between "
            "the retrieved material and DeDe's final response."
        )
