"""
DeDe - Cognitive Governor

Controls cognitive and epistemic decisions before the LLM answers.

Principles:
- no language-specific keyword lists;
- no personal markers;
- explicit search is controlled by the interface;
- automatic search is based on semantic classification;
- information provenance must remain explicit.
"""

from __future__ import annotations

from typing import Any


class CognitiveGovernor:
    """
    Governs search decisions and information provenance.

    The Governor does not attempt to understand natural language
    through lists of words.

    Search intent is supplied through:
    - an explicit interface decision;
    - or a semantic classification produced by a reasoning model.
    """

    name = "cognitive_governor"

    # --------------------------------------------------
    # Search Decision
    # --------------------------------------------------

    def decide_search(
        self,
        search_mode: str,
        explicit_request: bool = False,
        semantic_decision: str | None = None,
        semantic_reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Decide whether an external search should be performed.

        Parameters
        ----------
        search_mode:
            off, on_request, governor or always.

        explicit_request:
            Boolean supplied by the interface.
            It does not depend on language detection.

        semantic_decision:
            SEARCH or SKIP, normally produced by an LLM classifier.

        semantic_reason:
            Optional explanation supplied by the semantic classifier.
        """

        normalized_mode = (
            search_mode
            or "off"
        ).lower().strip()

        normalized_semantic_decision = (
            semantic_decision
            or ""
        ).upper().strip()

        # --------------------------------------------------
        # Search Disabled
        # --------------------------------------------------

        if normalized_mode == "off":
            return self._build_decision(
                mode=normalized_mode,
                should_search=False,
                reason="External search is disabled.",
                explicit_request=explicit_request,
                semantic_decision=normalized_semantic_decision,
            )

        # --------------------------------------------------
        # Forced Search
        # --------------------------------------------------

        if normalized_mode == "always":
            return self._build_decision(
                mode=normalized_mode,
                should_search=True,
                reason="External search is enabled for every message.",
                explicit_request=explicit_request,
                semantic_decision=normalized_semantic_decision,
            )

        # --------------------------------------------------
        # Search On Request
        # --------------------------------------------------

        if normalized_mode == "on_request":
            should_search = (
                bool(explicit_request)
                or normalized_semantic_decision == "SEARCH"
            )

            if explicit_request:
                reason = (
                    "External search was explicitly requested "
                    "for this message."
                )

            elif normalized_semantic_decision == "SEARCH":
                reason = (
                    semantic_reason
                    or (
                        "Semantic classification detected a request "
                        "for external information."
                    )
                )

            else:
                reason = (
                    semantic_reason
                    or (
                        "No external-search request was detected."
                    )
                )

            return self._build_decision(
                mode=normalized_mode,
                should_search=should_search,
                reason=reason,
                explicit_request=explicit_request,
                semantic_decision=normalized_semantic_decision,
            )

        # --------------------------------------------------
        # Semantic Governor
        # --------------------------------------------------

        if normalized_mode == "governor":
            should_search = (
                normalized_semantic_decision == "SEARCH"
            )

            return self._build_decision(
                mode=normalized_mode,
                should_search=should_search,
                reason=(
                    semantic_reason
                    or (
                        "Semantic classification requires external search."
                        if should_search
                        else (
                            "Semantic classification does not require "
                            "external search."
                        )
                    )
                ),
                explicit_request=explicit_request,
                semantic_decision=normalized_semantic_decision,
            )

        # --------------------------------------------------
        # Unknown Mode: Safe Default
        # --------------------------------------------------

        return self._build_decision(
            mode=normalized_mode,
            should_search=False,
            reason=(
                f"Unknown search mode '{normalized_mode}'. "
                "Search was skipped safely."
            ),
            explicit_request=explicit_request,
            semantic_decision=normalized_semantic_decision,
        )

    # --------------------------------------------------
    # Semantic Classification Prompt
    # --------------------------------------------------

    def build_search_classification_prompt(
        self,
        text: str,
        conversation_context: dict[str, Any] | None = None,
        search_mode: str = "governor",
    ) -> str:
        """
        Build a language-independent semantic search decision prompt.

        on_request:
            Search only when the user is requesting external information,
            sources, links, verification or web retrieval.

        governor:
            Search whenever external verification is materially required,
            even when it was not explicitly requested.
        """

        conversation_context = conversation_context or {}

        normalized_mode = (
            search_mode
            or "governor"
        ).lower().strip()

        recent_topics = conversation_context.get(
            "recent_topics",
            [],
        )

        recent_turns = conversation_context.get(
            "recent_turns",
            [],
        )

        context_summary = {
            "recent_topics": recent_topics[-3:],
            "recent_turns": recent_turns[-2:],
        }

        if normalized_mode == "on_request":
            decision_policy = (
                "Return SEARCH when the user is asking for external "
                "retrieval, web information, links, sources, references, "
                "verification, research, or information that clearly depends "
                "on consulting external material.\n\n"

                "Also return SEARCH for substantive questions about an "
                "ideology, doctrine, political system, religious system or "
                "economic model when historical applications, human "
                "consequences or factual claims are needed to confront "
                "theory with reality. Detect this semantically in every "
                "language; do not rely on keyword lists.\n\n"

                "Return SKIP for greetings, thanks, casual conversation, "
                "creative writing, reflection, ordinary explanation that "
                "has no material historical or empirical dimension, or "
                "summarization of supplied material."
            )

        else:
            decision_policy = (
                "Return SEARCH whenever external verification is materially "
                "needed, including current or changing facts, recent events, "
                "public figures, prices, schedules, laws, external sources, "
                "or claims that cannot be grounded safely from the supplied "
                "context.\n\n"

                "Return SEARCH for substantive analysis of an ideology, "
                "doctrine, political system, religious system or economic "
                "model whenever its theory must be confronted with historical "
                "applications, human consequences, recurring institutional "
                "mechanisms or disputed quantitative claims. Detect the "
                "category semantically in every language; do not rely on "
                "keyword lists.\n\n"

                "Return SKIP for greetings, thanks, introductions, casual "
                "conversation, creative writing, reflection, or requests "
                "answerable safely without external verification."
            )

        return (
            "You are the search-decision layer of an AI reasoning system.\n\n"
            f"Search mode: {normalized_mode}\n\n"
            f"{decision_policy}\n\n"
            "Important rules:\n"
            "- A greeting or conversational opening must return SKIP.\n"
            "- Do not answer the user's request.\n"
            "- Do not explain your decision.\n"
            "- Return exactly one word: SEARCH or SKIP.\n\n"
            f"Conversation context:\n{context_summary}\n\n"
            f"User message:\n{text}"
        )

    # --------------------------------------------------
    # Semantic Classification Parsing
    # --------------------------------------------------

    def parse_search_classification(
        self,
        model_response: str | None,
    ) -> dict[str, Any]:
        """
        Convert the semantic classifier response into a safe decision.

        Ambiguous or malformed output defaults to SKIP.
        """

        cleaned = (
            model_response
            or ""
        ).strip().upper()

        if cleaned == "SEARCH":
            return {
                "status": "classified",
                "decision": "SEARCH",
                "reason": (
                    "The semantic classifier determined that external "
                    "verification is required."
                ),
                "raw_response": model_response or "",
            }

        if cleaned == "SKIP":
            return {
                "status": "classified",
                "decision": "SKIP",
                "reason": (
                    "The semantic classifier determined that external "
                    "verification is not required."
                ),
                "raw_response": model_response or "",
            }

        return {
            "status": "invalid_response",
            "decision": "SKIP",
            "reason": (
                "The semantic classifier returned an invalid response. "
                "Search was skipped safely."
            ),
            "raw_response": model_response or "",
        }

    # --------------------------------------------------
    # Decision Structure
    # --------------------------------------------------

    def _build_decision(
        self,
        mode: str,
        should_search: bool,
        reason: str,
        explicit_request: bool,
        semantic_decision: str,
    ) -> dict[str, Any]:

        return {
            "engine": self.name,
            "status": "ready",
            "mode": mode,
            "should_search": should_search,
            "decision": (
                "perform_search"
                if should_search
                else "skip_search"
            ),
            "reason": reason,
            "explicit_request": explicit_request,
            "semantic_decision": semantic_decision or None,
        }

    # --------------------------------------------------
    # Prompt Provenance Governance
    # --------------------------------------------------

    def apply_to_prompt_package(
        self,
        llm_package: dict[str, Any],
        search_result: dict[str, Any] | None = None,
        search_validation: dict[str, Any] | None = None,
        search_summary: dict[str, Any] | None = None,
        retrieved_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        search_result = search_result or {}
        search_validation = search_validation or {}
        search_summary = search_summary or {}
        retrieved_memory = retrieved_memory or {}

        search_results = search_result.get(
            "results",
            [],
        )

        search_performed = (
            search_result.get("status")
            in {
                "success",
                "low_relevance",
            }
            and bool(search_results)
        )

        search_relevant = search_validation.get(
            "is_relevant",
            False,
        )

        memory_available = bool(
            retrieved_memory.get("relevant_facts")
            or retrieved_memory.get("relevant_notes")
        )

        provenance_rules = self._build_provenance_rules(
            search_performed=search_performed,
            search_relevant=search_relevant,
            memory_available=memory_available,
        )

        full_prompt = llm_package.get(
            "full_prompt",
            "",
        )

        llm_package["full_prompt"] = (
            full_prompt
            + "\n\n"
            + "COGNITIVE GOVERNOR RULES:\n\n"
            + provenance_rules
        )

        previous_governance = llm_package.get(
            "cognitive_governor",
            {},
        )

        llm_package["cognitive_governor"] = {
            **previous_governance,
            "engine": self.name,
            "status": "applied",
            "search_performed": search_performed,
            "search_relevant": search_relevant,
            "memory_available": memory_available,
            "summary": (
                "Cognitive provenance rules injected before LLM call."
            ),
        }

        return llm_package

    # --------------------------------------------------
    # Provenance Rules
    # --------------------------------------------------

    def _build_provenance_rules(
        self,
        search_performed: bool,
        search_relevant: bool,
        memory_available: bool,
    ) -> str:

        lines = [
            "Distinguish clearly between:",
            "- information retrieved from external search;",
            "- information retrieved from memory;",
            "- general internal knowledge;",
            "- hypothesis or reconstruction;",
            "",
        ]

        if search_performed:
            lines.extend(
                [
                    "External search results are available.",
                    (
                        "Use them only according to their demonstrated "
                        "relevance and reliability."
                    ),
                ]
            )

            if not search_relevant:
                lines.append(
                    "The retrieved results have limited relevance. "
                    "Express appropriate caution."
                )
        else:
            lines.extend(
                [
                    "No external search result is available.",
                    (
                        "Do not say or imply that an external search "
                        "was performed."
                    ),
                    (
                        "Do not invent links, sources, publications, "
                        "biographies or credentials."
                    ),
                ]
            )

        lines.append("")

        if memory_available:
            lines.append(
                "Relevant memory is available, but memory is not "
                "external verification."
            )
        else:
            lines.append(
                "No relevant memory is available. Do not invent "
                "personal information."
            )

        lines.extend(
            [
                "",
                (
                    "When evidence is missing or incomplete, preserve "
                    "epistemic caution and revisability."
                ),
            ]
        )

        return "\n".join(lines)
