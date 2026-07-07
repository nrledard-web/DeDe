"""
DeDe - Search Query Builder

Builds clean search queries from DeDe's cognitive understanding,
not from the raw user message.
"""

from typing import Any


class SearchQueryBuilder:
    name = "search_query_builder"

    def build(
        self,
        text: str,
        concept_data: dict[str, Any] | None = None,
        conversation_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        concept_data = concept_data or {}
        conversation_context = conversation_context or {}

        concepts = concept_data.get("main_concepts", [])
        recent_topics = conversation_context.get("recent_topics", [])

        candidates = []

        for concept in concepts:
            concept = str(concept).strip()

            if self._is_usable_concept(concept):
                candidates.append(concept)

        if not candidates:
            for topic in reversed(recent_topics):
                topic = str(topic).strip()

                if self._is_usable_concept(topic):
                    candidates.append(topic)
                    break

        query = " ".join(candidates[:3]).strip()

        if not query:
            query = text.strip()

        return {
            "builder": self.name,
            "status": "ready",
            "query": query,
            "concepts_used": candidates[:3],
            "source": (
                "concepts"
                if candidates
                else "raw_text"
            ),
            "summary": f"Search query built: {query}",
        }

    def _is_usable_concept(
        self,
        concept: str,
    ) -> bool:

        if not concept:
            return False

        if len(concept) <= 2:
            return False

        if concept.startswith("claim:"):
            return False

        return True
