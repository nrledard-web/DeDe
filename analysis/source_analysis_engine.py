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

        The analysis must distinguish:
        - what the snippet explicitly says;
        - what evidence is visible in the snippet;
        - what remains an unsupported claim or interpretation;
        - the source's apparent framing.
        """

        sources = []

        for index, item in enumerate(
            search_results
        ):
            if not isinstance(
                item,
                dict,
            ):
                continue

            validation = item.get(
                "validation",
                {},
            )

            if not isinstance(
                validation,
                dict,
            ):
                validation = {}

            sources.append(
                {
                    "index": index,
                    "title": str(
                        item.get(
                            "title",
                            "",
                        )
                        or ""
                    ).strip(),
                    "url": str(
                        item.get(
                            "url",
                            "",
                        )
                        or ""
                    ).strip(),
                    "snippet": str(
                        item.get(
                            "snippet",
                            "",
                        )
                        or ""
                    ).strip(),
                    "provider": str(
                        item.get(
                            "provider",
                            "",
                        )
                        or ""
                    ).strip(),
                    "technical_validation": {
                        "url_valid": validation.get(
                            "url_valid",
                            True,
                        ),
                        "hostname": validation.get(
                            "hostname",
                            "",
                        ),
                        "topical_score": validation.get(
                            "topical_score",
                            0.0,
                        ),
                        "matched_concepts": validation.get(
                            "matched_concepts",
                            [],
                        ),
                    },
                }
            )

        return (
            "You are the source-analysis layer of a cognitive "
            "reasoning system.\n\n"

            "Evaluate each retrieved source only from the supplied "
            "title, URL, search-result snippet and technical "
            "validation metadata.\n\n"

            "A search-result snippet is limited evidence. It may be "
            "incomplete, truncated, promotional, editorialized or "
            "taken out of context. Never behave as if the full linked "
            "document has been read.\n\n"

            "For every source, distinguish clearly between:\n"
            "- what the snippet explicitly states;\n"
            "- what evidence is actually visible in the snippet;\n"
            "- what remains a claim, interpretation, qualification "
            "or inference;\n"
            "- the apparent framing or standpoint of the source.\n\n"

            "Do not treat repeated wording across several results as "
            "independent confirmation. Several results may reproduce "
            "the same framing, institution, article or upstream "
            "source.\n\n"

            "Do not decide that a claim is true or false solely from "
            "the source category, reputation, political orientation "
            "or frequency in the result list.\n\n"

            "For every source, estimate:\n"
            "- source_type: one of encyclopedic, academic, "
            "institutional, governmental, journalistic, commercial, "
            "activist, forum, personal, unknown;\n"
            "- evidence_level: number from 0.0 to 1.0 measuring the "
            "evidence visible in the supplied snippet, not the presumed "
            "quality of the unread full page;\n"
            "- independence: number from 0.0 to 1.0;\n"
            "- commercial_pressure: number from 0.0 to 1.0;\n"
            "- ideological_pressure: number from 0.0 to 1.0;\n"
            "- relevance: number from 0.0 to 1.0;\n"
            "- claim_summary: a short neutral description of what the "
            "snippet claims or reports;\n"
            "- evidence_summary: a short description of the evidence "
            "actually visible in the snippet; use an empty string when "
            "no supporting evidence is visible;\n"
            "- framing: one of descriptive, supportive, critical, "
            "mixed, unclear;\n"
            "- limitations: a short list of material limitations;\n"
            "- rationale: one short explanation.\n\n"

            "A source may be highly relevant while providing little "
            "visible evidence. Relevance must never be converted into "
            "truth, reliability or confirmation.\n\n"

            "When the snippet uses a categorical label, moral judgment "
            "or contested qualification, preserve it as the source's "
            "framing unless the supplied snippet contains sufficient "
            "evidence to establish it independently.\n\n"

            "Do not invent information absent from the supplied "
            "metadata. When evidence is insufficient, say so and use "
            "moderate or low evidence scores.\n\n"

            "Return valid JSON only, using exactly this structure:\n\n"

            "{\n"
            '  "sources": [\n'
            "    {\n"
            '      "index": 0,\n'
            '      "source_type": "unknown",\n'
            '      "evidence_level": 0.0,\n'
            '      "independence": 0.5,\n'
            '      "commercial_pressure": 0.0,\n'
            '      "ideological_pressure": 0.0,\n'
            '      "relevance": 0.5,\n'
            '      "claim_summary": "",\n'
            '      "evidence_summary": "",\n'
            '      "framing": "unclear",\n'
            '      "limitations": [],\n'
            '      "rationale": ""\n'
            "    }\n"
            "  ],\n"
            '  "agreement_warning": "",\n'
            '  "viewpoint_diversity": "unknown",\n'
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

        for index, source in enumerate(
            search_results
        ):
            if not isinstance(
                source,
                dict,
            ):
                continue

            source_analysis = (
                analyses_by_index.get(
                    index,
                    self._unknown_analysis(
                        index
                    ),
                )
            )

            validation = source.get(
                "validation",
                {},
            )

            if not isinstance(
                validation,
                dict,
            ):
                validation = {}

            enriched_sources.append(
                {
                    "index": index,
                    "title": str(
                        source.get(
                            "title",
                            "",
                        )
                        or ""
                    ).strip(),
                    "url": str(
                        source.get(
                            "url",
                            "",
                        )
                        or ""
                    ).strip(),
                    "snippet": str(
                        source.get(
                            "snippet",
                            "",
                        )
                        or ""
                    ).strip(),
                    "provider": str(
                        source.get(
                            "provider",
                            "",
                        )
                        or ""
                    ).strip(),
                    "validation": (
                        validation
                    ),
                    "analysis": (
                        source_analysis
                    ),
                }
            )

        aggregate = self._aggregate(
            enriched_sources
        )

        # --------------------------------------------------
        # Viewpoint Diversity
        # --------------------------------------------------

        allowed_diversity_values = {
            "low",
            "moderate",
            "high",
            "unknown",
        }

        viewpoint_diversity = str(
            parsed.get(
                "viewpoint_diversity",
                "unknown",
            )
            or "unknown"
        ).lower().strip()

        if (
            viewpoint_diversity
            not in allowed_diversity_values
        ):
            viewpoint_diversity = "unknown"

        agreement_warning = str(
            parsed.get(
                "agreement_warning",
                "",
            )
            or ""
        ).strip()

        overall_summary = str(
            parsed.get(
                "overall_summary",
                "",
            )
            or ""
        ).strip()

        # --------------------------------------------------
        # Coherence Loop Indicators
        # --------------------------------------------------

        coherence_loop = (
            self._build_coherence_loop_state(
                sources=enriched_sources,
                viewpoint_diversity=(
                    viewpoint_diversity
                ),
                agreement_warning=(
                    agreement_warning
                ),
            )
        )

        return {
            "engine": self.name,
            "status": "ready",
            "source_count": len(
                enriched_sources
            ),
            "sources": enriched_sources,
            "aggregate": aggregate,
            "viewpoint_diversity": (
                viewpoint_diversity
            ),
            "agreement_warning": (
                agreement_warning
            ),
            "coherence_loop": (
                coherence_loop
            ),
            "overall_summary": (
                overall_summary
            ),
            "raw_response": (
                raw_response
            ),
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

        allowed_framings = {
            "descriptive",
            "supportive",
            "critical",
            "mixed",
            "unclear",
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

        framing = str(
            item.get(
                "framing",
                "unclear",
            )
            or "unclear"
        ).lower().strip()

        if framing not in allowed_framings:
            framing = "unclear"

        limitations = item.get(
            "limitations",
            [],
        )

        if not isinstance(
            limitations,
            list,
        ):
            limitations = []

        limitations = [
            str(value).strip()
            for value in limitations
            if str(value).strip()
        ][:5]

        claim_summary = str(
            item.get(
                "claim_summary",
                "",
            )
            or ""
        ).strip()

        evidence_summary = str(
            item.get(
                "evidence_summary",
                "",
            )
            or ""
        ).strip()

        rationale = str(
            item.get(
                "rationale",
                "",
            )
            or ""
        ).strip()

        return {
            "source_type": source_type,
            "evidence_level": self._clamp(
                item.get(
                    "evidence_level"
                )
            ),
            "independence": self._clamp(
                item.get(
                    "independence"
                )
            ),
            "commercial_pressure": self._clamp(
                item.get(
                    "commercial_pressure"
                )
            ),
            "ideological_pressure": self._clamp(
                item.get(
                    "ideological_pressure"
                )
            ),
            "relevance": self._clamp(
                item.get(
                    "relevance"
                )
            ),
            "claim_summary": claim_summary,
            "evidence_summary": (
                evidence_summary
            ),
            "framing": framing,
            "limitations": limitations,
            "rationale": rationale,
        }

    def _unknown_analysis(
        self,
        index: int,
    ) -> dict[str, Any]:

        return {
            "source_type": "unknown",
            "evidence_level": 0.0,
            "independence": 0.5,
            "commercial_pressure": 0.0,
            "ideological_pressure": 0.0,
            "relevance": 0.5,
            "claim_summary": "",
            "evidence_summary": "",
            "framing": "unclear",
            "limitations": [
                (
                    "The available metadata was insufficient "
                    "for a complete evaluation."
                )
            ],
            "rationale": (
                f"No valid semantic evaluation was returned "
                f"for source {index}."
            ),
        }
        
    # --------------------------------------------------
    # Coherence Loop Analysis
    # --------------------------------------------------

    def _build_coherence_loop_state(
        self,
        sources: list[dict[str, Any]],
        viewpoint_diversity: str,
        agreement_warning: str,
    ) -> dict[str, Any]:
        """
        Build a deterministic warning from the semantic
        evaluations already produced.

        This method performs no additional LLM call.
        """

        if not sources:
            return {
                "status": "empty",
                "risk": "unknown",
                "risk_score": 0.0,
                "indicators": [],
                "requires_counterpoint": False,
                "summary": (
                    "No source was available for "
                    "coherence-loop analysis."
                ),
            }

        indicators = []
        risk_score = 0.0

        analyses = []

        for source in sources:
            analysis = source.get(
                "analysis",
                {},
            )

            if isinstance(
                analysis,
                dict,
            ):
                analyses.append(
                    analysis
                )

        framing_counts = {}

        for analysis in analyses:
            framing = str(
                analysis.get(
                    "framing",
                    "unclear",
                )
                or "unclear"
            ).lower().strip()

            framing_counts[framing] = (
                framing_counts.get(
                    framing,
                    0,
                )
                + 1
            )

        meaningful_framings = {
            framing: count
            for framing, count
            in framing_counts.items()
            if framing not in {
                "unclear",
                "descriptive",
            }
        }

        if viewpoint_diversity == "low":
            indicators.append(
                {
                    "type": (
                        "low_viewpoint_diversity"
                    ),
                    "severity": "high",
                    "message": (
                        "The retrieved sources present "
                        "limited viewpoint diversity."
                    ),
                }
            )

            risk_score += 0.35

        elif viewpoint_diversity == "moderate":
            indicators.append(
                {
                    "type": (
                        "moderate_viewpoint_diversity"
                    ),
                    "severity": "low",
                    "message": (
                        "The retrieved sources present only "
                        "moderate viewpoint diversity."
                    ),
                }
            )

            risk_score += 0.10

        if agreement_warning:
            indicators.append(
                {
                    "type": (
                        "agreement_not_independent"
                    ),
                    "severity": "high",
                    "message": (
                        agreement_warning
                    ),
                }
            )

            risk_score += 0.30

        source_count = len(
            analyses
        )

        if (
            source_count >= 3
            and len(
                meaningful_framings
            ) == 1
        ):
            dominant_framing = next(
                iter(
                    meaningful_framings
                ),
                "unknown",
            )

            indicators.append(
                {
                    "type": (
                        "single_dominant_framing"
                    ),
                    "severity": "medium",
                    "message": (
                        "All materially framed sources "
                        "share the same apparent framing: "
                        f"{dominant_framing}."
                    ),
                }
            )

            risk_score += 0.20

        evidence_values = [
            float(
                analysis.get(
                    "evidence_level",
                    0.0,
                )
            )
            for analysis in analyses
            if isinstance(
                analysis.get(
                    "evidence_level"
                ),
                (int, float),
            )
        ]

        ideological_values = [
            float(
                analysis.get(
                    "ideological_pressure",
                    0.0,
                )
            )
            for analysis in analyses
            if isinstance(
                analysis.get(
                    "ideological_pressure"
                ),
                (int, float),
            )
        ]

        independence_values = [
            float(
                analysis.get(
                    "independence",
                    0.0,
                )
            )
            for analysis in analyses
            if isinstance(
                analysis.get(
                    "independence"
                ),
                (int, float),
            )
        ]

        average_evidence = (
            sum(
                evidence_values
            )
            / len(
                evidence_values
            )
            if evidence_values
            else 0.0
        )

        average_ideological_pressure = (
            sum(
                ideological_values
            )
            / len(
                ideological_values
            )
            if ideological_values
            else 0.0
        )

        average_independence = (
            sum(
                independence_values
            )
            / len(
                independence_values
            )
            if independence_values
            else 0.0
        )

        if (
            average_ideological_pressure
            >= 0.60
        ):
            indicators.append(
                {
                    "type": (
                        "high_ideological_pressure"
                    ),
                    "severity": "high",
                    "message": (
                        "The retrieved corpus has high "
                        "average ideological pressure."
                    ),
                }
            )

            risk_score += 0.25

        if (
            average_evidence < 0.40
            and source_count >= 2
        ):
            indicators.append(
                {
                    "type": (
                        "repetition_without_evidence"
                    ),
                    "severity": "high",
                    "message": (
                        "Several sources are present, but "
                        "the evidence visible in their "
                        "snippets remains limited."
                    ),
                }
            )

            risk_score += 0.25

        if (
            average_independence < 0.45
            and source_count >= 2
        ):
            indicators.append(
                {
                    "type": (
                        "low_source_independence"
                    ),
                    "severity": "medium",
                    "message": (
                        "The retrieved sources may not "
                        "constitute independent confirmation."
                    ),
                }
            )

            risk_score += 0.20

        risk_score = max(
            0.0,
            min(
                1.0,
                risk_score,
            ),
        )

        if risk_score >= 0.60:
            risk = "high"

        elif risk_score >= 0.30:
            risk = "moderate"

        else:
            risk = "low"

        requires_counterpoint = (
            risk in {
                "moderate",
                "high",
            }
        )

        return {
            "status": "ready",
            "risk": risk,
            "risk_score": round(
                risk_score,
                3,
            ),
            "requires_counterpoint": (
                requires_counterpoint
            ),
            "viewpoint_diversity": (
                viewpoint_diversity
            ),
            "framing_counts": (
                framing_counts
            ),
            "average_evidence": round(
                average_evidence,
                3,
            ),
            "average_independence": round(
                average_independence,
                3,
            ),
            "average_ideological_pressure": round(
                average_ideological_pressure,
                3,
            ),
            "indicators": indicators,
            "summary": (
                "A potential coherence loop was detected."
                if requires_counterpoint
                else (
                    "No strong coherence-loop risk "
                    "was detected."
                )
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

        for index, source in enumerate(
            search_results
        ):
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
                    "snippet": source.get(
                        "snippet",
                        "",
                    ),
                    "provider": source.get(
                        "provider",
                        "",
                    ),
                    "validation": source.get(
                        "validation",
                        {},
                    ),
                    "analysis": (
                        self._unknown_analysis(
                            index
                        )
                    ),
                }
            )

        coherence_loop = (
            self._build_coherence_loop_state(
                sources=sources,
                viewpoint_diversity="unknown",
                agreement_warning="",
            )
        )

        return {
            "engine": self.name,
            "status": "unavailable",
            "source_count": len(
                sources
            ),
            "sources": sources,
            "aggregate": self._aggregate(
                sources
            ),
            "viewpoint_diversity": (
                "unknown"
            ),
            "agreement_warning": "",
            "coherence_loop": (
                coherence_loop
            ),
            "overall_summary": reason,
            "raw_response": raw_response,
        }

    def _clamp(
        self,
        value: Any,
        default: float = 0.5,
    ) -> float:

        if not isinstance(
            value,
            (int, float),
        ):
            return default

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )
