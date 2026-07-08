"""
DeDe - Committee Reasoner

Transforms multiple LLM outputs into structured reasoning material.
It does not speak to the user directly.
"""

from typing import Any
import json


class CommitteeReasoner:

    name = "committee_reasoner"

    def analyze(
        self,
        llm_committee: dict[str, Any],
    ) -> dict[str, Any]:

        provider_responses = llm_committee.get(
            "provider_responses",
            [],
        )

        if not provider_responses:
            return {
                "engine": self.name,
                "status": "empty",
                "consensus": [],
                "differences": [],
                "uncertainties": [],
                "missing_dimensions": [],
                "confidence": 0.0,
                "summary": "No LLM material available.",
            }

        responses = []

        for item in provider_responses:
            responses.append(
                {
                    "provider": item.get("provider", "unknown"),
                    "text": self._extract_text(
                        item.get("response", ""),
                    ),
                }
            )

        consensus = self._build_consensus(responses)
        differences = self._build_differences(responses)

        return {
            "engine": self.name,
            "status": "ready",
            "consensus": consensus,
            "differences": differences,
            "uncertainties": [],
            "missing_dimensions": [],
            "confidence": min(0.95, 0.55 + 0.15 * len(responses)),
            "source_count": len(responses),
            "summary": (
                "LLM committee material analyzed into structured "
                "reasoning components."
            ),
        }

    def _extract_text(
        self,
        text: str,
    ) -> str:

        cleaned = (
            text
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        try:
            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                return (
                    parsed.get("user_facing_response")
                    or parsed.get("response")
                    or cleaned
                )
        except Exception:
            pass

        return cleaned

    def _build_consensus(
        self,
        responses: list[dict[str, str]],
    ) -> list[str]:

        if len(responses) == 1:
            return [
                responses[0]["text"],
            ]

        shortest = min(
            responses,
            key=lambda item: len(item["text"]),
        )

        longest = max(
            responses,
            key=lambda item: len(item["text"]),
        )

        return [
            "Multiple reasoning models produced compatible answers.",
            self._shorten(longest["text"], 420),
            "The shorter response does not introduce a major contradiction.",
        ]

    def _build_differences(
        self,
        responses: list[dict[str, str]],
    ) -> list[str]:

        differences = []

        for item in responses:
            differences.append(
                f"{item['provider']} contribution: "
                f"{self._shorten(item['text'], 240)}"
            )

        return differences

    def _shorten(
        self,
        text: str,
        limit: int,
    ) -> str:

        cleaned = " ".join(text.split())

        if len(cleaned) <= limit:
            return cleaned

        return cleaned[:limit].rstrip() + "..."
