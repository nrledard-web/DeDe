"""
DeDe - Conversation Reasoner

Chooses the next conversational move from the current report
and short-term conversation context.

This component does not speak directly to the user.
It produces conversational intentions for the Response Builder.
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
        last_user_input = conversation_context.get("last_user_input")
        text_lower = text.lower().strip()

        is_follow_up = self._is_follow_up(
            text_lower=text_lower,
            turn_count=turn_count,
            recent_topics=recent_topics,
        )

        current_topic = self._detect_current_topic(text_lower)
        reference_topic = self._detect_reference_topic(
            recent_topics=recent_topics,
            last_user_input=last_user_input,
        )

        questions = cognitive_feedback.get("new_questions", [])
        missing_dimensions = cognitive_feedback.get(
            "new_missing_dimensions",
            [],
        )

        if is_follow_up:
            move = "continue_thread"
            goal = "extend_previous_reasoning"
            style = "contextual_continuation"
            next_prompt = None

        elif questions:
            move = "ask_clarifying_question"
            goal = "clarify_user_intent"
            style = "clarifying"
            next_prompt = questions[0]

        elif missing_dimensions:
            move = "clarify_missing_dimension"
            goal = "make_missing_dimension_explicit"
            style = "exploratory"
            next_prompt = (
                "Souhaites-tu préciser cette dimension : "
                f"{missing_dimensions[0]}"
            )

        elif summary.get("mecroyance_risk", 0) > 0.5:
            move = "increase_revisability"
            goal = "restore_revisability"
            style = "recalibrating"
            next_prompt = (
                "Souhaites-tu examiner les hypothèses alternatives "
                "ou les présupposés implicites ?"
            )

        else:
            move = "offer_deeper_path"
            goal = "propose_next_depth"
            style = "open_continuation"
            next_prompt = (
                "Souhaites-tu approfondir le concept, l’appliquer à "
                "un exemple, ou le comparer avec un autre domaine ?"
            )

        return {
            "reasoner": self.name,
            "status": "ready",
            "move": move,
            "goal": goal,
            "style": style,
            "is_follow_up": is_follow_up,
            "turn_count": turn_count,
            "recent_topics": recent_topics,
            "reference_topic": reference_topic,
            "current_topic": current_topic,
            "next_prompt": next_prompt,
            "summary": self._build_summary(
                move=move,
                goal=goal,
                is_follow_up=is_follow_up,
                turn_count=turn_count,
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

    def _detect_current_topic(
        self,
        text_lower: str,
    ) -> str | None:

        domain_markers = {
            "politics": ["politic", "politics", "political"],
            "religion": ["religion", "religious", "faith"],
            "science": ["science", "scientific"],
            "ai": ["ai", "artificial intelligence", "llm"],
            "education": ["education", "school", "learning"],
            "media": ["media", "press", "journalism"],
        }

        for topic, markers in domain_markers.items():
            if any(marker in text_lower for marker in markers):
                return topic

        return None

    def _detect_reference_topic(
        self,
        recent_topics: list[str],
        last_user_input: str | None,
    ) -> str | None:

        if last_user_input:
            detected = self._detect_current_topic(
                last_user_input.lower()
            )

            if detected:
                return detected

        for topic in reversed(recent_topics):
            if topic not in [
                "mecroyance",
                "certainty",
                "understanding",
                "revisability",
                "reduction",
                "closure",
                "cognitive_filter",
            ]:
                return topic

        return None

    def _build_summary(
        self,
        move: str,
        goal: str,
        is_follow_up: bool,
        turn_count: int,
    ) -> str:

        if is_follow_up:
            return (
                f"Conversation reasoner selected '{move}' "
                f"with goal '{goal}' after {turn_count} previous turn(s)."
            )

        return (
            f"Conversation reasoner selected '{move}' "
            f"with goal '{goal}'."
        )
