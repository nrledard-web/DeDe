"""
DeDe - Response Builder

Builds a clear user-facing answer from DeDe's cognitive report.
"""

import json
from typing import Any

from dialogue.language_pack import LanguagePack


class ResponseBuilder:

    name = "response_builder"

    def build(
        self,
        report: dict[str, Any],
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Context extraction
        # --------------------------------------------------

        knowledge = report.get(
            "knowledge",
            {},
        )

        onboarding = report.get(
            "onboarding",
            {},
        )

        dialogue_decision = report.get(
            "dialogue_decision",
            {},
        )

        conversation_reasoning = report.get(
            "conversation_reasoning",
            {},
        )

        dialogue_profile = report.get(
            "dialogue_profile",
            {},
        )

        llm_bridge_response = report.get(
            "llm_bridge_response",
            {},
        )

        llm_interpretation = report.get(
            "llm_interpretation",
            {},
        )

        committee_reasoning = report.get(
            "committee_reasoning",
            {},
        )

        summary = report.get(
            "summary",
            {},
        )

        search_result = report.get(
            "search_result",
            {},
        )

        source_analysis = report.get(
            "source_analysis",
            {},
        )

        coherence_loop = (
            source_analysis.get(
                "coherence_loop",
                {},
            )
        )

        if not isinstance(
            coherence_loop,
            dict,
        ):
            coherence_loop = {}

        dialogue = report.get(
            "dialogue",
            {},
        )

        language = dialogue_profile.get(
            "language",
            "fr",
        )

        # --------------------------------------------------
        # Extract the final LLM response
        # --------------------------------------------------

        llm_direct_response = (
            self._clean_llm_text(
                llm_interpretation.get(
                    "user_facing_response",
                    "",
                )
            )
        )

        if not llm_direct_response:

            llm_direct_response = (
                llm_bridge_response.get(
                    "response",
                    "",
                )
                or (
                    llm_bridge_response.get(
                        "llm_engine",
                        {},
                    ).get(
                        "response",
                        "",
                    )
                )
            )

            llm_direct_response = (
                self._clean_llm_text(
                    llm_direct_response
                )
            )

        # --------------------------------------------------
        # Build answer
        # --------------------------------------------------

        answer_parts = []

        if onboarding.get(
            "message"
        ):
            answer_parts.append(
                onboarding["message"]
            )

        if llm_direct_response:

            provider_count = (
                committee_reasoning.get(
                    "source_count",
                    1,
                )
            )

            confidence = (
                committee_reasoning.get(
                    "confidence",
                    0.0,
                )
            )

            texts = self._committee_texts(
                language=language,
                confidence=confidence,
                provider_count=provider_count,
            )

            synthesis_parts = [
                texts.get(
                    "title",
                    "",
                ),
                llm_direct_response,
            ]

            # A comparative notice is shown only when
            # several models were genuinely consulted.
            if provider_count > 1:
                synthesis_parts.extend(
                    [
                        texts.get(
                            "analysis",
                            "",
                        ),
                        texts.get(
                            "confidence",
                            "",
                        ),
                    ]
                )

            answer_parts.append(
                "\n\n".join(
                    part
                    for part in synthesis_parts
                    if part
                )
            )

        else:

            # Search results are displayed directly only when
            # no synthesized LLM response is available.
            search_fallback_response = (
                self._build_search_response(
                    search_result=search_result,
                    language=language,
                )
            )

            if search_fallback_response:
                answer_parts.append(
                    search_fallback_response
                )

            elif dialogue.get(
                "response"
            ):
                answer_parts.append(
                    dialogue["response"]
                )

            elif knowledge.get(
                "found"
            ):
                answer_parts.append(
                    knowledge.get(
                        "answer",
                        "",
                    )
                )

        if not answer_parts:
            diagnosis = summary.get(
                "diagnosis",
                "",
            )

            if diagnosis:
                answer_parts.append(
                    diagnosis
                )

        final_answer = "\n\n".join(
            part
            for part in answer_parts
            if part
        )

        if not final_answer:
            final_answer = (
                "DeDe has analyzed the request, but no clear "
                "user-facing answer could be generated."
            )

        return {
            "builder": self.name,
            "status": "ready",
            "conversation_mode": (
                dialogue_decision.get(
                    "strategy",
                    "direct_answer",
                )
            ),
            "final_answer": final_answer,
            "follow_up_question": None,
            "used_llm": bool(
                llm_direct_response
            ),
            "used_local_knowledge": (
                knowledge.get(
                    "found",
                    False,
                )
            ),
            "search_fallback_used": bool(
                not llm_direct_response
                and search_result.get(
                    "results",
                    [],
                )
            ),
            "summary": (
                "User-facing response built from "
                "DeDe's governed report."
            ),
        }
    # --------------------------------------------------
    # LLM Cleaning
    # --------------------------------------------------

    def _clean_llm_text(
        self,
        text: str,
    ) -> str:

        if not text:
            return ""

        cleaned = text.strip()

        try:
            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                return (
                    parsed.get("user_facing_response")
                    or parsed.get("response")
                    or parsed.get("answer")
                    or cleaned
                )

        except Exception:
            pass

        return cleaned

    # --------------------------------------------------
    # Search Builder
    # --------------------------------------------------

    def _build_search_response(
        self,
        search_result: dict[str, Any],
        language: str,
    ) -> str | None:
        """
        Build a safe fallback list when no synthesized response exists.

        Only technically and topically admissible results are displayed.
        Raw snippets are not reproduced as a substitute for synthesis.
        """

        raw_results = search_result.get(
            "results",
            [],
        )

        if not isinstance(
            raw_results,
            list,
        ):
            return None

        admissible_results = []

        for item in raw_results:

            if not isinstance(
                item,
                dict,
            ):
                continue

            validation = item.get(
                "validation",
                {},
            )

            if not isinstance(
                validation,
                dict,
            ):
                validation = {}

            admissible = validation.get(
                "admissible",
                True,
            )

            url_valid = validation.get(
                "url_valid",
                True,
            )

            if (
                admissible
                and url_valid
            ):
                admissible_results.append(
                    item
                )

        if not admissible_results:
            return None

        if language == "en":
            heading = (
                "The synthesis model was unavailable. "
                "Here are the admissible search results:"
            )

        elif language == "es":
            heading = (
                "El modelo de síntesis no estaba disponible. "
                "Estos son los resultados de búsqueda admisibles:"
            )

        elif language == "fil":
            heading = (
                "Hindi available ang synthesis model. "
                "Narito ang mga katanggap-tanggap na resulta:"
            )

        else:
            heading = (
                "Le modèle de synthèse n’était pas disponible. "
                "Voici les résultats de recherche admissibles :"
            )

        lines = [
            heading,
            "",
        ]

        for index, item in enumerate(
            admissible_results[:5],
            start=1,
        ):

            title = str(
                item.get(
                    "title",
                    "",
                )
                or ""
            ).strip()

            url = str(
                item.get(
                    "url",
                    "",
                )
                or ""
            ).strip()

            if not title and not url:
                continue

            lines.append(
                f"{index}. {title}"
            )

            if url:
                lines.append(
                    url
                )

            lines.append("")

        return "\n".join(
            lines
        ).strip()

    def _committee_texts(
        self,
        language: str,
        confidence: float,
        provider_count: int = 1,
    ) -> dict[str, str]:
        """
        Build transparent synthesis labels.

        A single model is never presented as a cognitive comparison.
        Comparative language is used only when several providers
        genuinely contributed.
        """

        multiple_models = (
            provider_count > 1
        )

        if language == "en":
            return {
                "title": "DeDe synthesis:",
                "analysis": (
                    "Comparative analysis: several reasoning models "
                    "were consulted and their outputs were compared."
                    if multiple_models
                    else ""
                ),
                "confidence": (
                    f"Comparative confidence: "
                    f"{round(confidence * 100)}%."
                    if multiple_models
                    else ""
                ),
            }

        if language == "es":
            return {
                "title": "Síntesis DeDe:",
                "analysis": (
                    "Análisis comparativo: se consultaron varios "
                    "modelos de razonamiento y se compararon sus resultados."
                    if multiple_models
                    else ""
                ),
                "confidence": (
                    f"Confianza comparativa: "
                    f"{round(confidence * 100)}%."
                    if multiple_models
                    else ""
                ),
            }

        if language == "fil":
            return {
                "title": "Sintesis ni DeDe:",
                "analysis": (
                    "Paghahambing na pagsusuri: maraming reasoning "
                    "model ang kinonsulta at inihambing ang kanilang tugon."
                    if multiple_models
                    else ""
                ),
                "confidence": (
                    f"Antas ng paghahambing: "
                    f"{round(confidence * 100)}%."
                    if multiple_models
                    else ""
                ),
            }

        return {
            "title": "Synthèse DeDe :",
            "analysis": (
                "Analyse comparative : plusieurs modèles de "
                "raisonnement ont été consultés et leurs productions "
                "ont été comparées."
                if multiple_models
                else ""
            ),
            "confidence": (
                f"Confiance comparative : "
                f"{round(confidence * 100)}%."
                if multiple_models
                else ""
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
