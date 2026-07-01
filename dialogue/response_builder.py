"""
DeDe - Response Builder

Builds a clear user-facing answer from DeDe's cognitive report.
"""

from typing import Any


class ResponseBuilder:

    name = "response_builder"

    # --------------------------------------------------
    # Main Builder
    # --------------------------------------------------

    def build(
        self,
        report: dict[str, Any],
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Context extraction
        # --------------------------------------------------

        knowledge = report.get("knowledge", {})
        dialogue_decision = report.get("dialogue_decision", {})
        conversation_reasoning = report.get(
            "conversation_reasoning",
            {},
        )
        cognitive_feedback = report.get("cognitive_feedback", {})
        llm_bridge_response = report.get("llm_bridge_response", {})
        summary = report.get("summary", {})

        # --------------------------------------------------
        # Build answer
        # --------------------------------------------------

        answer_parts = []

        conversational_intro = self._build_conversational_intro(
            conversation_reasoning,
        )

        if conversational_intro:
            answer_parts.append(conversational_intro)

        if knowledge.get("found"):
            answer_parts.append(
                knowledge.get("answer", "")
            )

        llm_json = llm_bridge_response.get("parsed_json")

        if llm_json and llm_json.get("summary"):
            answer_parts.append(
                llm_json["summary"]
            )

        if not answer_parts:
            answer_parts.append(
                summary.get("diagnosis", "")
            )

        final_answer = "\n\n".join(
            part
            for part in answer_parts
            if part
        )

        if not final_answer:
            final_answer = (
                "DeDe has analyzed the input, but no clear "
                "user-facing answer could be generated yet."
            )

        # --------------------------------------------------
        # Follow-up question
        # --------------------------------------------------

        follow_up_question = self._build_follow_up_question(
            dialogue_decision,
            cognitive_feedback,
            conversation_reasoning,
        )

        # --------------------------------------------------
        # Final response
        # --------------------------------------------------

        return {
            "builder": self.name,
            "status": "ready",
            "conversation_mode": dialogue_decision.get(
                "strategy",
                "direct_answer",
            ),
            "final_answer": final_answer,
            "follow_up_question": follow_up_question,
            "used_llm": (
                llm_bridge_response.get("status")
                == "success"
            ),
            "used_local_knowledge": knowledge.get(
                "found",
                False,
            ),
            "summary": (
                "User-facing response built from "
                "DeDe report."
            ),
        }

    # --------------------------------------------------
    # Conversational Intro Builder
    # --------------------------------------------------

    def _build_conversational_intro(
        self,
        conversation_reasoning: dict[str, Any],
    ) -> str | None:

        move = conversation_reasoning.get("move")
        current_topic = conversation_reasoning.get("current_topic")
        reference_topic = conversation_reasoning.get("reference_topic")

        if move != "continue_thread":
            return None

        if current_topic and reference_topic:
            return (
                f"En continuité avec {reference_topic}, "
                f"on peut appliquer la même mécanique à {current_topic}."
            )

        if current_topic:
            return (
                f"Oui, on peut prolonger la réflexion vers {current_topic}."
            )

        return (
            "Oui, on peut poursuivre dans le même fil de réflexion."
        )

    # --------------------------------------------------
    # Follow-up Question Builder
    # --------------------------------------------------

    def _build_follow_up_question(
        self,
        dialogue_decision: dict[str, Any],
        cognitive_feedback: dict[str, Any],
        conversation_reasoning: dict[str, Any] | None = None,
    ) -> str | None:

        conversation_reasoning = (
            conversation_reasoning or {}
        )

        # --------------------------------------------------
        # Conversation Reasoner
        # --------------------------------------------------

        if conversation_reasoning.get("next_prompt"):
            return conversation_reasoning["next_prompt"]

        if conversation_reasoning.get("move") == "continue_thread":
            current_topic = conversation_reasoning.get("current_topic")

            if current_topic:
                return (
                    f"Souhaites-tu maintenant comparer {current_topic} "
                    "avec un autre domaine, ou approfondir ce cas précis ?"
                )

            return (
                "Souhaites-tu continuer avec un autre domaine "
                "ou approfondir ce fil ?"
            )

        # --------------------------------------------------
        # LLM Questions
        # --------------------------------------------------

        questions = cognitive_feedback.get(
            "new_questions",
            [],
        )

        if questions:
            return questions[0]

        # --------------------------------------------------
        # Missing Dimensions
        # --------------------------------------------------

        missing_dimensions = cognitive_feedback.get(
            "new_missing_dimensions",
            [],
        )

        if missing_dimensions:
            return (
                "Souhaites-tu préciser cette dimension : "
                f"{missing_dimensions[0]}"
            )

        # --------------------------------------------------
        # Clarification
        # --------------------------------------------------

        if dialogue_decision.get(
            "needs_clarification",
        ):
            return (
                "Souhaites-tu une réponse courte, "
                "technique, philosophique ou "
                "orientée application ?"
            )

        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        return None
