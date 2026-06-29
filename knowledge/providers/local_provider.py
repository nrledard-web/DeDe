"""
DeDe - Local Knowledge Provider

Provides knowledge from a local dictionary.

This is the first provider used by the KnowledgeAgent.
Future providers may use web search, LLMs, documents or databases.
"""

from typing import Any


class LocalProvider:
    """
    Local dictionary-based knowledge provider.
    """

    name = "local_knowledge_base"

    def __init__(self):
        self.knowledge_base = {
            "what is gravity":
                "Gravity is the attraction between masses.",

            "who discovered relativity":
                "Albert Einstein developed General Relativity.",

            "what is cognition":
                "Cognition refers to processes involved in acquiring and using knowledge.",

            "what is mecroyance":
                (
                    "Mecroyance is a cognitive condition in which certainty "
                    "stabilizes faster than understanding."
                ),

            "what is doxa":
                (
                    "Doxa refers to stabilized certainty that can become "
                    "resistant to revision."
                ),
        }

    def search(self, query: str) -> dict[str, Any]:
        normalized_query = query.lower().strip()

        answer = self.knowledge_base.get(
            normalized_query,
            "Knowledge not found in local knowledge base.",
        )

        found = "not found" not in answer.lower()
        confidence = 0.90 if found else 0.10

        return {
            "provider": self.name,
            "query": normalized_query,
            "answer": answer,
            "found": found,
            "confidence": confidence,
            "sources": [
                {
                    "type": "local",
                    "name": self.name,
                    "confidence": confidence,
                }
            ],
        }
