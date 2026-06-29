"""
DeDe - Knowledge Agent

Phase 2 compatible knowledge component.

The KnowledgeAgent currently uses a local knowledge base.
Later, it will orchestrate multiple knowledge providers:
- local knowledge
- web search
- LLMs
- documents
- external databases
"""

from typing import Any


class KnowledgeAgent:
    """
    Local knowledge provider and future knowledge orchestrator.

    This component does not diagnose.
    It retrieves knowledge and returns a structured knowledge result.
    """

    name = "knowledge"

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
        """
        Search the local knowledge base.
        """

        normalized_query = query.lower().strip()

        answer = self.knowledge_base.get(
            normalized_query,
            "Knowledge not found in local knowledge base.",
        )

        found = "not found" not in answer.lower()

        confidence = 0.90 if found else 0.10

        return {
            "agent": self.name,
            "query": normalized_query,
            "answer": answer,
            "found": found,
            "confidence": confidence,
            "sources": [
                {
                    "type": "local",
                    "name": "local_knowledge_base",
                    "confidence": confidence,
                }
            ],
            "provider": "local_knowledge_base",
        }

    def analyze(self, workspace) -> dict[str, Any]:
        """
        Phase 2 entry point.

        Read the text from the CognitiveWorkspace and store
        the knowledge result as an interpretation.
        """

        result = self.search(workspace.text)

        workspace.add_interpretation(self.name, result)

        return result

    # -----------------------------------------------------
    # Legacy Phase 1 compatibility
    # -----------------------------------------------------

    def can_handle(self, state) -> bool:
        return True

    def update_state(self, state, result):
        state.analyses["knowledge"] = result
        state.metadata["knowledge"] = result

        return state
