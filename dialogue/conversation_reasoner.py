"""
DeDe - Conversation Reasoner

Chooses the next conversational move from the current report
and short-term conversation context.

This component does not speak directly to the user.
It produces conversational intentions for the Response Builder.

Principle:
- Multilingual continuation detection.
- No hard-coded subject domains.
- Uses previous focus_concept when the current message is elliptical.
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
        last_focus_concept = conversation_context.get("last_focus_concept")
        recent_focus_concepts = conversation_context.get(
            "recent_focus_concepts",
            [],
        )

        text_lower = text.lower().strip()

        current_topic = self._detect_current_topic(
            text_lower=text_lower,
            cognitive_feedback=cognitive_feedback,
        )

        reference_topic = self._detect_reference_topic(
            last_focus_concept=last_focus_concept,
            recent_focus_concepts=recent_focus_concepts,
            recent_topics=recent_topics,
        )

        is_follow_up = self._is_follow_up(
            text_lower=text_lower,
            turn_count=turn_count,
            current_topic=current_topic,
            reference_topic=reference_topic,
        )

        resolved_topic = (
            current_topic
            or reference_topic
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
            "resolved_topic": resolved_topic,
            "next_prompt": next_prompt,
            "summary": self._build_summary(
                move=move,
                goal=goal,
                is_follow_up=is_follow_up,
                turn_count=turn_count,
                resolved_topic=resolved_topic,
            ),
        }

    def _is_follow_up(
        self,
        text_lower: str,
        turn_count: int,
        current_topic: str | None,
        reference_topic: str | None,
    ) -> bool:

        if turn_count <= 0:
            return False

        word_count = len(text_lower.split())

        if current_topic and reference_topic:
            return True

        if word_count <= 6 and reference_topic:
            return True

        if self._has_continuation_marker(text_lower) and reference_topic:
            return True

        return False

    def _has_continuation_marker(
        self,
        text_lower: str,
    ) -> bool:

        markers = [
            # French
            "maintenant",
            "et sur",
            "et pour",
            "et contre",
            "en faveur",
            "contre",
            "synthèse",
            "synthese",
            "équilibrée",
            "equilibree",
            "pareil",
            "même chose",
            "meme chose",

            # English
            "now",
            "what about",
            "and about",
            "in favor",
            "against",
            "balanced",
            "same thing",

            # Spanish
            "ahora",
            "y sobre",
            "a favor",
            "en contra",
            "equilibrada",
            "lo mismo",

            # Filipino / Tagalog
            "ngayon",
            "pabor",
            "laban",
            "balanse",
            "pareho",
        ]

        return any(
            marker in text_lower
            for marker in markers
        )

    def _detect_current_topic(
        self,
        text_lower: str,
        cognitive_feedback: dict[str, Any],
    ) -> str | None:

        concepts = cognitive_feedback.get("new_concepts", [])

        for concept in concepts:
            clean = self._clean_concept(concept)

            if not self._is_internal_or_empty(clean):
                return clean

        return None

    def _detect_reference_topic(
        self,
        last_focus_concept: str | None,
        recent_focus_concepts: list[str],
        recent_topics: list[str],
    ) -> str | None:

        if last_focus_concept:
            return last_focus_concept

        if recent_focus_concepts:
            return recent_focus_concepts[-1]

        if recent_topics:
            return recent_topics[-1]

        return None

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

    def _is_internal_or_empty(
        self,
        concept: str,
    ) -> bool:

        if not concept:
            return True

        internal_terms = {
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

        return concept in internal_terms

    def _build_summary(
        self,
        move: str,
        goal: str,
        is_follow_up: bool,
        turn_count: int,
        resolved_topic: str | None,
    ) -> str:

        topic_text = (
            f" Resolved topic: {resolved_topic}."
            if resolved_topic
            else ""
        )

        if is_follow_up:
            return (
                f"Conversation reasoner selected '{move}' "
                f"with goal '{goal}' after {turn_count} previous turn(s)."
                f"{topic_text}"
            )

        return (
            f"Conversation reasoner selected '{move}' "
            f"with goal '{goal}'."
            f"{topic_text}"
        )
