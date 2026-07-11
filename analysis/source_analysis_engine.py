"""
DeDe - Source Analysis Engine

Semantically evaluates the nature and epistemic quality of web sources.

Principles:
- one analysis request for all retrieved sources;
- no language-specific keyword lists;
- no hard-coded political or personal markers;
- source evaluation remains distinct from textual cognitive analysis;
- malformed model output fails safely.
"""

from __future__ import annotations

import json
import re
from typing import Any


class SourceAnalysisEngine:
    """
    Builds and parses a semantic evaluation of retrieved web sources.
    """

    name = "source_analysis_engine"

    def build_prompt(
        self,
        search_results: list[dict[str, Any]],
        user_request: str,
        search_query: str,
    ) -> str:
        """
        Build one semantic source-analysis prompt for all results.
        """

        sources = []

        for index, item in enumerate(search_results):
            if not isinstance(item, dict):
                continue

            sources.append(
                {
                    "index": index,
                    "title": str(
                        item.get("title", "")
                        or ""
                    ).strip(),
                    "url": str(
                        item.get("url", "")
                        or ""
                    ).strip(),
                    "snippet": str(
                        item.get("snippet", "")
                        or ""
                    ).strip(),
                    "provider": str(
                        item.get("provider", "")
                        or ""
                    ).strip(),
                }
            )

        return (
            "You are the source-analysis layer of a cognitive reasoning "
            "system.\n\n"
            "Evaluate each retrieved source from its title, URL, snippet "
            "and relationship to the user's request.\n\n"
            "For every source, estimate:\n"
            "- source_type: one of encyclopedic, academic, institutional, "
            "governmental, journalistic, commercial, activist, forum, "
            "personal, unknown;\n"
            "- evidence_level: a number from 0.0 to 1.0;\n"
            "- independence: a number from 0.0 to 1.0;\n"
            "- commercial_pressure: a number from 0.0 to 1.0;\n"
            "- ideological_pressure: a number from 0.0 to 1.0;\n"
            "- relevance: a number from 0.0 to 1.0;\n"
            "- limitations: a short list of limitations;\n"
            "- rationale: one short explanation.\n\n"
            "Do not decide whether the source is true or false solely from "
            "its category.\n"
            "Do not invent information that is absent from the supplied "
            "metadata.\n"
            "When evidence is insufficient, use 'unknown' and moderate "
            "scores.\n\n"
            "Return valid JSON only, using exactly this structure:\n\n"
            "{\n"
            '  "sources": [\n'
            "    {\n"
            '      "index": 0,\n'
            '      "source_type": "unknown",\n'
            '      "evidence_level": 0.5,\n'
            '      "independence": 0.5,\n'
            '      "commercial_pressure": 0.0,\n'
            '      "ideological_pressure": 0.0,\n'
            '      "relevance": 0.5,\n'
            '      "limitations": [],\n'
            '      "rationale": ""\n'
            "    }\n"
            "  ],\n"
            '  "overall_summary": ""\n'
            "}\n\n"
            f"User request:\n{user_request}\n\n"
            f"Search query:\n{search_query}\n\n"
            "Retrieved sources:\n"
            f"{json.dumps(sources, ensure_ascii=False, indent=2)}"
        )

    def parse_response(
        self,
        model_response: str | None,
        search_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Parse and normalize the model's JSON response.
        """

        raw_response = str(
            model_response
            or ""
        ).strip()

        parsed = self._parse_json(
            raw_response
        )

        if not isinstance(parsed, dict):
            return self._fallback_result(
                search_results=search_results,
                raw_response=raw_response,
                reason=(
                    "The reasoning model did not return valid source-analysis "
                    "JSON."
                ),
            )

        raw_sources = parsed.get(
            "sources",
            [],
        )

        if not isinstance(raw_sources, list):
            raw_sources = []

        analyses_by_index = {}

        for item in raw_sources:
            if not isinstance(item, dict):
                continue

            index = item.get("index")

            if not isinstance(index, int):
                continue

            analyses_by_index[index] = (
                self._normalize_source_analysis(
                    item
                )
            )

        enriched_sources = []

        for index, source in enumerate(search_results):
            source_analysis = analyses_by_index.get(
                index,
                self._unknown_analysis(index),
            )

            enriched_sources.append(
                {
                    "index": index,
                    "title": source.get(
                        "title",
                        "",
                    ),
                    "url": source.get(
                        "url",
                        "",
                    ),
                    "provider": source.get(
                        "provider",
                        "",
                    ),
                    "analysis": source_analysis,
                }
            )

        aggregate = self._aggregate(
            enriched_sources
        )

        return {
            "engine": self.name,
            "status": "ready",
            "source_count": len(enriched_sources),
            "sources": enriched_sources,
            "aggregate": aggregate,
            "overall_summary": str(
                parsed.get(
                    "overall_summary",
                    "",
                )
                or ""
            ).strip(),
            "raw_response": raw_response,
        }

    def unavailable(
        self,
        search_results: list[dict[str, Any]],
        reason: str,
    ) -> dict[str, Any]:
        """
        Safe result when semantic source analysis cannot run.
        """

        return self._fallback_result(
            search_results=search_results,
            raw_response="",
            reason=reason,
        )

    def _parse_json(
        self,
        raw_response: str,
    ) -> dict[str, Any] | None:

        if not raw_response:
            return None

        cleaned = raw_response.strip()

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        try:
            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return None

        candidate = cleaned[
            start:end + 1
        ]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            return None

        return None

    def _normalize_source_analysis(
        self,
        item: dict[str, Any],
    ) -> dict[str, Any]:

        allowed_types = {
            "encyclopedic",
            "academic",
            "institutional",
            "governmental",
            "journalistic",
            "commercial",
            "activist",
            "forum",
            "personal",
            "unknown",
        }

        source_type = str(
            item.get(
                "source_type",
                "unknown",
            )
            or "unknown"
        ).lower().strip()

        if source_type not in allowed_types:
            source_type = "unknown"

        limitations = item.get(
            "limitations",
            [],
        )

        if not isinstance(limitations, list):
            limitations = []

        limitations = [
            str(value).strip()
            for value in limitations
            if str(value).strip()
        ][:5]

        return {
            "source_type": source_type,
            "evidence_level": self._clamp(
                item.get("evidence_level")
            ),
            "independence": self._clamp(
                item.get("independence")
            ),
            "commercial_pressure": self._clamp(
                item.get("commercial_pressure")
            ),
            "ideological_pressure": self._clamp(
                item.get("ideological_pressure")
            ),
            "relevance": self._clamp(
                item.get("relevance")
            ),
            "limitations": limitations,
            "rationale": str(
                item.get(
                    "rationale",
                    "",
                )
                or ""
            ).strip(),
        }

    def _unknown_analysis(
        self,
        index: int,
    ) -> dict[str, Any]:

        return {
            "source_type": "unknown",
            "evidence_level": 0.5,
            "independence": 0.5,
            "commercial_pressure": 0.0,
            "ideological_pressure": 0.0,
            "relevance": 0.5,
            "limitations": [
                (
                    "The available metadata was insufficient for "
                    "a complete evaluation."
                )
            ],
            "rationale": (
                f"No valid semantic evaluation was returned "
                f"for source {index}."
            ),
        }

    def _aggregate(
        self,
        enriched_sources: list[dict[str, Any]],
    ) -> dict[str, Any]:

        metric_names = [
            "evidence_level",
            "independence",
            "commercial_pressure",
            "ideological_pressure",
            "relevance",
        ]

        collected = {
            name: []
            for name in metric_names
        }

        type_counts = {}

        for source in enriched_sources:
            analysis = source.get(
                "analysis",
                {},
            )

            source_type = analysis.get(
                "source_type",
                "unknown",
            )

            type_counts[source_type] = (
                type_counts.get(
                    source_type,
                    0,
                )
                + 1
            )

            for metric_name in metric_names:
                value = analysis.get(
                    metric_name
                )

                if isinstance(value, (int, float)):
                    collected[metric_name].append(
                        float(value)
                    )

        averages = {}

        for metric_name, values in collected.items():
            averages[metric_name] = (
                sum(values) / len(values)
                if values
                else None
            )

        return {
            "source_type_counts": type_counts,
            "average_scores": averages,
        }

    def _fallback_result(
        self,
        search_results: list[dict[str, Any]],
        raw_response: str,
        reason: str,
    ) -> dict[str, Any]:

        sources = []

        for index, source in enumerate(search_results):
            sources.append(
                {
                    "index": index,
                    "title": source.get(
                        "title",
                        "",
                    ),
                    "url": source.get(
                        "url",
                        "",
                    ),
                    "provider": source.get(
                        "provider",
                        "",
                    ),
                    "analysis": self._unknown_analysis(
                        index
                    ),
                }
            )

        return {
            "engine": self.name,
            "status": "unavailable",
            "source_count": len(sources),
            "sources": sources,
            "aggregate": self._aggregate(
                sources
            ),
            "overall_summary": reason,
            "raw_response": raw_response,
        }

    def _clamp(
        self,
        value: Any,
        default: float = 0.5,
    ) -> float:

        if not isinstance(value, (int, float)):
            return default

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )
