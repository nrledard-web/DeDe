"""
DeDe - Conversation Manager

Maintains a short-term conversation context for the current session.
"""

from typing import Any


class ConversationManager:

    name = "conversation_manager"

    def build_context(
        self,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:

        history = history or []

        if not history:
            return {
                "manager": self.name,
                "status": "empty",
                "turn_count": 0,
                "last_user_input": None,
                "last_answer": None,
                "recent_topics": [],
                "summary": "No previous conversation context available.",
            }

        last_turn = history[-1]

        recent_topics = []

        for turn in history[-5:]:
            topics = turn.get("topics", [])
            recent_topics.extend(topics)

        recent_topics = self._unique(recent_topics)

        return {
            "manager": self.name,
            "status": "ready",
            "turn_count": len(history),
            "last_user_input": last_turn.get("user_input"),
            "last_answer": last_turn.get("answer"),
            "recent_topics": recent_topics,
            "summary": (
                f"Conversation context available with {len(history)} previous turn(s)."
            ),
        }

    def add_turn(
        self,
        history: list[dict[str, Any]] | None,
        user_input: str,
        user_response: dict[str, Any],
        report: dict[str, Any],
    ) -> list[dict[str, Any]]:

        history = history or []

        topics = self._extract_topics(report)

        turn = {
            "user_input": user_input,
            "answer": user_response.get("final_answer", ""),
            "follow_up_question": user_response.get("follow_up_question"),
            "conversation_mode": user_response.get("conversation_mode"),
            "topics": topics,
        }

        history.append(turn)

        return history[-10:]

    def _extract_topics(
        self,
        report: dict[str, Any],
    ) -> list[str]:

        concepts = report.get("concepts", {})
        semantic = report.get("semantic", {})
        graph_queries = report.get("graph_queries", {})

        topics = []

        topics.extend(
            concepts.get("main_concepts", [])
        )

        topics.extend(
            semantic.get("main_concepts", [])
        )

        for item in graph_queries.get("central_nodes", []):
            node = item.get("node")

            if node:
                topics.append(node)

        return self._unique(topics)[:12]

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:

        seen = set()
        unique_values = []

        for value in values:
            if value not in seen:
                seen.add(value)
                unique_values.append(value)

        return unique_values
