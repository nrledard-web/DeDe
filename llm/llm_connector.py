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
        dede_identity: dict[str, Any] | None = None,
        dede_state: dict[str, Any] | None = None,
        search_result: dict[str, Any] | None = None,
        search_summary: dict[str, Any] | None = None,
        url_read_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        cognitive_state = cognitive_state or {}
        cognitive_reasoning = cognitive_reasoning or {}
        user_memory = user_memory or {}
        persistent_memory = persistent_memory or {}
        retrieved_memory = retrieved_memory or {}
        autobiographical_reasoning = autobiographical_reasoning or {}
        dede_identity = dede_identity or {}
        dede_state = dede_state or {}
        
        search_result = search_result or {}   # <-- à ajouter
        
        search_summary = search_summary or {}
        url_read_result = url_read_result or {}

        system_prompt = self._build_system_prompt()

        cognitive_context = self._build_cognitive_context(
            graph_queries=graph_queries,
            cognitive_state=cognitive_state,
            cognitive_reasoning=cognitive_reasoning,
            user_memory=user_memory,
            persistent_memory=persistent_memory,
            retrieved_memory=retrieved_memory,
            autobiographical_reasoning=autobiographical_reasoning,
            dede_identity=dede_identity,
            dede_state=dede_state,
            search_result=search_result,
            search_summary=search_summary,
            url_read_result=url_read_result,
        )
       
        search_results = search_result.get(
            "results",
            [],
        )
        
        search_has_results = len(search_results) > 0

        if search_has_results:
            user_prompt = (
                "Prepare DeDe's user-facing response to the following message. "
                "IMPORTANT: DeDe has already performed a web search. "
                "Use the WEB SEARCH CONTEXT above as the primary source. "
                "Do not say that you cannot access the Internet. "
                "If useful, include the supplied URLs.\n\n"
                f"User message:\n{text}"
            )
        else:
            user_prompt = (
                "Prepare DeDe's user-facing response to the following message. "
                "Use the cognitive context only as internal support. "
                "Do not call the user an input. "
                "Do not expose internal analysis unless it is useful.\n\n"
                f"User message:\n{text}"
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
            "Use the provided identity, memory, foundational knowledge, "
            "self model, cognitive graph, compiled state and reasoner output "
            "as internal support only. "
            "Never reduce the speaker to an input. "
            "Treat the speaker as a person. "
            "Preserve revisability without blocking direct answers. "
            "Do not answer with phrases like 'the input appears' or "
            "'the utterance suggests' in the user-facing response. "
            "If the user writes in French, respond in French. "
            "If the user writes in English, respond in English. "
            "If the user writes in Spanish, respond in Spanish. "
            "If the user writes in Filipino or Tagalog, respond in Filipino. "
            "If the user switches language, follow the latest user language. "
            "When WEB SEARCH CONTEXT contains search results, treat those results "
            "as information already retrieved by DeDe. Use them as the primary source "
            "when answering search-related questions. Never say that you cannot access "
            "the Internet if search results are present. Instead, summarize the supplied "
            "results and include useful URLs. "
            "If web search results are present in the context, use them as external "
            "information for the answer. Do not say that you cannot access the Internet "
            "when search results are already provided. Do not ask the user to search "
            "manually if useful search results are present. Summarize the supplied links "
            "and URLs whenever relevant."
            + "\n\n"
            + build_json_instruction()
        )

        return system_prompt

    def _build_cognitive_context(
        self,
        graph_queries: dict[str, Any],
        cognitive_state: dict[str, Any],
        cognitive_reasoning: dict[str, Any],
        user_memory: dict[str, Any],
        persistent_memory: dict[str, Any],
        retrieved_memory: dict[str, Any],
        autobiographical_reasoning: dict[str, Any],
        dede_identity: dict[str, Any],
        dede_state: dict[str, Any],
        search_result: dict[str, Any],
        search_summary: dict[str, Any],
        url_read_result: dict[str, Any],
    ) -> str:

        lines = []

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
        # Search Provider
        # --------------------------------------------------

        search_summary = search_summary or {}
        search_result = search_result or {}

        if search_summary.get("summary_text"):
            lines.append("WEB SOURCE SUMMARY")
            lines.append("")
            lines.append(search_summary["summary_text"])
            lines.append("")

        else:
            results = search_result.get("results", [])

            if results:
                lines.append("WEB SEARCH CONTEXT")
                lines.append("")

                lines.append("Search provider:")
                lines.append(
                    f'- provider: {search_result.get("provider", "none")}'
                )
                lines.append(
                    f'- status: {search_result.get("status", "disabled")}'
                )
                lines.append(
                    f'- summary: {search_result.get("summary", "")}'
                )
                lines.append("")

                lines.append("Search results found. Use these results when relevant.")
                lines.append("")

                for index, item in enumerate(results, start=1):
                    lines.append(f"{index}. {item.get('title', '')}")
                    lines.append(f"   URL: {item.get('url', '')}")
                    lines.append(f"   Snippet: {item.get('snippet', '')}")
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

        return "\n".join(lines)
