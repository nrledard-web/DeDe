"""
DeDe - Cognitive Dialogue Manager

Decides the cognitive strategy before LLM use.

It determines whether DeDe should:
- answer directly
- ask a clarification question
- request evidence
- propose alternatives
- call an external LLM
- suspend judgment
"""

from typing import Any


class CognitiveDialogueManager:

    name = "cognitive_dialogue_manager"

    def decide(
        self,
        text: str,
        knowledge: dict[str, Any],
        cognitive_state: dict[str, Any],
        cognitive_reasoning: dict[str, Any],
    ) -> dict[str, Any]:

        text_lower = text.lower()

        orientation = cognitive_state.get("orientation", "unknown")
        missing_dimensions = cognitive_state.get("missing_dimensions", [])
        pressure = cognitive_state.get("pressure", [])
        protective = cognitive_state.get("protective_mechanisms", [])

        knowledge_found = knowledge.get("found", False)
        knowledge_confidence = knowledge.get("confidence", 0)

        is_definition_request = self._is_definition_request(text_lower)
        is_comparison_request = self._is_comparison_request(text_lower)
        is_explanation_request = self._is_explanation_request(text_lower)

        needs_clarification = bool(missing_dimensions)
        needs_alternatives = orientation == "pressure_dominant"
        needs_verification = not knowledge_found or knowledge_confidence < 0.65
        needs_external_llm = False
        should_answer_directly = False
        should_suspend_judgment = False

        if is_definition_request and knowledge_found:
            should_answer_directly = True
            needs_external_llm = False

        elif is_comparison_request or is_explanation_request:
            needs_external_llm = True

        elif needs_verification:
            needs_external_llm = True
            should_suspend_judgment = True

        elif orientation == "pressure_dominant":
            needs_external_llm = True

        strategy = self._choose_strategy(
            should_answer_directly=should_answer_directly,
            needs_external_llm=needs_external_llm,
            needs_clarification=needs_clarification,
            needs_alternatives=needs_alternatives,
            needs_verification=needs_verification,
            should_suspend_judgment=should_suspend_judgment,
        )

        return {
            "manager": self.name,
            "status": "ready",
            "strategy": strategy,
            "should_answer_directly": should_answer_directly,
            "needs_external_llm": needs_external_llm,
            "needs_clarification": needs_clarification,
            "needs_alternatives": needs_alternatives,
            "needs_verification": needs_verification,
            "should_suspend_judgment": should_suspend_judgment,
            "decision_factors": {
                "knowledge_found": knowledge_found,
                "knowledge_confidence": knowledge_confidence,
                "orientation": orientation,
                "pressure_count": len(pressure),
                "protective_mechanism_count": len(protective),
                "missing_dimension_count": len(missing_dimensions),
                "is_definition_request": is_definition_request,
                "is_comparison_request": is_comparison_request,
                "is_explanation_request": is_explanation_request,
            },
            "recommended_actions": self._build_actions(
                strategy=strategy,
                missing_dimensions=missing_dimensions,
            ),
            "summary": self._build_summary(
                strategy=strategy,
                needs_external_llm=needs_external_llm,
                needs_clarification=needs_clarification,
                needs_alternatives=needs_alternatives,
                needs_verification=needs_verification,
            ),
        }

    def _is_definition_request(
        self,
        text: str,
    ) -> bool:

        markers = [
            "what is",
            "what does",
            "define",
            "definition",
            "meaning of",
            "qu'est-ce",
            "c'est quoi",
            "définis",
            "definition de",
            "définition de",
        ]

        return any(marker in text for marker in markers)

    def _is_comparison_request(
        self,
        text: str,
    ) -> bool:

        markers = [
            "compare",
            "comparison",
            "versus",
            "vs",
            "difference",
            "différence",
            "compare",
            "comparer",
            "rapport avec",
        ]

        return any(marker in text for marker in markers)

    def _is_explanation_request(
        self,
        text: str,
    ) -> bool:

        markers = [
            "why",
            "how",
            "explain",
            "analyse",
            "analyze",
            "pourquoi",
            "comment",
            "explique",
        ]

        return any(marker in text for marker in markers)

    def _choose_strategy(
        self,
        should_answer_directly: bool,
        needs_external_llm: bool,
        needs_clarification: bool,
        needs_alternatives: bool,
        needs_verification: bool,
        should_suspend_judgment: bool,
    ) -> str:

        if should_answer_directly:
            return "direct_answer"

        if should_suspend_judgment:
            return "suspend_and_verify"

        if needs_external_llm and needs_clarification:
            return "llm_with_clarification"

        if needs_external_llm:
            return "llm_reasoning"

        if needs_clarification:
            return "clarify_before_answer"

        if needs_alternatives:
            return "offer_alternatives"

        if needs_verification:
            return "request_verification"

        return "answer_with_revisability"

    def _build_actions(
        self,
        strategy: str,
        missing_dimensions: list[str],
    ) -> list[str]:

        actions = []

        if strategy == "direct_answer":
            actions.append("Answer directly from DeDe knowledge base.")
            actions.append("Preserve revisability in the wording.")

        elif strategy == "suspend_and_verify":
            actions.append("Suspend strong conclusion.")
            actions.append("Request or search for verification.")

        elif strategy == "llm_with_clarification":
            actions.append("Use external LLM as reasoning assistant.")
            actions.append("Ask clarification around missing dimensions.")
            actions.append("Prevent overconfident answer.")

        elif strategy == "llm_reasoning":
            actions.append("Use external LLM for expanded reasoning.")
            actions.append("Keep DeDe cognitive state as primary context.")

        elif strategy == "clarify_before_answer":
            actions.append("Ask a clarifying question before answering.")

        elif strategy == "offer_alternatives":
            actions.append("Offer alternative hypotheses.")

        else:
            actions.append("Answer while preserving revisability.")

        for dimension in missing_dimensions[:3]:
            actions.append(f"Clarify missing dimension: {dimension}")

        return actions

    def _build_summary(
        self,
        strategy: str,
        needs_external_llm: bool,
        needs_clarification: bool,
        needs_alternatives: bool,
        needs_verification: bool,
    ) -> str:

        return (
            f"Dialogue strategy selected: {strategy}. "
            f"External LLM needed: {needs_external_llm}. "
            f"Clarification needed: {needs_clarification}. "
            f"Alternatives needed: {needs_alternatives}. "
            f"Verification needed: {needs_verification}."
        )
