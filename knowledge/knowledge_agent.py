"""
DeDe - Knowledge Agent

Phase 2 knowledge orchestrator.

The KnowledgeAgent no longer contains knowledge directly.
It coordinates knowledge providers and writes structured knowledge
results into the CognitiveWorkspace.
"""

from typing import Any

from knowledge.providers.local_provider import LocalProvider


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
        self.providers = [
            LocalProvider(),
        ]

    def search(self, query: str) -> dict[str, Any]:
        normalized_query = query.lower().strip()

        results = [
            provider.search(normalized_query)
            for provider in self.providers
        ]

        found_results = [
            result for result in results
            if result.get("found")
        ]

        if found_results:
            best_result = max(
                found_results,
                key=lambda result: result.get("confidence", 0.0),
            )
        else:
            best_result = max(
                results,
                key=lambda result: result.get("confidence", 0.0),
            )

        return {
            "agent": self.name,
            "query": normalized_query,
            "answer": best_result.get("answer"),
            "found": best_result.get("found", False),
            "confidence": best_result.get("confidence", 0.0),
            "provider": best_result.get("provider"),
            "sources": best_result.get("sources", []),
            "all_results": results,
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
