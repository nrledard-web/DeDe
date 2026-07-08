"""
DeDe - Conversation Manager

Maintains a short-term conversation context for the current session.

Principle:
- No hard-coded personal markers.
- No hard-coded political / thematic topics.
- Multilingual by structure, not by topic list.
- Uses dominant concepts from DeDe's own cognitive pipeline.
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
                "last_focus_concept": None,
                "recent_focus_concepts": [],
                "recent_topics": [],
                "summary": "No previous conversation context available.",
            }

        last_turn = history[-1]

        recent_focus_concepts = []

        for turn in history[-5:]:
            focus = turn.get("focus_concept")

            if focus:
                recent_focus_concepts.append(focus)

        recent_focus_concepts = self._unique(recent_focus_concepts)

        last_focus_concept = last_turn.get("focus_concept")

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
            "last_focus_concept": last_focus_concept,
            "recent_focus_concepts": recent_focus_concepts,
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

        focus_concept = self._extract_focus_concept(
            report=report,
            topics=topics,
        )

        turn = {
            "user_input": user_input,
            "answer": user_response.get("final_answer", ""),
            "follow_up_question": user_response.get("follow_up_question"),
            "conversation_mode": user_response.get("conversation_mode"),
            "focus_concept": focus_concept,
            "topics": topics,
        }

        history.append(turn)

        return history[-10:]

    def _extract_focus_concept(
        self,
        report: dict[str, Any],
        topics: list[str],
    ) -> str | None:

        cognitive_feedback = report.get("cognitive_feedback", {})
        concepts = report.get("concepts", {})
        semantic = report.get("semantic", {})
        graph_queries = report.get("graph_queries", {})

        candidates = []

        candidates.extend(
            cognitive_feedback.get("new_concepts", [])
        )

        candidates.extend(
            concepts.get("main_concepts", [])
        )

        candidates.extend(
            semantic.get("main_concepts", [])
        )

        for item in graph_queries.get("central_nodes", []):
            node = item.get("node")

            if node:
                candidates.append(node)

        candidates.extend(topics)

        scored = []

        for candidate in candidates:
            clean = self._clean_concept(candidate)

            if not self._is_valid_concept(clean):
                continue

            score = self._score_concept(
                concept=clean,
                report=report,
            )

            scored.append(
                {
                    "concept": clean,
                    "score": score,
                }
            )

        if not scored:
            return None

        scored = sorted(
            scored,
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored[0]["concept"]

    def _extract_topics(
        self,
        report: dict[str, Any],
    ) -> list[str]:

        cognitive_feedback = report.get("cognitive_feedback", {})
        concepts = report.get("concepts", {})
        semantic = report.get("semantic", {})

        topics = []

        topics.extend(
            cognitive_feedback.get("new_concepts", [])
        )

        topics.extend(
            concepts.get("main_concepts", [])
        )

        topics.extend(
            semantic.get("main_concepts", [])
        )

        cleaned_topics = []

        for topic in topics:
            clean = self._clean_concept(topic)

            if self._is_valid_concept(clean):
                cleaned_topics.append(clean)

        return self._unique(cleaned_topics)[:12]

    def _score_concept(
        self,
        concept: str,
        report: dict[str, Any],
    ) -> float:

        score = 0.0

        cognitive_feedback = report.get("cognitive_feedback", {})
        concepts = report.get("concepts", {})
        semantic = report.get("semantic", {})
        graph_queries = report.get("graph_queries", {})

        if concept in [
            self._clean_concept(item)
            for item in cognitive_feedback.get("new_concepts", [])
        ]:
            score += 4.0

        if concept in [
            self._clean_concept(item)
            for item in concepts.get("main_concepts", [])
        ]:
            score += 2.0

        if concept in [
            self._clean_concept(item)
            for item in semantic.get("main_concepts", [])
        ]:
            score += 2.0

        for item in graph_queries.get("central_nodes", []):
            node = self._clean_concept(item.get("node"))

            if node == concept:
                score += float(item.get("degree", 0)) * 0.2

        score += min(len(concept) / 20, 1.0)

        return round(score, 3)

    def _clean_concept(
        self,
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return (
            str(value)
            .lower()
            .strip()
            .replace("_", " ")
        )

    def _is_valid_concept(
        self,
        concept: str,
    ) -> bool:

        if not concept:
            return False

        if len(concept) < 4:
            return False

        forbidden_prefixes = [
            "claim:",
            "metric:",
            "agent:",
            "strategy:",
            "assumption:",
            "missing_dimension:",
            "alternative_hypothesis:",
        ]

        if any(
            concept.startswith(prefix)
            for prefix in forbidden_prefixes
        ):
            return False

        if concept in self._function_words():
            return False

        if concept in self._internal_cognitive_terms():
            return False

        return True

    def _function_words(
        self,
    ) -> set[str]:

        return {
            # French
            "alors", "apres", "après", "avec", "dans", "donc",
            "elle", "elles", "encore", "entre", "mais", "meme",
            "même", "nous", "pour", "quand", "quoi", "sans",
            "sous", "tout", "tous", "très", "tres", "vous",

            # English
            "about", "after", "again", "also", "because", "before",
            "between", "could", "should", "there", "these", "those",
            "under", "where", "which", "while", "would",

            # Spanish
            "ahora", "aunque", "como", "cuando", "desde", "donde",
            "entonces", "entre", "hasta", "para", "pero", "porque",
            "sobre", "tambien", "también",

            # Filipino / Tagalog
            "ang", "ano", "bakit", "dahil", "dito", "gusto",
            "hindi", "ikaw", "isang", "kailan", "kung", "mga",
            "naman", "ngayon", "para", "paano", "saan", "sila",
            "tayo",
        }

    def _internal_cognitive_terms(
        self,
    ) -> set[str]:

        return {
            "mecroyance",
            "mécroyance",
            "certainty",
            "understanding",
            "revisability",
            "reduction",
            "closure",
            "grounding",
            "integration",
            "cognitive filter",
            "cognitive_filter",
            "nouscope",
            "doxa",
            "gnosis",
            "nous",
        }

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
