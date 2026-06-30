"""
DeDe - LLM Connector

Prepares structured prompts for future LLM integration.

This connector does not call an external LLM yet.
It transforms DeDe's cognitive graph context into a clean prompt package.
"""

from typing import Any


class LLMConnector:
    """
    Builds LLM-ready cognitive prompts from graph query outputs.
    """

    name = "llm_connector"

    def build_prompt_package(
        self,
        text: str,
        graph_queries: dict[str, Any],
    ) -> dict[str, Any]:
        llm_context = graph_queries.get("llm_context", {})
        central_nodes = graph_queries.get("central_nodes", [])
        key_paths = graph_queries.get("key_paths", {})

        system_prompt = self._build_system_prompt()
        cognitive_context = self._build_cognitive_context(
            llm_context,
            central_nodes,
            key_paths,
        )
        user_prompt = self._build_user_prompt(text)

        return {
            "connector": self.name,
            "status": "prepared_not_sent",
            "system_prompt": system_prompt,
            "cognitive_context": cognitive_context,
            "user_prompt": user_prompt,
            "full_prompt": self._build_full_prompt(
                system_prompt,
                cognitive_context,
                user_prompt,
            ),
            "summary": (
                "LLM prompt package prepared from DeDe's structured "
                "cognitive graph context."
            ),
        }

    def _build_system_prompt(self) -> str:
        return (
            "You are a cognitive reasoning assistant connected to DeDe, "
            "a symbolic cognitive architecture. "
            "You must not replace DeDe's analysis. "
            "You must use the provided cognitive graph context to explain, "
            "clarify, question, or refine the interpretation. "
            "You should preserve revisability, identify assumptions, "
            "avoid overconfidence, and make missing dimensions explicit."
        )

    def _build_user_prompt(self, text: str) -> str:
        return (
            "Analyze the following input using the provided cognitive context:\n\n"
            f"{text}"
        )

    def _build_cognitive_context(
        self,
        llm_context: dict[str, Any],
        central_nodes: list[dict[str, Any]],
        key_paths: dict[str, Any],
    ) -> str:
        nodes = llm_context.get("nodes", [])
        relations = llm_context.get("relations", [])
        causal_paths = llm_context.get("causal_paths", [])

        lines = []

        lines.append("COGNITIVE GRAPH CONTEXT")
        lines.append("")
        lines.append("Central nodes:")

        for item in central_nodes:
            lines.append(
                f'- {item.get("node")} '
                f'(degree: {item.get("degree")})'
            )

        lines.append("")
        lines.append("Important nodes:")

        for node in nodes:
            lines.append(
                f'- {node.get("id")} '
                f'[{node.get("type")}]: {node.get("label")}'
            )

        lines.append("")
        lines.append("Important relations:")

        for relation in relations:
            lines.append(
                f'- {relation.get("source")} '
                f'--{relation.get("relation")}--> '
                f'{relation.get("target")}'
            )

        lines.append("")
        lines.append("Detected causal paths:")

        for path in causal_paths:
            readable = " -> ".join(
                f'{step.get("source")} '
                f'/{step.get("relation")} '
                f'/ {step.get("target")}'
                for step in path.get("path", [])
            )
            lines.append(f"- {readable}")

        lines.append("")
        lines.append("Key graph paths:")

        for name, path in key_paths.items():
            if not path:
                lines.append(f"- {name}: not found")
                continue

            readable = " -> ".join(
                f'{step.get("source")} '
                f'/{step.get("relation")} '
                f'/ {step.get("target")}'
                for step in path
            )

            lines.append(f"- {name}: {readable}")

        return "\n".join(lines)

    def _build_full_prompt(
        self,
        system_prompt: str,
        cognitive_context: str,
        user_prompt: str,
    ) -> str:
        return "\n\n".join(
            [
                "SYSTEM:",
                system_prompt,
                "CONTEXT:",
                cognitive_context,
                "USER:",
                user_prompt,
            ]
        )
