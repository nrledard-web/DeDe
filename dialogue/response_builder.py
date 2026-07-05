"""
DeDe - Response Builder

Builds a clear user-facing answer from DeDe's cognitive report.
"""

from typing import Any

from dialogue.language_pack import LanguagePack


class ResponseBuilder:

    name = "response_builder"

    def __init__(self):
        self.language_pack = LanguagePack()

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
        onboarding = report.get("onboarding", {})
        dialogue_decision = report.get("dialogue_decision", {})
        conversation_reasoning = report.get(
            "conversation_reasoning",
            {},
        )
        dialogue_profile = report.get(
            "dialogue_profile",
            {},
        )
        cognitive_feedback = report.get("cognitive_feedback", {})
        llm_bridge_response = report.get("llm_bridge_response", {})
        summary = report.get("summary", {})

        dialogue = report.get("dialogue", {})
        user_memory = report.get("user_memory", {})
        dede_identity = report.get("dede_identity", {})

        # --------------------------------------------------
        # Build answer
        # --------------------------------------------------

        answer_parts = []
        
        if onboarding.get("message"):
            answer_parts.append(
                onboarding["message"]
            )
        
        if dialogue.get("response"):
            answer_parts.append(
                dialogue["response"]
            )
            
        # Cognitive autonomy:
        # DeDe does not add conversational steering by default.
        conversational_intro = None

        if knowledge.get("found"):
            answer_parts.append(
                knowledge.get("answer", "")
            )

        llm_json = llm_bridge_response.get("parsed_json")

        if (
            llm_json
            and llm_json.get("user_facing_response")
            and not dialogue.get("response")
        ):
            answer_parts.append(
                llm_json["user_facing_response"]
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

        # Cognitive autonomy:
        # DeDe does not generate follow-up questions by default.
        follow_up_question = None

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
        dialogue_profile: dict[str, Any] | None = None,
    ) -> str | None:

        dialogue_profile = dialogue_profile or {}

        language = dialogue_profile.get("language", "en")

        move = conversation_reasoning.get("move")
        current_topic = conversation_reasoning.get("current_topic")
        reference_topic = conversation_reasoning.get("reference_topic")

        if move != "continue_thread":
            return None

        if current_topic and reference_topic:
            return self.language_pack.get(
                language,
                "continue_with_reference",
                reference_topic=reference_topic,
                current_topic=current_topic,
            )

        if current_topic:
            return self.language_pack.get(
                language,
                "continue_with_topic",
                current_topic=current_topic,
            )

        return self.language_pack.get(
            language,
            "continue_generic",
        )

    # --------------------------------------------------
    # Follow-up Question Builder
    # --------------------------------------------------

    def _build_follow_up_question(
        self,
        dialogue_decision: dict[str, Any],
        cognitive_feedback: dict[str, Any],
        conversation_reasoning: dict[str, Any] | None = None,
        dialogue_profile: dict[str, Any] | None = None,
    ) -> str | None:

        conversation_reasoning = conversation_reasoning or {}
        dialogue_profile = dialogue_profile or {}

        language = dialogue_profile.get("language", "en")

        # --------------------------------------------------
        # Conversation Reasoner
        # --------------------------------------------------

        if conversation_reasoning.get("next_prompt"):
            return conversation_reasoning["next_prompt"]

        if conversation_reasoning.get("move") == "continue_thread":
            current_topic = conversation_reasoning.get("current_topic")

            if current_topic:
                return self.language_pack.get(
                    language,
                    "follow_up_with_topic",
                    current_topic=current_topic,
                )

            return self.language_pack.get(
                language,
                "follow_up_generic",
            )

        # --------------------------------------------------
        # LLM Questions
        # --------------------------------------------------

        questions = cognitive_feedback.get(
            "new_questions",
            [],
        )

        if questions and language == "en":
            return questions[0]

        # --------------------------------------------------
        # Missing Dimensions
        # --------------------------------------------------

        missing_dimensions = cognitive_feedback.get(
            "new_missing_dimensions",
            [],
        )

        if missing_dimensions:
            return self.language_pack.get(
                language,
                "missing_dimension",
                dimension=missing_dimensions[0],
            )

        # --------------------------------------------------
        # Clarification
        # --------------------------------------------------

        if dialogue_decision.get(
            "needs_clarification",
        ):
            return self.language_pack.get(
                language,
                "clarification",
            )

        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        return None
