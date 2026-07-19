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

import json
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
        Build a language-independent semantic classification prompt.

        A single fast model call determines:
        - whether external search is required;
        - canonical English concepts;
        - relevant historical counterpoint identifiers.

        The user message may be written in any language.
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
                "Use SEARCH when the user requests external information, "
                "links, sources, verification or research, or when a "
                "substantive question about an ideology, doctrine, political "
                "system, religious system or economic model requires "
                "historical evidence and human consequences. "
                "Use SKIP for greetings, thanks, creative writing, casual "
                "conversation or explanations without a material historical "
                "or empirical dimension."
            )

        else:
            decision_policy = (
                "Use SEARCH whenever external verification is materially "
                "needed, including current facts, historical consequences, "
                "laws, public figures, disputed quantitative claims, doctrines "
                "or claims that cannot be grounded safely from the supplied "
                "context. Use SKIP only when external verification would not "
                "materially improve the answer."
            )

        return (
            "You are the multilingual semantic-classification layer of "
            "an AI reasoning system.\n\n"

            f"Search mode: {normalized_mode}\n\n"
            f"Search policy: {decision_policy}\n\n"

            "Analyze the meaning of the user message in its original language. "
            "Do not depend on literal English keywords.\n\n"

            "Produce canonical_concepts as short English concept labels. "
            "Translate and normalize the meaning, not every individual word.\n\n"

            "Available historical counterpoint identifiers:\n"
            "- islamic_thought: use when the message materially concerns Islam, "
            "Muslim faith, Islamic theology or philosophy, political Islam, "
            "Islamism, jihadism, Sharia, Falsafa, Kalam, Mu'tazilism or closely "
            "related Islamic intellectual and historical questions.\n\n"

            "Use only identifiers from the available list. "
            "Return an empty counterpoint_ids list when none is relevant.\n\n"

            "Important rules:\n"
            "- Do not answer the user's question.\n"
            "- Do not add explanations outside the JSON object.\n"
            "- A greeting alone must use SKIP.\n"
            "- decision must be exactly SEARCH or SKIP.\n"
            "- canonical_concepts must contain English labels.\n"
            "- counterpoint_ids must contain only available identifiers.\n\n"

            "Return exactly this JSON structure:\n"
            "{\n"
            '  "decision": "SEARCH",\n'
            '  "canonical_concepts": ["concept"],\n'
            '  "counterpoint_ids": ["islamic_thought"]\n'
            "}\n\n"

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
        Parse enriched semantic classification.

        The former one-word SEARCH or SKIP format remains
        supported as a safe backward-compatible fallback.
        """

        raw_response = str(
            model_response
            or ""
        ).strip()

        cleaned = (
            raw_response
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        # --------------------------------------------------
        # Backward compatibility
        # --------------------------------------------------

        legacy_decision = cleaned.upper()

        if legacy_decision in {
            "SEARCH",
            "SKIP",
        }:
            return {
                "status": "classified_legacy",
                "decision": legacy_decision,
                "canonical_concepts": [],
                "counterpoint_ids": [],
                "reason": (
                    "The semantic classifier returned the "
                    "legacy one-word decision."
                ),
                "raw_response": raw_response,
            }

        # --------------------------------------------------
        # Enriched JSON classification
        # --------------------------------------------------

        try:
            parsed = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            return {
                "status": "invalid_response",
                "decision": "SKIP",
                "canonical_concepts": [],
                "counterpoint_ids": [],
                "reason": (
                    "The semantic classifier returned invalid JSON. "
                    "Search and counterpoint retrieval were skipped safely."
                ),
                "raw_response": raw_response,
            }

        if not isinstance(parsed, dict):
            return {
                "status": "invalid_response",
                "decision": "SKIP",
                "canonical_concepts": [],
                "counterpoint_ids": [],
                "reason": (
                    "The semantic classification was not a JSON object."
                ),
                "raw_response": raw_response,
            }

        decision = str(
            parsed.get(
                "decision",
                "SKIP",
            )
        ).strip().upper()

        if decision not in {
            "SEARCH",
            "SKIP",
        }:
            decision = "SKIP"

        canonical_concepts = parsed.get(
            "canonical_concepts",
            [],
        )

        if not isinstance(
            canonical_concepts,
            list,
        ):
            canonical_concepts = []

        canonical_concepts = [
            str(concept).strip()
            for concept in canonical_concepts
            if str(concept).strip()
        ]

        requested_counterpoints = parsed.get(
            "counterpoint_ids",
            [],
        )

        if not isinstance(
            requested_counterpoints,
            list,
        ):
            requested_counterpoints = []

        allowed_counterpoints = {
            "islamic_thought",
        }

        counterpoint_ids = [
            str(counterpoint_id).strip()
            for counterpoint_id in requested_counterpoints
            if str(counterpoint_id).strip()
            in allowed_counterpoints
        ]

        return {
            "status": "classified",
            "decision": decision,
            "canonical_concepts": canonical_concepts,
            "counterpoint_ids": counterpoint_ids,
            "reason": (
                "The multilingual semantic classifier returned "
                "a search decision, canonical concepts and "
                "historical counterpoint identifiers."
            ),
            "raw_response": raw_response,
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
