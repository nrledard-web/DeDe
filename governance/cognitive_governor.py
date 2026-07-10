"""
DeDe - Cognitive Governor

Controls cognitive and epistemic decisions before the LLM answers.

Current responsibilities:
- decide whether a web search is required;
- distinguish explicit search requests from ordinary dialogue;
- preserve information provenance;
- prevent DeDe from claiming that a search occurred when it did not.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


class CognitiveGovernor:

    name = "cognitive_governor"

    # --------------------------------------------------
    # Search Decision
    # --------------------------------------------------

    def decide_search(
        self,
        text: str,
        search_mode: str,
        conversation_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        conversation_context = conversation_context or {}

        normalized_mode = (
            search_mode
            or "off"
        ).lower().strip()

        normalized_text = self._normalize(text)

        # --------------------------------------------------
        # Search Disabled
        # --------------------------------------------------

        if normalized_mode == "off":
            return {
                "engine": self.name,
                "status": "ready",
                "mode": normalized_mode,
                "should_search": False,
                "decision": "skip_search",
                "reason": "Search is disabled by the user.",
                "explicit_request": False,
                "automatic_need": False,
            }

        # --------------------------------------------------
        # Forced Search
        # --------------------------------------------------

        if normalized_mode == "always":
            return {
                "engine": self.name,
                "status": "ready",
                "mode": normalized_mode,
                "should_search": True,
                "decision": "perform_search",
                "reason": "Search is forced for every message.",
                "explicit_request": True,
                "automatic_need": True,
            }

        # --------------------------------------------------
        # Greeting and Simple Dialogue Protection
        # --------------------------------------------------

        if self._is_simple_dialogue(normalized_text):
            return {
                "engine": self.name,
                "status": "ready",
                "mode": normalized_mode,
                "should_search": False,
                "decision": "skip_search",
                "reason": (
                    "The message is simple conversational dialogue "
                    "and does not require external information."
                ),
                "explicit_request": False,
                "automatic_need": False,
            }

        explicit_request = self._contains_explicit_search_request(
            normalized_text
        )

        # --------------------------------------------------
        # On Request Mode
        # --------------------------------------------------

        if normalized_mode == "on_request":
            return {
                "engine": self.name,
                "status": "ready",
                "mode": normalized_mode,
                "should_search": explicit_request,
                "decision": (
                    "perform_search"
                    if explicit_request
                    else "skip_search"
                ),
                "reason": (
                    "The user explicitly requested external search."
                    if explicit_request
                    else (
                        "No explicit request for links, sources, "
                        "verification or web search was detected."
                    )
                ),
                "explicit_request": explicit_request,
                "automatic_need": False,
            }

        # --------------------------------------------------
        # Governor Mode
        # --------------------------------------------------

        automatic_need = self._requires_external_verification(
            text=text,
            normalized_text=normalized_text,
            conversation_context=conversation_context,
        )

        should_search = (
            explicit_request
            or automatic_need
        )

        return {
            "engine": self.name,
            "status": "ready",
            "mode": normalized_mode,
            "should_search": should_search,
            "decision": (
                "perform_search"
                if should_search
                else "skip_search"
            ),
            "reason": self._build_search_reason(
                explicit_request=explicit_request,
                automatic_need=automatic_need,
            ),
            "explicit_request": explicit_request,
            "automatic_need": automatic_need,
        }

    # --------------------------------------------------
    # Explicit Search Request Detection
    # --------------------------------------------------

    def _contains_explicit_search_request(
        self,
        normalized_text: str,
    ) -> bool:

        markers = [
            # French
            "cherche",
            "chercher",
            "recherche",
            "rechercher",
            "trouve",
            "trouver",
            "verifie",
            "verifier",
            "donne moi des liens",
            "donne-moi des liens",
            "des liens sur",
            "des sources sur",
            "sur internet",
            "sur le web",

            # English
            "search for",
            "look up",
            "find links",
            "find sources",
            "give me links",
            "give me sources",
            "check online",
            "verify online",
            "on the web",
            "on the internet",

            # Spanish
            "busca",
            "buscar",
            "encuentra",
            "dame enlaces",
            "dame fuentes",
            "verifica",
            "en internet",
            "en la web",

            # Filipino / Tagalog
            "hanap",
            "hanapin",
            "maghanap",
            "bigyan mo ako ng link",
            "bigyan mo ako ng mga link",
            "mga sanggunian",
            "mga source",
            "suriin sa internet",
            "sa web",
            "sa internet",
        ]

        return any(
            marker in normalized_text
            for marker in markers
        )

    # --------------------------------------------------
    # Automatic Verification Need
    # --------------------------------------------------

    def _requires_external_verification(
        self,
        text: str,
        normalized_text: str,
        conversation_context: dict[str, Any],
    ) -> bool:

        current_information_markers = [
            # French
            "aujourd hui",
            "actuellement",
            "dernier",
            "derniere",
            "recemment",
            "actualite",
            "prix",
            "cours actuel",
            "qui est",

            # English
            "today",
            "currently",
            "latest",
            "recent",
            "news",
            "current price",
            "who is",

            # Spanish
            "hoy",
            "actualmente",
            "ultimo",
            "ultima",
            "reciente",
            "noticias",
            "precio actual",
            "quien es",

            # Filipino / Tagalog
            "ngayon",
            "kasalukuyan",
            "pinakabagong",
            "balita",
            "presyo ngayon",
            "sino si",
        ]

        if any(
            marker in normalized_text
            for marker in current_information_markers
        ):
            return True

        # A sequence of two or more capitalized words may represent
        # a person, publication, institution or public entity.
        proper_name_pattern = re.compile(
            r"\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ'-]+"
            r"(?:\s+[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ'-]+)+\b"
        )

        if proper_name_pattern.search(text):
            return True

        recent_topics = conversation_context.get(
            "recent_topics",
            [],
        )

        reference_markers = [
            "lui",
            "elle",
            "cette personne",
            "cet auteur",
            "ce chercheur",
            "sur lui",
            "sur elle",
            "him",
            "her",
            "this person",
            "this author",
            "sobre el",
            "sobre ella",
            "esa persona",
            "tungkol sa kanya",
            "siya",
        ]

        if recent_topics and any(
            marker in normalized_text
            for marker in reference_markers
        ):
            return True

        return False

    # --------------------------------------------------
    # Simple Dialogue Detection
    # --------------------------------------------------

    def _is_simple_dialogue(
        self,
        normalized_text: str,
    ) -> bool:

        cleaned = normalized_text.strip()

        simple_messages = {
            # French
            "bonjour",
            "bonjour dede",
            "salut",
            "salut dede",
            "bonsoir",
            "merci",
            "merci dede",
            "comment vas tu",
            "comment allez vous",

            # English
            "hello",
            "hello dede",
            "hi",
            "hi dede",
            "thanks",
            "thank you",
            "how are you",

            # Spanish
            "hola",
            "hola dede",
            "gracias",
            "como estas",

            # Filipino / Tagalog
            "kumusta",
            "kumusta dede",
            "kamusta",
            "salamat",
            "maraming salamat",
        }

        if cleaned in simple_messages:
            return True

        word_count = len(cleaned.split())

        conversational_starts = [
            "bonjour",
            "salut",
            "hello",
            "hi",
            "hola",
            "kumusta",
            "kamusta",
            "merci",
            "thanks",
            "gracias",
            "salamat",
        ]

        return (
            word_count <= 3
            and any(
                cleaned.startswith(marker)
                for marker in conversational_starts
            )
        )

    # --------------------------------------------------
    # Search Decision Explanation
    # --------------------------------------------------

    def _build_search_reason(
        self,
        explicit_request: bool,
        automatic_need: bool,
    ) -> str:

        if explicit_request and automatic_need:
            return (
                "The user explicitly requested a search and the subject "
                "also requires external verification."
            )

        if explicit_request:
            return (
                "The user explicitly requested links, sources, "
                "verification or web search."
            )

        if automatic_need:
            return (
                "The Governor detected information that should be "
                "externally verified before answering."
            )

        return (
            "The message can be answered without external search."
        )

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
            search_result.get("status") == "success"
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

        governed_prompt = (
            full_prompt
            + "\n\n"
            + "COGNITIVE GOVERNOR RULES:\n\n"
            + provenance_rules
        )

        previous_governance = llm_package.get(
            "cognitive_governor",
            {},
        )

        llm_package["full_prompt"] = governed_prompt

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

        lines = []

        lines.append(
            "You must distinguish clearly between:"
        )
        lines.append(
            "- information retrieved from web search;"
        )
        lines.append(
            "- information retrieved from memory;"
        )
        lines.append(
            "- general internal knowledge;"
        )
        lines.append(
            "- hypothesis or reconstruction."
        )
        lines.append("")

        if search_performed and search_relevant:
            lines.append(
                "A web search was performed and relevant results are available."
            )
            lines.append(
                "You may say that the answer uses retrieved web results."
            )
            lines.append(
                "When useful, include the supplied URLs."
            )
        else:
            lines.append(
                "No relevant web search result is available."
            )
            lines.append(
                "You must not say or imply that DeDe searched the web."
            )
            lines.append(
                "Do not invent links, sources, titles, biographies "
                "or public credentials."
            )

        lines.append("")

        if memory_available:
            lines.append(
                "Relevant memory is available. Use it carefully, "
                "but do not present memory as external verification."
            )
        else:
            lines.append(
                "No relevant memory is available. Do not invent "
                "personal or biographical information."
            )

        lines.append("")
        lines.append(
            "If evidence is missing, express epistemic caution."
        )

        return "\n".join(lines)

    # --------------------------------------------------
    # Text Normalization
    # --------------------------------------------------

    def _normalize(
        self,
        text: str,
    ) -> str:

        lowered = str(text).lower().strip()

        decomposed = unicodedata.normalize(
            "NFKD",
            lowered,
        )

        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )

        return " ".join(
            without_accents.split()
        )
