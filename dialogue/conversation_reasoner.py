"""
DeDe - Conversation Reasoner

Chooses the next conversational move from the current report
and short-term conversation context.
"""

from typing import Any


class ConversationReasoner:

    name = "conversation_reasoner"

    def reason(
        self,
        text: str,
        conversation_context: dict[str, Any],
        dialogue_decision: dict[str, Any],
        cognitive_feedback: dict[str, Any],
        summary: dict[str, Any],
    ) -> dict[str, Any]:

        turn_count = conversation_context.get("turn_count", 0)
        recent_topics = conversation_context.get("recent_topics", [])
        text_lower = text.lower().strip()

        is_follow_up = self._is_follow_up(
            text_lower,
            turn_count,
            recent_topics,
        )

        questions = cognitive_feedback.get("new_questions", [])
        missing_dimensions = cognitive_feedback.get(
            "new_missing_dimensions",
            [],
        )

        if is_follow_up:
            move = "continue_thread"
            next_prompt = (
                "This appears to continue the previous conversation. "
                "Use the recent topics to preserve continuity."
            )

        elif questions:
            move = "ask_clarifying_question"
            next_prompt = questions[0]

        elif missing_dimensions:
            move = "clarify_missing_dimension"
            next_prompt = (
                "A useful next step is to clarify: "
                f"{missing_dimensions[0]}"
            )

        elif summary.get("mecroyance_risk", 0) > 0.5:
            move = "increase_revisability"
            next_prompt = (
                "The next step should increase revisability by asking "
                "for alternatives, evidence, or assumptions."
            )

        else:
            move = "offer_deeper_path"
            next_prompt = (
                "Would you like to go deeper conceptually, apply this "
                "to an example, or compare it with another domain?"
            )

        return {
            "reasoner": self.name,
            "status": "ready",
            "move": move,
            "is_follow_up": is_follow_up,
            "turn_count": turn_count,
            "recent_topics": recent_topics,
            "next_prompt": next_prompt,
            "summary": self._build_summary(
                move,
                is_follow_up,
                turn_count,
            ),
        }

    def _is_follow_up(
        self,
        text_lower: str,
        turn_count: int,
        recent_topics: list[str],
    ) -> bool:

        if turn_count <= 0:
            return False

        follow_up_markers = [
            "and ",
            "and in",
            "what about",
            "continue",
            "go on",
            "develop",
            "explain more",
            "compare",
            "same",
            "this",
            "that",
            "it",
            "in politics",
            "in religion",
            "in science",
            "in ai",
            "in education",
        ]

        if any(marker in text_lower for marker in follow_up_markers):
            return True

        for topic in recent_topics:
            if topic and topic.lower() in text_lower:
                return True

        if len(text_lower.split()) <= 5:
            return True

        return False

    def _build_summary(
        self,
        move: str,
        is_follow_up: bool,
        turn_count: int,
    ) -> str:

        if is_follow_up:
            return (
                f"Conversation reasoner selected '{move}' because the "
                f"message appears to continue a previous thread "
                f"after {turn_count} turn(s)."
            )

        return (
            f"Conversation reasoner selected '{move}' for the current turn."
        )
