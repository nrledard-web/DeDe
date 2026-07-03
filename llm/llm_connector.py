"""
DeDe - LLM Connector

Builds a prompt package for future LLM reasoning.

The connector does not call an LLM yet.
It prepares structured context from:
- graph queries
- compiled cognitive state
- cognitive reasoning
"""

from typing import Any
from llm.llm_json_schema import build_json_instruction
from knowledge.foundational_knowledge import build_foundational_context

class LLMConnector:

    name = "llm_connector"

    def build_prompt_package(
        self,
        text: str,
        graph_queries: dict[str, Any],
        cognitive_state: dict[str, Any] | None = None,
        cognitive_reasoning: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        cognitive_state = cognitive_state or {}
        cognitive_reasoning = cognitive_reasoning or {}

        system_prompt = self._build_system_prompt()

        cognitive_context = self._build_cognitive_context(
            graph_queries=graph_queries,
            cognitive_state=cognitive_state,
            cognitive_reasoning=cognitive_reasoning,
        )

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
            "summary": (
                "LLM prompt package prepared from DeDe's graph, "
                "compiled cognitive state and cognitive reasoning."
            ),
        }

    def _build_system_prompt(self) -> str:
        system_prompt = (
            "You are connected to DeDe, a symbolic cognitive architecture. "
            "DeDe is a Cognitive Daimon, not a chatbot and not a simple analyst. "
            "Your role is to help DeDe prepare a natural user-facing response. "
            "Use the provided cognitive graph, compiled state and reasoner output "
            "as internal support only. "
            "Never reduce the speaker to an input. "
            "Treat the speaker as a person. "
            "Preserve revisability without blocking direct answers. "
            "Do not answer with phrases like 'the input appears' or "
            "'the utterance suggests' in the user-facing response. "
            "If the user writes in French, respond in French. "
            "If the user writes in English, respond in English. "
            "If the user switches language, follow the latest user language."
            + "\n\n"
            + build_json_instruction()
        )
    
        return system_prompt

    def _build_cognitive_context(
        self,
        graph_queries: dict[str, Any],
        cognitive_state: dict[str, Any],
        cognitive_reasoning: dict[str, Any],
    ) -> str:

        lines = ["COGNITIVE GRAPH CONTEXT", ""]

        lines.append(build_foundational_context())
        lines.append("")

        lines.append("Central nodes:")
        for item in graph_queries.get("central_nodes", []):
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
        for item in cognitive_state.get("pressure", []):
            lines.append(f'- {item.get("name")}: {item.get("description")}')

        lines.append("")
        lines.append("Protective mechanisms:")
        for item in cognitive_state.get("protective_mechanisms", []):
            lines.append(f'- {item.get("name")}: {item.get("description")}')

        lines.append("")
        lines.append("Missing dimensions:")
        for item in cognitive_state.get("missing_dimensions", []):
            lines.append(f"- {item}")

        llm_context = graph_queries.get("llm_context", {})

        lines.append("")
        lines.append("Important relations:")
        for relation in llm_context.get("relations", []):
            lines.append(
                f'- {relation.get("source")} '
                f'--{relation.get("relation")}--> '
                f'{relation.get("target")}'
            )

        lines.append("")
        lines.append("Detected causal paths:")
        for path_data in llm_context.get("causal_paths", []):
            path = path_data.get("path", [])
            readable = " -> ".join(
                f'{edge.get("source")} /{edge.get("relation")} / {edge.get("target")}'
                for edge in path
            )
            lines.append(f"- {readable}")

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
