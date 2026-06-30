"""
DeDe - Cognitive Reasoner

Interprets graph queries and compiled cognitive state.

It produces:
- hypotheses
- contradictions
- explanations
- missing links
- predictions
- counterfactuals
- inference chains
"""

from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


class CognitiveReasoner:

    name = "cognitive_reasoner"

    def run(
        self,
        workspace: CognitiveWorkspace,
        graph_queries: dict[str, Any],
        cognitive_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        cognitive_state = cognitive_state or {}

        central_nodes = graph_queries.get("central_nodes", [])
        llm_context = graph_queries.get("llm_context", {})
        causal_paths = llm_context.get("causal_paths", [])

        nodes = self._extract_node_names(central_nodes)
        node_set = set(nodes)

        orientation = cognitive_state.get("orientation", "unknown")
        state_confidence = cognitive_state.get("confidence", 0)

        hypotheses = []
        contradictions = []
        explanations = []
        missing_links = []
        predictions = []
        counterfactuals = []
        inference_chains = []

        # --------------------------------------------------
        # Cognitive-state based reasoning
        # --------------------------------------------------

        if orientation == "pressure_dominant":
            hypotheses.append(
                "The compiled cognitive state suggests that pressure currently dominates protective mechanisms."
            )

            predictions.append(
                "If pressure remains stronger than revisability mechanisms, cognitive closure may increase."
            )

        elif orientation == "revisability_dominant":
            hypotheses.append(
                "The compiled cognitive state suggests that revisability currently dominates pressure."
            )

            predictions.append(
                "The interpretation is likely to remain open if revisability is preserved."
            )

        elif orientation == "balanced":
            hypotheses.append(
                "The compiled cognitive state suggests a balance between pressure and protection."
            )

            counterfactuals.append(
                "A small increase in closure or reduction could shift the state toward pressure dominance."
            )

        for item in cognitive_state.get("pressure", []):
            explanations.append(item.get("description", ""))

        for item in cognitive_state.get("protective_mechanisms", []):
            explanations.append(item.get("description", ""))

        for dimension in cognitive_state.get("missing_dimensions", []):
            missing_links.append(dimension)

        # --------------------------------------------------
        # Graph fallback reasoning
        # --------------------------------------------------

        if "certainty" in node_set and "understanding" in node_set:
            hypotheses.append(
                "Certainty and understanding appear structurally connected."
            )

        if "revisability" in node_set and "certainty" in node_set:
            counterfactuals.append(
                "If revisability were stronger, the same belief could remain open rather than closed."
            )

        for path_data in causal_paths:
            readable_path = self._format_path(path_data.get("path", []))

            if readable_path:
                inference_chains.append(readable_path)

        if not hypotheses:
            hypotheses.append(
                "No strong cognitive hypothesis detected from the current structure."
            )

        return {
            "status": "ready",
            "reasoning_source": "cognitive_state_plus_graph",
            "compiled_orientation": orientation,
            "compiled_confidence": state_confidence,
            "nodes_considered": sorted(node_set),
            "hypotheses": self._unique(hypotheses),
            "contradictions": self._unique(contradictions),
            "explanations": self._unique(explanations),
            "missing_links": self._unique(missing_links),
            "predictions": self._unique(predictions),
            "counterfactuals": self._unique(counterfactuals),
            "inference_chains": self._unique(inference_chains),
        }

    def _extract_node_names(
        self,
        node_group: list[Any],
    ) -> list[str]:

        names = []

        for item in node_group:
            if isinstance(item, str):
                names.append(item)

            elif isinstance(item, dict):
                name = (
                    item.get("node")
                    or item.get("name")
                    or item.get("id")
                    or item.get("label")
                )

                if name:
                    names.append(str(name))

        return names

    def _format_path(
        self,
        path: list[dict[str, Any]],
    ) -> str:

        parts = []

        for edge in path:
            source = edge.get("source")
            relation = edge.get("relation")
            target = edge.get("target")

            if source and relation and target:
                parts.append(f"{source} / {relation} / {target}")

        return " → ".join(parts)

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:

        seen = set()
        unique_values = []

        for value in values:
            if value and value not in seen:
                seen.add(value)
                unique_values.append(value)

        return unique_values
