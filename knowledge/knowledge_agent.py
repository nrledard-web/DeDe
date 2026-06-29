"""
DeDe - Knowledge Agent

Phase 2 knowledge orchestrator.

The KnowledgeAgent delegates knowledge retrieval to the ProviderEngine
and writes structured knowledge results into the CognitiveWorkspace.
"""

from typing import Any

from knowledge.providers.provider_engine import ProviderEngine


class KnowledgeAgent:
    """
    Knowledge orchestrator.

    Current provider:
    - LocalProvider

    Future providers:
    - WebProvider
    - LLMProvider
    - PDFProvider
    - WikipediaProvider
    """

    name = "knowledge"

    def __init__(self):
        self.provider_engine = ProviderEngine()

    def search(self, query: str) -> dict[str, Any]:
        normalized_query = query.lower().strip()

        provider_result = self.provider_engine.search(normalized_query)

        best = provider_result["best_result"]

        return {
            "agent": self.name,
            "query": normalized_query,
            "answer": best.get("answer"),
            "found": best.get("found", False),
            "confidence": best.get("confidence", 0.0),
            "provider": best.get("provider"),
            "sources": best.get("sources", []),
            "all_results": provider_result["results"],
            "provider_count": provider_result["provider_count"],
        }

    def analyze(self, workspace) -> dict[str, Any]:
        result = self.search(workspace.text)

        workspace.add_interpretation(self.name, result)

        return result

    def can_handle(self, state) -> bool:
        return True

    def update_state(self, state, result):
        state.analyses["knowledge"] = result
        state.metadata["knowledge"] = result

        return state
