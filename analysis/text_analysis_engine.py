"""
DeDe - Universal Text Analysis Engine

Provides one common cognitive-analysis interface for text originating from:
- the user;
- web search results;
- documents;
- memory;
- LLM responses;
- DeDe's final answer.

This engine does not duplicate cognitive detectors.
It wraps the existing DetectorEngine and preserves provenance.
"""

from __future__ import annotations

from typing import Any

from core.cognitive_state import CognitiveState
from detectors.detector_engine import DetectorEngine


class TextAnalysisEngine:
    """
    Universal entry point for symbolic cognitive text analysis.
    """

    name = "text_analysis_engine"

    def __init__(self) -> None:
        self.detector_engine = DetectorEngine()

    def analyze(
        self,
        text: str,
        source_type: str = "unknown",
        provenance: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze one text while preserving its origin and context.

        Parameters
        ----------
        text:
            Text to analyze.

        source_type:
            Origin of the text, for example:
            user, web, document, memory, llm or final_response.

        provenance:
            Information about the origin of the text:
            provider, URL, title, model, document name, etc.

        context:
            Optional contextual information supplied to CognitiveState.
        """

        provenance = provenance or {}
        context = context or {}

        normalized_source_type = (
            str(source_type or "unknown")
            .strip()
            .lower()
        )

        cleaned_text = str(text or "").strip()

        if not cleaned_text:
            return self._empty_result(
                source_type=normalized_source_type,
                provenance=provenance,
            )

        state = CognitiveState(
            user_input=cleaned_text,
            context={
                **context,
                "analysis_source_type": normalized_source_type,
                "analysis_provenance": provenance,
            },
        )

        detector_results = self.detector_engine.analyze(
            state
        )

        summary = self._build_summary(
            detector_results
        )

        return {
            "engine": self.name,
            "status": "ready",
            "source_type": normalized_source_type,
            "provenance": provenance,
            "text": cleaned_text,
            "text_preview": self._build_preview(
                cleaned_text
            ),
            "analysis": detector_results,
            "summary": summary,
        }

    def analyze_many(
        self,
        items: list[dict[str, Any]],
        source_type: str = "unknown",
        shared_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze several text items independently.

        Each item may contain:
        - text
        - provenance
        - context
        - source_type
        """

        shared_context = shared_context or {}

        analyses = []

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            item_text = str(
                item.get("text", "")
                or ""
            ).strip()

            if not item_text:
                continue

            item_source_type = item.get(
                "source_type",
                source_type,
            )

            item_provenance = {
                "index": index,
                **(
                    item.get(
                        "provenance",
                        {},
                    )
                    or {}
                ),
            }

            item_context = {
                **shared_context,
                **(
                    item.get(
                        "context",
                        {},
                    )
                    or {}
                ),
            }

            analyses.append(
                self.analyze(
                    text=item_text,
                    source_type=item_source_type,
                    provenance=item_provenance,
                    context=item_context,
                )
            )

        return {
            "engine": self.name,
            "status": (
                "ready"
                if analyses
                else "empty"
            ),
            "source_type": source_type,
            "item_count": len(analyses),
            "items": analyses,
            "aggregate": self._aggregate(
                analyses
            ),
        }

    def _build_summary(
        self,
        detector_results: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract the principal cognitive values into a compact summary.
        """

        vector = detector_results.get(
            "cognitive_vector",
            {},
        )

        metrics = detector_results.get(
            "metrics",
            {},
        )

        formulas = detector_results.get(
            "formulas",
            {},
        )

        balance = detector_results.get(
            "balance",
            {},
        )

        mecroyance = detector_results.get(
            "mecroyance",
            {},
        )

        return {
            "gnosis": vector.get("gnosis"),
            "nous": vector.get("nous"),
            "doxa": vector.get("doxa"),
            "reduction": vector.get("reduction"),
            "revisability": vector.get(
                "revisability"
            ),
            "balance": balance,
            "mecroyance": mecroyance,
            "metrics": metrics,
            "formulas": formulas,
        }

    def _aggregate(
        self,
        analyses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Compute simple mean values across several analyses.

        This is descriptive aggregation only.
        It does not replace cognitive comparison or source evaluation.
        """

        vector_keys = [
            "gnosis",
            "nous",
            "doxa",
            "reduction",
            "revisability",
        ]

        values = {
            key: []
            for key in vector_keys
        }

        for analysis_result in analyses:
            cognitive_vector = (
                analysis_result
                .get("analysis", {})
                .get("cognitive_vector", {})
            )

            for key in vector_keys:
                value = cognitive_vector.get(key)

                if isinstance(
                    value,
                    (int, float),
                ):
                    values[key].append(
                        float(value)
                    )

        averages = {}

        for key, collected in values.items():
            averages[key] = (
                sum(collected) / len(collected)
                if collected
                else None
            )

        return {
            "analyzed_item_count": len(analyses),
            "average_cognitive_vector": averages,
        }

    def _build_preview(
        self,
        text: str,
        max_length: int = 280,
    ) -> str:

        if len(text) <= max_length:
            return text

        return (
            text[:max_length].rstrip()
            + "..."
        )

    def _empty_result(
        self,
        source_type: str,
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "engine": self.name,
            "status": "empty",
            "source_type": source_type,
            "provenance": provenance,
            "text": "",
            "text_preview": "",
            "analysis": {},
            "summary": {},
        }
