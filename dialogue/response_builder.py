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
        dialogue_profile = report.get(
            "dialogue_profile",
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
            dialogue_profile,
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
            dialogue_profile,
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
        dialogue_profile: dict[str, Any] | None = None,
    ) -> str | None:

        dialogue_profile = dialogue_profile or {}

        language = dialogue_profile.get("language", "en")

        move = conversation_reasoning.get("move")
        current_topic = conversation_reasoning.get("current_topic")
        reference_topic = conversation_reasoning.get("reference_topic")

        if move != "continue_thread":
            return None

        # --------------------------------------------------
        # French
        # --------------------------------------------------

        if language == "fr":
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
        # Spanish
        # --------------------------------------------------

        if language == "es":

            if current_topic and reference_topic:
                return (
                    f"En continuidad con {reference_topic}, "
                    f"podemos aplicar la misma mecánica a {current_topic}."
                )

            if current_topic:
                return (
                    f"Sí, podemos prolongar la reflexión hacia {current_topic}."
                )

            return (
                "Sí, podemos continuar en la misma línea de reflexión."
            )
        # --------------------------------------------------
        # Filipino
        # --------------------------------------------------

        if language == "fil":

            if current_topic and reference_topic:
                return (
                    f"Sa pagpapatuloy ng usapan tungkol sa {reference_topic}, "
                    f"maaari nating ilapat ang parehong mekanismo sa {current_topic}."
                )

            if current_topic:
                return (
                    f"Oo, maaari nating palawakin ang pagtalakay tungkol sa {current_topic}."
                )

            return (
                "Oo, maaari nating ipagpatuloy ang parehong linya ng pag-iisip."
            )

        # --------------------------------------------------
        # English / Default
        # --------------------------------------------------

        if current_topic and reference_topic:
            return (
                f"Continuing from {reference_topic}, "
                f"we can apply the same mechanism to {current_topic}."
            )

        if current_topic:
            return (
                f"Yes, we can extend the reflection toward {current_topic}."
            )

        return (
            "Yes, we can continue in the same line of thought."
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

            if language == "fr":
                if current_topic:
                    return (
                        f"Souhaites-tu maintenant comparer {current_topic} "
                        "avec un autre domaine, ou approfondir ce cas précis ?"
                    )

                return (
                    "Souhaites-tu continuer avec un autre domaine "
                    "ou approfondir ce fil ?"
                )

            if language == "es":

                if current_topic:
                    return (
                        f"¿Quieres comparar ahora {current_topic} "
                        "con otro dominio, o profundizar este caso?"
                    )

                return (
                    "¿Quieres continuar con otro dominio "
                    "o profundizar esta línea?"
                )

            if language == "fil":

                
                if current_topic:
                    return (
                        f"Gusto mo bang ihambing ang {current_topic} "
                        "sa ibang larangan, o palalimin pa natin ito?"
                    )

                return (
                    "Gusto mo bang magpatuloy sa ibang larangan "
                    "o palalimin pa natin ang usaping ito?"
                )
            if current_topic:
                return (
                    f"Would you like to compare {current_topic} "
                    "with another domain, or go deeper into this case?"
                )

            return (
                "Would you like to continue with another domain, "
                "or go deeper into this thread?"
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
            if language == "fr":
                return (
                    "Souhaites-tu préciser cette dimension : "
                    f"{missing_dimensions[0]}"
                )

            if language == "es":
                return (
                    "¿Quieres precisar esta dimensión: "
                    f"{missing_dimensions[0]}?"
                )

            if language == "fil":
                return (
                    "Gusto mo bang linawin ang aspektong ito: "
                    f"{missing_dimensions[0]}?"
                )

            return (
                "Would you like to clarify this dimension: "
                f"{missing_dimensions[0]}?"
            )

        # --------------------------------------------------
        # Clarification
        # --------------------------------------------------

        if dialogue_decision.get(
            "needs_clarification",
        ):
            if language == "fr":
                return (
                    "Souhaites-tu une réponse courte, "
                    "technique, philosophique ou "
                    "orientée application ?"
                )

            if language == "es":
                return (
                    "¿Quieres una respuesta breve, técnica, "
                    "filosófica u orientada a la aplicación?"
                )

            if language == "fil":
                return (
                    "Gusto mo ba ng maikli, teknikal, pilosopikal, "
                    "o praktikal na paliwanag?"
                )

            return (
                "Would you like a short, technical, philosophical, "
                "or application-oriented answer?"
            )

        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        return None
