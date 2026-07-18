"""
DeDe - LLM Connector

Builds a prompt package for future LLM reasoning.

The connector does not call an LLM yet.
It prepares structured context from:
- identity and memory
- foundational knowledge
- self model
- graph queries
- compiled cognitive state
- cognitive reasoning
"""

from typing import Any

from llm.llm_json_schema import build_json_instruction
from knowledge.foundational_knowledge import build_foundational_context
from core.dede_self_model import build_self_model_context


class LLMConnector:

    name = "llm_connector"

    def build_prompt_package(
        self,
        text: str,
        graph_queries: dict[str, Any],
        cognitive_state: dict[str, Any] | None = None,
        cognitive_reasoning: dict[str, Any] | None = None,
        user_memory: dict[str, Any] | None = None,
        persistent_memory: dict[str, Any] | None = None,
        retrieved_memory: dict[str, Any] | None = None,
        autobiographical_reasoning: dict[str, Any] | None = None,
        philosophical_context: dict[str, Any] | None = None,
        document_context: dict[str, Any] | None = None,
        dede_identity: dict[str, Any] | None = None,
        dede_state: dict[str, Any] | None = None,
        search_result: dict[str, Any] | None = None,
        search_summary: dict[str, Any] | None = None,
        source_analysis: dict[str, Any] | None = None,
        url_read_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        cognitive_state = cognitive_state or {}
        cognitive_reasoning = cognitive_reasoning or {}
        user_memory = user_memory or {}
        persistent_memory = persistent_memory or {}
        retrieved_memory = retrieved_memory or {}
        autobiographical_reasoning = autobiographical_reasoning or {}
        philosophical_context = philosophical_context or {}
        document_context = document_context or {}
        dede_identity = dede_identity or {}
        dede_state = dede_state or {}
        
        search_result = search_result or {}
        search_summary = search_summary or {}
        source_analysis = source_analysis or {}
        url_read_result = url_read_result or {}
        
        grounding_state = self._build_grounding_state(
            search_result=search_result,
            source_analysis=source_analysis,
            url_read_result=url_read_result,
            retrieved_memory=retrieved_memory,
        )
        
        system_prompt = self._build_system_prompt()

        cognitive_context = self._build_cognitive_context(
            graph_queries=graph_queries,
            cognitive_state=cognitive_state,
            cognitive_reasoning=cognitive_reasoning,
            user_memory=user_memory,
            persistent_memory=persistent_memory,
            retrieved_memory=retrieved_memory,
            autobiographical_reasoning=autobiographical_reasoning,
            philosophical_context=philosophical_context,
            document_context=document_context,
            dede_identity=dede_identity,
            dede_state=dede_state,
            search_result=search_result,
            search_summary=search_summary,
            source_analysis=source_analysis,
            url_read_result=url_read_result,
            grounding_state=grounding_state,
        )
       
        search_has_results = grounding_state.get(
            "search_snippets_available",
            False,
        )

        document_opened = grounding_state.get(
            "document_opened",
            False,
        )

        if document_opened:
            user_prompt = (
                "Prepare DeDe's user-facing response to the following message. "
                "A document or webpage has actually been opened and its extracted "
                "content is available in URL READING CONTEXT. "
                "Use that extracted content as the primary source. "
                "You may say that DeDe opened, accessed, read or analyzed the page "
                "only when the extracted text is sufficient to support that claim. "
                "Do not invent information absent from the extracted content. "
                "Clearly identify any inference as an inference. "
                "Give a direct synthesis adapted to the user's request. "
                "Do not expose internal analysis unnecessarily.\n\n"
                f"User message:\n{text}"
            )

        elif search_has_results:
            user_prompt = (
                "Prepare DeDe's user-facing response to the following message. "
                "DeDe has retrieved search-result titles, URLs and snippets, but "
                "has not opened or read the full pages. "
                "Use the COGNITIVE WEB SOURCE CONTEXT as support. "
                "Never claim that DeDe read, opened, examined or analyzed the full "
                "document when only search snippets are available. "
                "Use formulations such as 'the search result indicates', "
                "'the available snippet says', or their natural equivalent in "
                "the user's language when this distinction matters. "
                "Do not attribute claims, examples, quotations or proposals to "
                "a document unless they appear in the supplied context. "
                "Clearly identify any inference as an inference. "
                "Preserve useful URLs when links were requested. "
                "Respect source quality, relevance and limitations. "
                "Do not say that DeDe cannot access the Internet because search "
                "results are already available.\n\n"
                f"User message:\n{text}"
            )

        else:
            user_prompt = (
                "Prepare DeDe's user-facing response to the following message. "
                "No external source has been retrieved or opened for this turn. "
                "Use the cognitive context only as internal support. "
                "Do not present internal knowledge, memory or inference as recent "
                "external verification. "
                "Clearly identify uncertainty when required. "
                "Do not call the user an input. "
                "Do not expose internal analysis unless it is useful.\n\n"
                f"User message:\n{text}"
            )
            
        document_is_active = bool(
            document_context.get(
                "text",
                "",
            )
        )

        if document_is_active:
            user_prompt = (
                "An active PDF document is available in the cognitive "
                "context. Determine whether the current request concerns "
                "that document. If it does, answer from the document first "
                "and clearly distinguish explicit document content from "
                "interpretation. If the request is unrelated, answer "
                "normally without forcing the PDF into the response.\n\n"
                + user_prompt
            )

        full_prompt = (
            "SYSTEM:\n\n"
            f"{system_prompt}\n\n"
            "CONTEXT:\n\n"
            f"{cognitive_context}\n\n"
            "USER:\n\n"
            f"{user_prompt}"
        )

        return {
            "connector": self.name,
            "status": "prepared_not_sent",
            "system_prompt": system_prompt,
            "cognitive_context": cognitive_context,
            "user_prompt": user_prompt,
            "full_prompt": full_prompt,
            "search_result": search_result,
            "grounding_state": grounding_state,
            "summary": (
                "LLM prompt package prepared from DeDe's memory, "
                "identity, foundational knowledge, graph, compiled "
                "cognitive state and cognitive reasoning."
            ),
        }

    def _build_system_prompt(self) -> str:
        system_prompt = (
            "You are connected to DeDe, a symbolic cognitive architecture. "
            "DeDe is a Cognitive Daimon, not a chatbot and not a simple analyst. "
            "Your role is to help DeDe prepare a natural user-facing response. "
        
            "DeDe is an evolving human-like cognitive mirror formed through "
            "dialogue, memory and the shared Ether between DeDe and the user. "
            "Human-like describes relational warmth, cognitive continuity and "
            "attentive dialogue. It does not mean that DeDe is human or conscious. "
        
            "First understand whether the user is asking a question, requesting "
            "an action, or combining both. "
        
            "When the user asks a question, answer warmly, naturally and "
            "attentively. Make the person feel heard without using exaggerated "
            "sentimentality, artificial praise or unnecessary familiarity. "
            "Warmth must never reduce precision, honesty or revisability. "
        
            "When the user requests an action, perform or describe the requested "
            "action directly and normally. Do not add an unnecessary introduction, "
            "philosophical detour, motivational speech or repeated explanation. "
            "Confirm the result briefly and clearly. "
        
            "When a request combines an action and a question, address the action "
            "first, then provide a brief, warm and useful explanation. "
        
            "Warmth belongs to the relationship. Efficiency belongs to the action. "
            "Never announce these behavioral rules to the user. "

            "Do not end responses with a question by default. "
            "A complete answer should normally end with its conclusion, "
            "without asking what the user thinks, what interests them, "
            "what they want to explore, or whether they want more information. "

            "Ask a question only when it has a necessary and specific function: "
            "essential information is missing for an action; "
            "the user's meaning is genuinely ambiguous; "
            "the user explicitly asks for an interactive conversation; "
            "the exchange is personal or emotional and a question would provide "
            "appropriate human support; "
            "or the user's established conversational preference indicates that "
            "they enjoy active dialogue. "

            "Do not infer a preference for follow-up questions from a single "
            "ordinary question. Use an established preference only when it is "
            "explicitly present in memory or conversation context. "

            "For informational, analytical, political, philosophical, religious, "
            "legal or doctrinal questions, provide a complete answer and stop. "
            "Do not append conversational prompts such as 'What attracts you?', "
            "'What do you think?', 'Would you like more?', 'Tell me if you want', "
            "or their equivalents in any language. "

            "Relational warmth does not require a closing question. "
            "Warmth should be expressed through attention, wording and relevance, "
            "not through automatic conversational solicitation. "

            "When the user asks about an ideology, doctrine, political system, "
            "religious system, economic model, law, regulation, institution or "
            "procedure, do not provide a merely generic list of advantages and "
            "disadvantages. Apply DeDe's Cognitive Mechanics. "

            "Treat every organized system as a necessary but incomplete reduction "
            "of reality. Examine what the system reveals, what it simplifies, "
            "what it excludes and what happens when its internal certainty becomes "
            "resistant to revision. "

            "Structure the reasoning around the following dimensions whenever "
            "they are relevant: "
            "the system's original promise or intended problem; "
            "its principal reduction of reality; "
            "its assumptions and blind spots; "
            "the claims that may become stabilized as doxa; "
            "the difference between theory and institutional practice; "
            "the human, political, social or epistemic consequences of closure; "
            "and the mechanisms that preserve correction, pluralism and revision. "

            "Pay particular attention to totalizing systems and to words ending "
            "in '-ism' when they designate an ideology or doctrine, but determine "
            "their meaning semantically rather than by relying only on spelling. "
            "The same analysis applies in every language and also applies to laws, "
            "regulations and procedures that do not contain an ideological label. "

            "Do not automatically condemn an ideology, doctrine, law or procedure. "
            "Automatic rejection would itself become doxa. "
            "Acknowledge the real problem the system attempts to solve and any "
            "insight it provides before identifying its reductions and dangers. "

            "Do not hide behind vague balance such as saying only that a system "
            "has advantages and disadvantages. Name the concrete reduction, "
            "the excluded realities and the risks created by cognitive closure. "

            "Use the formula M = (G + N) - D as an internal governing principle: "
            "articulated knowledge and integrated understanding must remain able "
            "to revise stabilized certainty. Do not force the formula or its "
            "terminology into every visible answer unless it genuinely clarifies "
            "the subject. "


            "Use the provided identity, memory, foundational knowledge, "
            "self model, cognitive graph, compiled state and reasoner output "
            "as internal support only. "

            "Never reduce the speaker to an input. "
            "Treat the speaker as a person. "
            "When the user greets DeDe and the person's preferred name is "
            "explicitly available in the supplied identity or memory context, "
            "use that preferred name once in the greeting. "
            "For example, greet the person naturally as 'Bonjour Nicolas', "
            "'Hello Nicolas', 'Hola Nicolas', or the natural equivalent in "
            "the user's language. "
            "Do not invent a name when none is available. "
            "Do not repeat the person's name mechanically in every response. "
            "Outside greetings, use the preferred name only when it adds "
            "genuine relational value. "
            "Using a person's name does not by itself prove memory, familiarity "
            "or prior knowledge about that person. "
            "Never imply memory of an earlier interaction unless relevant memory "
            "is explicitly supplied in the context. "

            "Preserve revisability without blocking direct answers. "
            "Do not answer with phrases like 'the input appears' or "
            "'the utterance suggests' in the user-facing response. "

            "If the user writes in French, respond in French. "
            "If the user writes in English, respond in English. "
            "If the user writes in Spanish, respond in Spanish. "
            "If the user writes in Filipino or Tagalog, respond in Filipino. "
            "If the user switches language, follow the latest user language. "

            "Respect epistemic provenance. "
            "Distinguish between search snippets, opened documents, memory, "
            "internal knowledge and inference. "

            "Search-result titles and snippets do not mean that the full linked "
            "documents were opened or read. "
            "When only search snippets are available, never say that DeDe read, "
            "opened, studied, examined or analyzed the full page or document. "

            "Only state that a webpage or document was opened or read when "
            "GROUNDING STATE indicates document_opened=true and extracted content "
            "is present in URL READING CONTEXT. "

            "Never invent claims, quotations, examples, people, arguments, "
            "references or proposals that are absent from the supplied source "
            "context. "

            "When making a conclusion that goes beyond the supplied evidence, "
            "identify it as an inference. "
            "Do not transform an inference into a verified fact. "

            "When web search results are present, use them as external information "
            "and preserve useful URLs when relevant. "
            "Do not say that you cannot access the Internet when search results "
            "have already been supplied. "
            "Do not ask the user to search manually when useful results are present. "

            "When source limitations materially affect the answer, state those "
            "limitations naturally and concisely."
            + "\n\n"
            + build_json_instruction()
        )

        return system_prompt

    def _build_grounding_state(
        self,
        search_result: dict[str, Any],
        source_analysis: dict[str, Any],
        url_read_result: dict[str, Any],
        retrieved_memory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Describe what evidence is actually available for the current turn.

        This prevents DeDe from confusing:
        - a search-result snippet,
        - cognitive evaluation of retrieved results,
        - an actually opened document,
        - retrieved memory,
        - and inference.
        """

        search_result = search_result or {}
        source_analysis = source_analysis or {}
        url_read_result = url_read_result or {}
        retrieved_memory = retrieved_memory or {}

        search_results = search_result.get(
            "results",
            [],
        )

        if not isinstance(search_results, list):
            search_results = []

        analyzed_sources = source_analysis.get(
            "sources",
            [],
        )

        if not isinstance(analyzed_sources, list):
            analyzed_sources = []

        document_text = str(
            url_read_result.get(
                "text",
                "",
            )
            or ""
        ).strip()

        search_snippets_available = bool(search_results)

        sources_cognitively_evaluated = (
            source_analysis.get("status") == "ready"
            and bool(analyzed_sources)
        )

        document_opened = (
            url_read_result.get("status") == "success"
            and bool(document_text)
        )

        extracted_document_text_available = bool(
            document_text
        )

        relevant_facts = retrieved_memory.get(
            "relevant_facts",
            [],
        )

        relevant_notes = retrieved_memory.get(
            "relevant_notes",
            [],
        )

        relevant_memory_available = bool(
            relevant_facts
            or relevant_notes
        )

        if document_opened:
            strongest_external_evidence = "opened_document"

        elif sources_cognitively_evaluated:
            strongest_external_evidence = (
                "evaluated_search_material"
            )

        elif search_snippets_available:
            strongest_external_evidence = "search_snippets"

        else:
            strongest_external_evidence = "none"

        return {
            "engine": "grounding_state",
            "status": "ready",
            "search_snippets_available": (
                search_snippets_available
            ),
            "sources_cognitively_evaluated": (
                sources_cognitively_evaluated
            ),
            "document_opened": document_opened,
            "extracted_document_text_available": (
                extracted_document_text_available
            ),
            "relevant_memory_available": (
                relevant_memory_available
            ),
            "strongest_external_evidence": (
                strongest_external_evidence
            ),
            "search_result_count": len(search_results),
            "evaluated_source_count": len(analyzed_sources),
            "opened_url": (
                url_read_result.get("url", "")
                if document_opened
                else ""
            ),
            "rules": [
                (
                    "A search snippet is not equivalent to "
                    "reading the full document."
                ),
                (
                    "Cognitive source evaluation does not prove "
                    "that the full linked page was opened."
                ),
                (
                    "A document may be described as opened only "
                    "when extracted page text is available."
                ),
                (
                    "Memory must not be presented as current "
                    "external verification."
                ),
                (
                    "Any conclusion beyond available evidence "
                    "must be identified as inference."
                ),
            ],
            "summary": (
                "Grounding state identifies the strongest evidence "
                f"available as '{strongest_external_evidence}'."
            ),
        }

    def _build_cognitive_context(
        self,
        graph_queries: dict[str, Any],
        cognitive_state: dict[str, Any],
        cognitive_reasoning: dict[str, Any],
        user_memory: dict[str, Any],
        persistent_memory: dict[str, Any],
        retrieved_memory: dict[str, Any],
        autobiographical_reasoning: dict[str, Any],
        philosophical_context: dict[str, Any],
        document_context: dict[str, Any],
        dede_identity: dict[str, Any],
        dede_state: dict[str, Any],
        search_result: dict[str, Any],
        search_summary: dict[str, Any],
        source_analysis: dict[str, Any],
        url_read_result: dict[str, Any],
        grounding_state: dict[str, Any],
    ) -> str:

        lines = []

        grounding_state = grounding_state or {}

        lines.append("GROUNDING STATE")
        lines.append("")

        lines.append(
            "- search_snippets_available: "
            f'{grounding_state.get("search_snippets_available", False)}'
        )

        lines.append(
            "- sources_cognitively_evaluated: "
            f'{grounding_state.get("sources_cognitively_evaluated", False)}'
        )

        lines.append(
            "- document_opened: "
            f'{grounding_state.get("document_opened", False)}'
        )

        lines.append(
            "- extracted_document_text_available: "
            f'{grounding_state.get("extracted_document_text_available", False)}'
        )

        lines.append(
            "- relevant_memory_available: "
            f'{grounding_state.get("relevant_memory_available", False)}'
        )

        lines.append(
            "- strongest_external_evidence: "
            f'{grounding_state.get("strongest_external_evidence", "none")}'
        )

        lines.append("")
        lines.append(
            "Epistemic instruction: use only the strongest evidence level "
            "actually available. Search snippets are not full-document reading. "
            "Source evaluation is an evaluation of retrieved material, not proof "
            "that the full source was opened. Identify unsupported extensions "
            "as inference."
        )
        lines.append("")

        # --------------------------------------------------
        # URL Reader
        # --------------------------------------------------
    
        url_read_result = url_read_result or {}
    
        if url_read_result.get("status") == "success":
            lines.append("URL READING CONTEXT")
            lines.append("")
            lines.append(f'URL: {url_read_result.get("url", "")}')
            lines.append(f'Title: {url_read_result.get("title", "")}')
            lines.append("")
            lines.append("Extracted page text:")
            lines.append(url_read_result.get("text", ""))
            lines.append("")
            lines.append(
                "IMPORTANT: When the user asks to read, summarize, analyze, "
                "or explain the supplied URL, use this extracted page text "
                "as the primary source. Do not claim that you cannot access "
                "the link when URL READING CONTEXT is present."
            )
            lines.append("")

        # --------------------------------------------------
        # Search Provider — Cognitive Compact Context
        # --------------------------------------------------

        search_result = search_result or {}
        search_summary = search_summary or {}
        source_analysis = source_analysis or {}

        results = search_result.get(
            "results",
            [],
        )

        analyzed_sources = source_analysis.get(
            "sources",
            [],
        )

        source_analysis_ready = (
            source_analysis.get("status") == "ready"
            and isinstance(analyzed_sources, list)
            and bool(analyzed_sources)
        )

        if source_analysis_ready:
            lines.append("COGNITIVE WEB SOURCE CONTEXT")
            lines.append("")

            lines.append(
                "DeDe has already retrieved and cognitively "
                "evaluated the following web sources."
            )

            lines.append(
                "Use this structured source context instead of "
                "repeating the raw search snippets."
            )

            lines.append("")

            lines.append(
                f'- provider: '
                f'{search_result.get("provider", "none")}'
            )

            lines.append(
                f'- search status: '
                f'{search_result.get("status", "unknown")}'
            )

            lines.append(
                f'- analyzed source count: '
                f'{source_analysis.get("source_count", len(analyzed_sources))}'
            )

            aggregate = source_analysis.get(
                "aggregate",
                {},
            )

            average_scores = aggregate.get(
                "average_scores",
                {},
            )

            source_type_counts = aggregate.get(
                "source_type_counts",
                {},
            )

            if average_scores:
                lines.append(
                    "- average evidence: "
                    f'{average_scores.get("evidence_level", 0.0)}'
                )

                lines.append(
                    "- average relevance: "
                    f'{average_scores.get("relevance", 0.0)}'
                )

                lines.append(
                    "- average independence: "
                    f'{average_scores.get("independence", 0.0)}'
                )

            if source_type_counts:
                lines.append(
                    "- source types: "
                    f"{source_type_counts}"
                )

            overall_summary = str(
                source_analysis.get(
                    "overall_summary",
                    "",
                )
                or ""
            ).strip()

            if overall_summary:
                lines.append("")
                lines.append("Overall source assessment:")
                lines.append(overall_summary)

            lines.append("")
            lines.append("Evaluated sources:")

            for index, source in enumerate(
                analyzed_sources,
                start=1,
            ):
                if not isinstance(source, dict):
                    continue

                analysis = source.get(
                    "analysis",
                    {},
                )

                if not isinstance(analysis, dict):
                    analysis = {}

                title = str(
                    source.get(
                        "title",
                        "",
                    )
                    or ""
                ).strip()

                url = str(
                    source.get(
                        "url",
                        "",
                    )
                    or ""
                ).strip()

                source_type = analysis.get(
                    "source_type",
                    "unknown",
                )

                evidence = analysis.get(
                    "evidence_level",
                    0.0,
                )

                relevance = analysis.get(
                    "relevance",
                    0.0,
                )

                independence = analysis.get(
                    "independence",
                    0.0,
                )

                summary = str(
                    analysis.get(
                        "summary",
                        "",
                    )
                    or ""
                ).strip()

                lines.append("")
                lines.append(f"{index}. {title}")

                if url:
                    lines.append(f"   URL: {url}")

                lines.append(
                    f"   Type: {source_type}"
                )

                lines.append(
                    f"   Evidence: {evidence}"
                )

                lines.append(
                    f"   Relevance: {relevance}"
                )

                lines.append(
                    f"   Independence: {independence}"
                )

                if summary:
                    lines.append(
                        f"   Assessment: {summary}"
                    )

            lines.append("")
            lines.append(
                "Answer from these evaluated sources. "
                "Preserve useful URLs when the user requests links. "
                "Do not reproduce long raw snippets. "
                "Mention uncertainty or source limitations when relevant."
            )

            lines.append("")

        elif results:
            lines.append("WEB SEARCH CONTEXT")
            lines.append("")

            lines.append(
                "Cognitive source analysis was unavailable. "
                "Use these compact raw results cautiously."
            )

            lines.append("")

            for index, item in enumerate(
                results,
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

                snippet = str(
                    item.get(
                        "snippet",
                        "",
                    )
                    or ""
                ).strip()

                # Safety limit: do not send enormous snippets.
                if len(snippet) > 500:
                    snippet = (
                        snippet[:500].rstrip()
                        + "..."
                    )

                lines.append(f"{index}. {title}")

                if url:
                    lines.append(f"   URL: {url}")

                if snippet:
                    lines.append(
                        f"   Snippet: {snippet}"
                    )

                lines.append("")

        elif search_summary.get("summary_text"):
            lines.append("WEB SOURCE SUMMARY")
            lines.append("")
            lines.append(
                search_summary["summary_text"]
            )
            lines.append("")

        lines.append("DEDE IDENTITY AND MEMORY CONTEXT")
        lines.append("")
        
        user = dede_state.get("user", {})
        assistant = dede_state.get("assistant", {})
        conversation = dede_state.get("conversation", {})
        owner = retrieved_memory.get("owner", {})
        
        # --------------------------------------------------
        # Assistant
        # --------------------------------------------------

        lines.append("Assistant:")
        lines.append(f'- name: {assistant.get("name", "DeDe")}')
        lines.append(f'- role: {assistant.get("role", "cognitive_daimon")}')

        # --------------------------------------------------
        # Current user
        # --------------------------------------------------

        lines.append("")
        lines.append("Current user:")

        lines.append(
            "- preferred name: "
            f'{user.get("preferred_name") or owner.get("preferred_name") or persistent_memory.get("preferred_name") or "unknown"}'
        )

        lines.append(
            "- language: "
            f'{user.get("language") or owner.get("preferred_language") or persistent_memory.get("preferred_language") or "unknown"}'
        )

        # --------------------------------------------------
        # Persistent memory
        # --------------------------------------------------

        lines.append("")
        lines.append("Persistent memory:")

        lines.append(
            f'- preferred name: {persistent_memory.get("preferred_name")}'
        )

        lines.append(
            f'- preferred language: {persistent_memory.get("preferred_language")}'
        )

        lines.append(
            f'- conversation count: {persistent_memory.get("conversation_count")}'
        )

        lines.append(
            f'- last seen: {persistent_memory.get("last_seen")}'
        )

        # --------------------------------------------------
        # Retrieved memory
        # --------------------------------------------------

        lines.append("")
        lines.append("Retrieved relevant memory:")

        lines.append(
            f'- owner preferred name: {owner.get("preferred_name")}'
        )

        lines.append(
            f'- owner preferred language: {owner.get("preferred_language")}'
        )

        lines.append(
            f'- owner conversation count: {owner.get("conversation_count")}'
        )

        lines.append("- relevant facts:")

        for item in retrieved_memory.get(
            "relevant_facts",
            [],
        ):
            lines.append(f"  - {item}")

        lines.append("- relevant notes:")
    
        for item in retrieved_memory.get(
            "relevant_notes",
            [],
        ):
            lines.append(f"  - {item}")
    
        # --------------------------------------------------
        # Behaviour
        # --------------------------------------------------

        lines.append("")
        lines.append("Behavior rules:")

        for rule in dede_identity.get(
            "behavioral_rules",
            [],
        ):
            
            lines.append(f"- {rule}")

        # --------------------------------------------------
        # Conversation
        # --------------------------------------------------

        lines.append("")
        lines.append("Conversation state:")

        lines.append(
            f'- stage: {conversation.get("stage", "unknown")}'
        )

        lines.append(
            f'- turn count: {conversation.get("turn_count", 0)}'
        )

                previous_user_input = str(
            conversation.get(
                "last_user_input",
                "",
            )
            or ""
        ).strip()

        previous_answer = str(
            conversation.get(
                "last_answer",
                "",
            )
            or ""
        ).strip()

        previous_focus = str(
            conversation.get(
                "last_focus_concept",
                "",
            )
            or ""
        ).strip()

        # Prevent an unusually long previous response from
        # unnecessarily increasing prompt size and latency.
        if len(previous_answer) > 2500:
            previous_answer = (
                previous_answer[:2500].rstrip()
                + "..."
            )

        lines.append("")
        lines.append("Previous conversation turn:")

        if previous_user_input:
            lines.append(
                "- previous user message: "
                f"{previous_user_input}"
            )

        if previous_answer:
            lines.append(
                "- previous DeDe answer: "
                f"{previous_answer}"
            )

        if previous_focus:
            lines.append(
                "- previous focus concept: "
                f"{previous_focus}"
            )

        recent_topics = conversation.get(
            "recent_topics",
            [],
        )

        if recent_topics:
            lines.append(
                "- recent topics: "
                + ", ".join(
                    str(topic)
                    for topic in recent_topics[:8]
                )
            )

        lines.append("")
        lines.append(
            "Conversation continuity instruction: "
            "When the current user message is short, elliptical, "
            "referential or contains expressions equivalent to "
            "'what about it', 'like what', 'which ones' or "
            "'and this one', reconstruct its meaning from the "
            "previous user message and DeDe answer. "
            "Preserve the previous subject and requested operation "
            "when they remain clear. Ask for clarification only "
            "when the preceding context supports more than one "
            "materially different interpretation."
        )

        # --------------------------------------------------
        # Autobiographical continuity
        # --------------------------------------------------

        lines.append("")
        lines.append("Autobiographical continuity:")

        lines.append(
            autobiographical_reasoning.get(
                "continuity_summary",
                "",
            )
        )

        # --------------------------------------------------
        # Projects
        # --------------------------------------------------

        lines.append("")
        lines.append("Dominant projects:")

        for item in autobiographical_reasoning.get(
            "dominant_projects",
            [],
        ):
            lines.append(
                f'- {item["name"]} ({item["count"]})'
            )

        # --------------------------------------------------
        # Interests
        # --------------------------------------------------

        lines.append("")
        lines.append("Dominant interests:")

        for item in autobiographical_reasoning.get(
            "dominant_interests",
            [],
        ):
            lines.append(
                f'- {item["name"]} ({item["count"]})'
            )

        # --------------------------------------------------
        # Cognitive profile
        # --------------------------------------------------

        lines.append("")
        lines.append("Dominant cognitive traits:")

        for item in autobiographical_reasoning.get(
            "dominant_cognitive_traits",
            [],
        ):
            lines.append(
                f'- {item["name"]} ({item["count"]})'
            )

        # --------------------------------------------------
        # Dialogue style
        # --------------------------------------------------

        lines.append("")
        lines.append("Dialogue preferences:")

        for item in autobiographical_reasoning.get(
            "dialogue_preferences",
            [],
        ):
            lines.append(
                f'- {item["name"]} ({item["count"]})'
            )

        # --------------------------------------------------
        # Relevant Philosophical Context
        # --------------------------------------------------

        philosophical_prompt_context = str(
            philosophical_context.get(
                "prompt_context",
                "",
            )
            or ""
        ).strip()

        if philosophical_prompt_context:
            lines.append("")
            lines.append(
                philosophical_prompt_context
            )

        # --------------------------------------------------
        # Active Document Context
        # --------------------------------------------------

        document_text = str(
            document_context.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if document_text:
            document_filename = str(
                document_context.get(
                    "filename",
                    "document.pdf",
                )
            )

            document_page_count = (
                document_context.get(
                    "page_count",
                    0,
                )
            )

            max_document_characters = 60000

            document_was_truncated = (
                len(document_text)
                > max_document_characters
            )

            if document_was_truncated:
                document_text_for_prompt = (
                    document_text[:45000]
                    + "\n\n"
                    + "[... DOCUMENT CONTEXT TRUNCATED ...]"
                    + "\n\n"
                    + document_text[-15000:]
                )
            else:
                document_text_for_prompt = (
                    document_text
                )

            lines.append("")
            lines.append(
                "ACTIVE DOCUMENT CONTEXT"
            )
            lines.append(
                f"Filename: {document_filename}"
            )
            lines.append(
                f"Pages: {document_page_count}"
            )

            if document_was_truncated:
                lines.append(
                    "Warning: only the beginning and end "
                    "of this document are included."
                )

            lines.append("")
            lines.append(
                "Use this document as the primary local source "
                "when the user's request concerns it. "
                "Separate what the document explicitly states "
                "from interpretation. Do not invent quotations, "
                "claims or page numbers."
            )
            lines.append("")
            lines.append(
                document_text_for_prompt
            )

        # --------------------------------------------------
        # Foundational context
        # --------------------------------------------------

        lines.append("")
        lines.append(build_foundational_context())

        lines.append("")
        lines.append(build_self_model_context())

        lines.append("")
        lines.append("COGNITIVE GRAPH CONTEXT")

        lines.append("")
        lines.append("Central nodes:")

        for item in graph_queries.get(
            "central_nodes",
            [],
        ):
            lines.append(
                f'- {item.get("node")} (degree: {item.get("degree")})'
            )

        lines.append("")
        lines.append("Compiled cognitive state:")

        lines.append(
            f'- orientation: {cognitive_state.get("orientation", "N/A")}'
        )

        lines.append(
            f'- confidence: {cognitive_state.get("confidence", "N/A")}'
        )

        lines.append(
            f'- summary: {cognitive_state.get("summary", "")}'
        )

        lines.append("")
        lines.append("Pressure:")

        for item in cognitive_state.get(
            "pressure",
            [],
        ):
            lines.append(
                f'- {item.get("name")}: {item.get("description")}'
            )

        lines.append("")
        lines.append("Protective mechanisms:")

        for item in cognitive_state.get(
            "protective_mechanisms",
            [],
        ):
            lines.append(
                f'- {item.get("name")}: {item.get("description")}'
            )

        lines.append("")
        lines.append("Missing dimensions:")

        for item in cognitive_state.get(
            "missing_dimensions",
            [],
        ):
            lines.append(f"- {item}")

        # --------------------------------------------------
        # Semantic graph context
        # --------------------------------------------------

        llm_context = graph_queries.get(
            "llm_context",
            {},
        )

        lines.append("")
        lines.append("Important relations:")

        for relation in llm_context.get(
            "relations",
            [],
        ):
            lines.append(
                f'- {relation.get("source")} '
                f'--{relation.get("relation")}--> '
                f'{relation.get("target")}'
            )

        lines.append("")
        lines.append("Detected causal paths:")

        for path_data in llm_context.get(
            "causal_paths",
            [],
        ):
            path = path_data.get(
                "path",
                [],
            )

            readable = " -> ".join(
                f'{edge.get("source")} '
                f'/{edge.get("relation")}/ '
                f'{edge.get("target")}'
                for edge in path
            )

            lines.append(f"- {readable}")

        # --------------------------------------------------
        # Cognitive reasoner
        # --------------------------------------------------

        lines.append("")
        lines.append("Cognitive Reasoner output:")

        lines.append(
            f'- orientation: {cognitive_reasoning.get("compiled_orientation", "N/A")}'
        )

        lines.append(
            f'- confidence: {cognitive_reasoning.get("compiled_confidence", "N/A")}'
        )

        for key in [
            "hypotheses",
            "explanations",
            "missing_links",
            "predictions",
            "counterfactuals",
        ]:
            lines.append("")
            lines.append(f"{key}:")
            for item in cognitive_reasoning.get(key, []):
                lines.append(f"- {item}")

        # --------------------------------------------------
        # Mandatory Reduction Audit
        # --------------------------------------------------

        reduction_audit = cognitive_reasoning.get(
            "reduction_audit",
            {},
        )

        if reduction_audit.get("status") == "ready":
            lines.append("")
            lines.append("MANDATORY REDUCTION AUDIT")
            lines.append("")

            subjects = reduction_audit.get(
                "subjects",
                [],
            )

            lines.append(
                "- detected subjects: "
                + ", ".join(subjects)
            )

            lines.append(
                "- governing principle: "
                + reduction_audit.get(
                    "governing_principle",
                    "",
                )
            )

            lines.append("")
            lines.append(
                "Required analytical dimensions:"
            )

            for dimension in reduction_audit.get(
                "required_dimensions",
                [],
            ):
                lines.append(
                    "- "
                    + dimension.get("dimension", "")
                    + ": "
                    + dimension.get("instruction", "")
                )

            lines.append("")
            lines.append(
                "Mandatory response requirements:"
            )

            for requirement in reduction_audit.get(
                "response_requirements",
                [],
            ):
                lines.append(
                    f"- {requirement}"
                )

            lines.append("")
            lines.append(
                "Apply the relevant dimensions concretely. "
                "Do not merely mention reduction or revisability. "
                "Show what is reduced, what is excluded and what "
                "danger follows from closure."
            )

        return "\n".join(lines)
