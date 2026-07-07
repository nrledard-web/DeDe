"""
DeDe - Response Builder

Builds a clear user-facing answer from DeDe's cognitive report.
"""

import json
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
        committee_reasoning = report.get("committee_reasoning", {})
        summary = report.get("summary", {})
        search_result = report.get("search_result", {})

        dialogue = report.get("dialogue", {})
        user_memory = report.get("user_memory", {})
        dede_identity = report.get("dede_identity", {})

        # --------------------------------------------------
        # Build answer
        # --------------------------------------------------

        answer_parts = []

        search_direct_response = self._build_search_response(
            search_result=search_result,
            language=dialogue_profile.get("language", "fr"),
        )
        
        if search_direct_response:
            answer_parts.append(search_direct_response)

        if onboarding.get("message"):
            answer_parts.append(
                onboarding["message"]
            )

        llm_direct_response = ""

        if committee_reasoning.get("status") == "ready":
            consensus = committee_reasoning.get("consensus", [])
            confidence = committee_reasoning.get("confidence", 0.0)
            language = dialogue_profile.get("language", "fr")

            if consensus:
                provider_count = committee_reasoning.get("source_count", 1)
                
                texts = self._committee_texts(
                    language=language,
                    confidence=confidence,
                    provider_count=provider_count,
                )

                llm_parts = [
                    texts["title"],
                    "\n\n".join(consensus[1:2] or consensus),
                    texts["analysis"],
                ]
                
                if texts["confidence"]:
                    llm_parts.append(texts["confidence"])
                
                llm_direct_response = "\n\n".join(
                    part for part in llm_parts if part
                )

        else:
            llm_direct_response = (
                llm_bridge_response.get("response")
                or (
                    llm_bridge_response.get("llm_engine", {})
                    .get("response", "")
                )
            )

            if llm_direct_response:
                try:
                    parsed = json.loads(llm_direct_response)

                    if isinstance(parsed, dict):
                        llm_direct_response = (
                            parsed.get("user_facing_response")
                            or parsed.get("response")
                            or llm_direct_response
                        )
                except Exception:
                    pass

        if llm_direct_response:
            answer_parts.append(llm_direct_response)

        elif dialogue.get("response"):
            answer_parts.append(
                dialogue["response"]
            )

        if knowledge.get("found"):
            answer_parts.append(
                knowledge.get("answer", "")
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

    def _build_search_response(
        self,
        search_result: dict[str, Any],
        language: str,
    ) -> str | None:

        results = search_result.get("results", [])

        if not results:
            return None

        lines = []

        if language == "en":
            lines.append("Here are some web results I found:")
        elif language == "es":
            lines.append("Aquí tienes algunos resultados encontrados en la web:")
        elif language == "fil":
            lines.append("Narito ang ilang resulta na nahanap sa web:")
        else:
            lines.append("Voici quelques résultats trouvés sur le web :")

        lines.append("")

        for index, item in enumerate(results[:5], start=1):
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("snippet", "")

            lines.append(f"{index}. {title}")
            if snippet:
                lines.append(snippet)
            if url:
                lines.append(url)
            lines.append("")

        return "\n".join(lines)

    def _committee_texts(
        self,
        language: str,
        confidence: float,
        provider_count: int = 1,
    ) -> dict[str, str]:

        if language == "en":
            return {
                "title": "DeDe synthesis:",
                "analysis": (
                    "Cognitive analysis: DeDe used the selected model "
                    "as reasoning material."
                    if provider_count <= 1
                    else "Cognitive analysis: several models were consulted. "
                    "DeDe compared their answers before producing a final response."
                ),
                "confidence": (
                    ""
                    if provider_count <= 1
                    else f"Comparative confidence: {round(confidence * 100)}%."
                ),
            }

        if language == "es":
            return {
                "title": "Síntesis DeDe:",
                "analysis": (
                    "Análisis cognitivo: DeDe utilizó el modelo seleccionado "
                    "como material de razonamiento."
                    if provider_count <= 1
                    else "Análisis cognitivo: se consultaron varios modelos. "
                    "DeDe comparó sus respuestas antes de producir una respuesta final."
                ),
                "confidence": (
                    ""
                    if provider_count <= 1
                    else f"Confianza comparativa: {round(confidence * 100)}%."
                ),
            }

        if language == "fil":
            return {
                "title": "Sintesis ni DeDe:",
                "analysis": (
                    "Pagsusuring pangkognitibo: ginamit ni DeDe ang napiling modelo "
                    "bilang batayan ng pangangatwiran."
                    if provider_count <= 1
                    else "Pagsusuring pangkognitibo: maraming modelo ang kinonsulta. "
                    "Inihambing ni DeDe ang kanilang mga sagot bago bumuo ng huling tugon."
                ),
                "confidence": (
                    ""
                    if provider_count <= 1
                    else f"Tinatayang antas ng paghahambing: {round(confidence * 100)}%."
                ),
            }

        return {
            "title": "Synthèse DeDe :",
            "analysis": (
                "Analyse cognitive : DeDe a utilisé le modèle sélectionné "
                "comme matière de raisonnement."
                if provider_count <= 1
                else "Analyse cognitive : plusieurs modèles ont été consultés. "
                "DeDe a comparé leurs réponses avant de produire une réponse finale."
            ),
            "confidence": (
                ""
                if provider_count <= 1
                else f"Confiance comparative : {round(confidence * 100)}%."
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
