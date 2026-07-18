"""
DeDe - Knowledge Provider Engine

Coordinates interchangeable and combinable
knowledge providers.
"""

from __future__ import annotations

from typing import Any

from knowledge.providers.local_provider import (
    LocalProvider,
)
from knowledge.providers.foundational_provider import (
    FoundationalProvider,
)


class ProviderEngine:
    """
    Select or combine knowledge providers.
    """

    name = "knowledge_provider_engine"

    def __init__(self) -> None:
        self.providers = {
            "local": LocalProvider(),
            "foundational": FoundationalProvider(),
        }

    def search(
        self,
        query: str,
        selected_providers: list[str] | None = None,
        mode: str = "best",
    ) -> dict[str, Any]:
        """
        Search selected providers.

        Modes:
        - best: use the result with the highest confidence
        - combine: preserve and combine all successful results
        """

        provider_names = (
            selected_providers
            if selected_providers
            else list(self.providers.keys())
        )

        results = []

        for provider_name in provider_names:
            provider = self.providers.get(
                provider_name
            )

            if provider is None:
                results.append(
                    {
                        "provider": provider_name,
                        "query": query,
                        "answer": "",
                        "found": False,
                        "confidence": 0.0,
                        "sources": [],
                        "error": (
                            "Knowledge provider is not registered."
                        ),
                    }
                )
                continue

            try:
                result = provider.search(
                    query
                )

            except Exception as error:
                result = {
                    "provider": provider_name,
                    "query": query,
                    "answer": "",
                    "found": False,
                    "confidence": 0.0,
                    "sources": [],
                    "error": str(error),
                }

            results.append(
                result
            )

        successful_results = [
            result
            for result in results
            if result.get(
                "found",
                False,
            )
        ]

        best_result = self._select_best_result(
            results=results,
        )

        combined_result = self._combine_results(
            query=query,
            successful_results=successful_results,
        )

        selected_result = (
            combined_result
            if mode == "combine"
            and combined_result.get("found")
            else best_result
        )

        return {
            "engine": self.name,
            "mode": mode,
            "selected_providers": provider_names,
            "results": results,
            "best_result": best_result,
            "combined_result": combined_result,
            "selected_result": selected_result,
            "provider_count": len(provider_names),
            "successful_provider_count": len(
                successful_results
            ),
        }

    def _select_best_result(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Select the result with the strongest confidence.
        """

        if not results:
            return self._empty_result(
                query="",
            )

        return max(
            results,
            key=lambda result: float(
                result.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            ),
        )

    def _combine_results(
        self,
        query: str,
        successful_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Combine successful answers while preserving provenance.
        """

        if not successful_results:
            return self._empty_result(
                query=query,
            )

        answers = []
        sources = []
        providers = []
        highest_confidence = 0.0

        for result in successful_results:
            answer = str(
                result.get(
                    "answer",
                    "",
                )
                or ""
            ).strip()

            if answer and answer not in answers:
                answers.append(
                    answer
                )

            provider_name = str(
                result.get(
                    "provider",
                    "",
                )
            ).strip()

            if (
                provider_name
                and provider_name not in providers
            ):
                providers.append(
                    provider_name
                )

            result_sources = result.get(
                "sources",
                [],
            )

            if isinstance(
                result_sources,
                list,
            ):
                sources.extend(
                    result_sources
                )

            try:
                confidence = float(
                    result.get(
                        "confidence",
                        0.0,
                    )
                    or 0.0
                )
            except (
                TypeError,
                ValueError,
            ):
                confidence = 0.0

            highest_confidence = max(
                highest_confidence,
                confidence,
            )

        return {
            "provider": "combined_knowledge",
            "providers": providers,
            "query": query,
            "answer": "\n\n".join(
                answers
            ),
            "found": bool(
                answers
            ),
            "confidence": highest_confidence,
            "sources": sources,
        }

    def _empty_result(
        self,
        query: str,
    ) -> dict[str, Any]:
        """
        Build a normalized empty result.
        """

        return {
            "provider": "none",
            "query": query,
            "answer": "",
            "found": False,
            "confidence": 0.0,
            "sources": [],
        }

    def available_providers(
        self,
    ) -> list[dict[str, str]]:
        """
        Expose registered providers to the interface.
        """

        return [
            {
                "name": provider_name,
                "provider": provider.name,
            }
            for provider_name, provider
            in self.providers.items()
        ]
