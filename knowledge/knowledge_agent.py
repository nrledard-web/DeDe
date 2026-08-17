"""
DeDe - Knowledge Agent

Knowledge orchestrator.

The KnowledgeAgent delegates retrieval to interchangeable
and combinable knowledge providers, then writes the selected
knowledge into the CognitiveWorkspace.

Canonical semantic concepts may be supplied by upstream
cognitive components and transmitted to compatible providers.
"""

from __future__ import annotations

from typing import Any

from knowledge.providers.provider_engine import (
    ProviderEngine,
)


class KnowledgeAgent:
    """
    Coordinate knowledge retrieval and provenance.
    """

    name = "knowledge"

    def __init__(self) -> None:
        self.provider_engine = ProviderEngine()

    def search(
        self,
        query: str,
        selected_providers: list[str] | None = None,
        mode: str = "best",
        canonical_concepts: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Search selected knowledge providers.

        canonical_concepts:
            Structured semantic identifiers produced upstream.
        """

        normalized_query = str(
            query or ""
        ).strip()

        canonical_concepts = (
            canonical_concepts
            if isinstance(
                canonical_concepts,
                list,
            )
            else []
        )

        provider_result = (
            self.provider_engine.search(
                query=normalized_query,
                selected_providers=selected_providers,
                mode=mode,
                canonical_concepts=canonical_concepts,
            )
        )

        selected_result = provider_result.get(
            "selected_result",
            provider_result.get(
                "best_result",
                {},
            ),
        )

        return {
            "agent": self.name,
            "query": normalized_query,
            "canonical_concepts": (
                canonical_concepts
            ),
            "mode": provider_result.get(
                "mode",
                mode,
            ),
            "answer": selected_result.get(
                "answer",
                "",
            ),
            "found": selected_result.get(
                "found",
                False,
            ),
            "confidence": selected_result.get(
                "confidence",
                0.0,
            ),
            "provider": selected_result.get(
                "provider",
            ),
            "providers": selected_result.get(
                "providers",
                [],
            ),
            "concept": selected_result.get(
                "concept",
            ),
            "entry": selected_result.get(
                "entry",
                {},
            ),
            "sources": selected_result.get(
                "sources",
                [],
            ),
            "selected_providers": provider_result.get(
                "selected_providers",
                [],
            ),
            "all_results": provider_result.get(
                "results",
                [],
            ),
            "best_result": provider_result.get(
                "best_result",
                {},
            ),
            "combined_result": provider_result.get(
                "combined_result",
                {},
            ),
            "provider_count": provider_result.get(
                "provider_count",
                0,
            ),
            "successful_provider_count": (
                provider_result.get(
                    "successful_provider_count",
                    0,
                )
            ),
        }

    def analyze(
        self,
        workspace: Any,
        selected_providers: list[str] | None = None,
        mode: str = "best",
        canonical_concepts: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze workspace text with selected providers.
        """

        result = self.search(
            query=workspace.text,
            selected_providers=selected_providers,
            mode=mode,
            canonical_concepts=canonical_concepts,
        )

        workspace.add_interpretation(
            self.name,
            result,
        )

        return result

    def available_providers(
        self,
    ) -> list[dict[str, str]]:
        """
        Expose providers for future interface controls.
        """

        return (
            self.provider_engine
            .available_providers()
        )

    def can_handle(
        self,
        state: Any,
    ) -> bool:
        return True

    def update_state(
        self,
        state: Any,
        result: dict[str, Any],
    ) -> Any:
        state.analyses[
            "knowledge"
        ] = result

        state.metadata[
            "knowledge"
        ] = result

        return state
