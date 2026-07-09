"""
DeDe - Cognitive Governor

Controls epistemic provenance before the LLM answers.

It prevents DeDe from claiming that a web search was performed
when no usable search result exists.
"""

from typing import Any


class CognitiveGovernor:
    name = "cognitive_governor"

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

        search_results = search_result.get("results", [])

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

        full_prompt = llm_package.get("full_prompt", "")

        governed_prompt = (
            full_prompt
            + "\n\n"
            + "COGNITIVE GOVERNOR RULES:\n\n"
            + provenance_rules
        )

        llm_package["full_prompt"] = governed_prompt
        llm_package["cognitive_governor"] = {
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
        lines.append("- information retrieved from web search;")
        lines.append("- information retrieved from memory;")
        lines.append("- general internal knowledge;")
        lines.append("- hypothesis or reconstruction.")
        lines.append("")

        if search_performed and search_relevant:
            lines.append(
                "A web search was performed and relevant results are available."
            )
            lines.append(
                "You may say: 'D'après les résultats trouvés...' "
                "or 'Selon les liens fournis...'."
            )
            lines.append(
                "When useful, include the supplied URLs."
            )
        else:
            lines.append(
                "No relevant web search result is available."
            )
            lines.append(
                "You must NOT say or imply that DeDe searched the web."
            )
            lines.append(
                "Forbidden formulations include:"
            )
            lines.append("- 'd'après les recherches effectuées';")
            lines.append("- 'selon les résultats trouvés';")
            lines.append("- 'j'ai trouvé plusieurs liens';")
            lines.append("- 'voici les sources trouvées';")
            lines.append("- 'after searching';")
            lines.append("- 'based on search results'.")
            lines.append(
                "If the user explicitly asked for links or a search, "
                "and no relevant search result is available, say clearly "
                "that no verified search result is available in the current context."
            )

        lines.append("")

        if memory_available:
            lines.append(
                "Relevant memory is available. Use it carefully, but do not "
                "present memory as external verification."
            )
        else:
            lines.append(
                "No relevant memory is available. Do not invent personal or "
                "biographical details."
            )

        lines.append("")
        lines.append(
            "If the user asks about a specific person, author, publication, "
            "social profile, Medium page, letter, article, or public presence, "
            "do not fabricate biography, links, titles or credentials."
        )
        lines.append(
            "If evidence is missing, answer with epistemic caution."
        )
        lines.append(
            "Prefer: 'Je n'ai pas assez d'éléments vérifiés pour l'affirmer.'"
        )

        return "\n".join(lines)
