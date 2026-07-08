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
                "last_topic": None,
                "recent_topics": [],
                "summary": "No previous conversation context available.",
            }

        last_turn = history[-1]

        recent_topics = []

        for turn in history[-5:]:
            topics = turn.get("topics", [])
            recent_topics.extend(topics)

        recent_topics = self._unique(recent_topics)

        last_topic = last_turn.get("main_topic")

        if not last_topic and recent_topics:
            last_topic = recent_topics[-1]

        return {
            "manager": self.name,
            "status": "ready",
            "turn_count": len(history),
            "last_user_input": last_turn.get("user_input"),
            "last_answer": last_turn.get("answer"),
            "last_topic": last_topic,
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
        main_topic = self._extract_main_topic(
            user_input=user_input,
            topics=topics,
        )

        turn = {
            "user_input": user_input,
            "answer": user_response.get("final_answer", ""),
            "follow_up_question": user_response.get("follow_up_question"),
            "conversation_mode": user_response.get("conversation_mode"),
            "main_topic": main_topic,
            "topics": topics,
        }

        history.append(turn)

        return history[-10:]

    def _extract_main_topic(
        self,
        user_input: str,
        topics: list[str],
    ) -> str | None:

        text = user_input.lower()

        known_topics = {
            "immigration": [
                "immigration",
                "immigré",
                "immigrés",
                "migrant",
                "migrants",
                "migration",
            ],
            "communisme": [
                "communisme",
                "communiste",
                "communistes",
                "marxisme",
                "marxiste",
            ],
            "capitalisme": [
                "capitalisme",
                "capitaliste",
                "capitalistes",
            ],
            "démocratie": [
                "démocratie",
                "democratie",
                "démocratique",
                "democratique",
            ],
            "religion": [
                "religion",
                "religions",
                "foi",
                "croyance",
            ],
            "science": [
                "science",
                "scientifique",
                "scientifiques",
            ],
            "ia": [
                "ia",
                "intelligence artificielle",
                "llm",
                "ai",
            ],
            "mécroyance": [
                "mécroyance",
                "mecroyance",
                "mécroire",
                "mecroire",
            ],
        }

        for topic, markers in known_topics.items():
            if any(marker in text for marker in markers):
                return topic

        for topic in topics:
            clean_topic = str(topic).lower().strip()

            if self._is_valid_topic(clean_topic):
                return clean_topic

        return None

    def _extract_topics(
        self,
        report: dict[str, Any],
    ) -> list[str]:

        concepts = report.get("concepts", {})
        semantic = report.get("semantic", {})
        cognitive_feedback = report.get("cognitive_feedback", {})

        topics = []

        topics.extend(
            concepts.get("main_concepts", [])
        )

        topics.extend(
            semantic.get("main_concepts", [])
        )

        topics.extend(
            cognitive_feedback.get("new_concepts", [])
        )

        cleaned_topics = []

        for topic in topics:
            clean_topic = str(topic).lower().strip()

            if self._is_valid_topic(clean_topic):
                cleaned_topics.append(clean_topic)

        return self._unique(cleaned_topics)[:12]

    def _is_valid_topic(
        self,
        topic: str,
    ) -> bool:

        if not topic:
            return False

        forbidden = {
            "dis", "dit", "moi", "plus", "sur", "des", "les", "le", "la",
            "un", "une", "et", "ou", "mais", "avec", "pour", "dans",
            "donne", "donner", "arguments", "uniquement", "maintenant",
            "synthèse", "equilibree", "équilibrée", "faveur", "contre",
            "stp", "svp", "claim:0", "understanding", "revisability",
            "mecroyance", "certainty", "reduction", "closure",
            "grounding", "integration", "cognitive_filter",
        }

        if topic in forbidden:
            return False

        if topic.startswith("claim:"):
            return False

        if topic.startswith("metric:"):
            return False

        if topic.startswith("agent:"):
            return False

        if topic.startswith("strategy:"):
            return False

        if len(topic) < 4:
            return False

        return True

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
