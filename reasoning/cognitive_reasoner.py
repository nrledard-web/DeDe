"""
DeDe - Cognitive Reasoner

Intermediate reasoning layer between graph queries and agents.

The Cognitive Reasoner uses:
- semantic graph structure
- graph query results
- causal paths
- key paths
- workspace context

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
    """
    Produces structured cognitive reasoning from semantic graph queries.
    """

    name = "cognitive_reasoner"

    def run(
        self,
        workspace: CognitiveWorkspace,
        graph_queries: dict[str, Any],
    ) -> dict[str, Any]:

        central_nodes = graph_queries.get("central_nodes", [])
        llm_context = graph_queries.get("llm_context", {})
        causal_paths = llm_context.get("causal_paths", [])
        key_paths = graph_queries.get("key_paths", {})

        nodes = self._extract_node_names(central_nodes)
        node_set = set(nodes)

        hypotheses = []
        contradictions = []
        explanations = []
        missing_links = []
        predictions = []
        counterfactuals = []
        inference_chains = []

        # --------------------------------------------------
        # Node-based reasoning
        # --------------------------------------------------

        if "certainty" in node_set and "understanding" in node_set:
            hypotheses.append(
                "Certainty and understanding appear structurally connected."
            )

            explanations.append(
                "The reasoning may depend on how certainty is stabilized relative to understanding."
            )

        if "revisability" in node_set and "certainty" in node_set:
            hypotheses.append(
                "Revisability may act as a regulating force against cognitive closure."
            )

            counterfactuals.append(
                "If revisability were stronger, the same belief could remain open rather than closed."
            )

        if "reduction" in node_set:
            explanations.append(
                "Reduction appears as a structural component of the reasoning frame."
            )

            missing_links.append(
                "The system should verify whether the reduction is acknowledged or forgotten."
            )

        if "mecroyance" in node_set:
            predictions.append(
                "The reasoning may contain a risk of mecroyance if certainty exceeds integrated understanding."
            )

        # --------------------------------------------------
        # Causal path reasoning
        # --------------------------------------------------

        for path_data in causal_paths:
            path = path_data.get("path", [])

            readable_path = self._format_path(path)

            if readable_path:
                inference_chains.append(readable_path)

            for edge in path:
                source = edge.get("source")
                relation = edge.get("relation")
                target = edge.get("target")

                if (
                    source == "certainty"
                    and relation == "can_increase"
                    and target == "closure"
                ):
                    explanations.append(
                        "The graph indicates that certainty may increase cognitive closure."
                    )

                    predictions.append(
                        "If certainty rises without stronger grounding or integration, closure may increase."
                    )

                if (
                    source == "closure"
                    and relation == "reduces"
                    and target == "revisability"
                ):
                    explanations.append(
                        "The graph indicates that closure reduces revisability."
                    )

                    counterfactuals.append(
                        "If closure decreases, revisability should become easier to preserve."
                    )

                if (
                    source == "reduction"
                    and relation == "can_produce"
                    and target == "closure"
                ):
                    hypotheses.append(
                        "Forgotten or unexamined reduction may contribute to cognitive closure."
                    )

                if (
                    source == "revisability"
                    and relation == "limits"
                    and target == "mecroyance"
                ):
                    explanations.append(
                        "Revisability appears as a limiting factor against mecroyance."
                    )

                if (
                    source == "cognitive_filter"
                    and relation == "shapes"
                    and target == "understanding"
                ):
                    hypotheses.append(
                        "The cognitive filter may influence how understanding is formed."
                    )

        # --------------------------------------------------
        # Key path reasoning
        # --------------------------------------------------

        if key_paths.get("certainty_to_revisability"):
            explanations.append(
                "A key path connects certainty to revisability, suggesting that certainty is not necessarily closed."
            )

        if key_paths.get("reduction_to_revisability"):
            hypotheses.append(
                "The reduction-to-revisability path suggests that reduction may affect openness through closure."
            )

        if key_paths.get("cognitive_filter_to_understanding"):
            missing_links.append(
                "The system should clarify which cognitive filters shape the current understanding."
            )

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        if not hypotheses:
            hypotheses.append(
                "No strong cognitive hypothesis detected from the current graph structure."
            )

        return {
            "status": "ready",
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
        *node_groups: list[Any],
    ) -> list[str]:
        """
        Extracts node names from graph query results.

        Supports:
        - strings
        - dictionaries such as {"node": "..."}
        - dictionaries such as {"name": "..."}
        - dictionaries such as {"id": "..."}
        - dictionaries such as {"label": "..."}
        """

        names = []

        for group in node_groups:
            for item in group:
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
        """
        Converts a graph path into a readable inference chain.
        """

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
        """
        Removes duplicates while preserving order.
        """

        seen = set()
        unique_values = []

        for value in values:
            if value not in seen:
                seen.add(value)
                unique_values.append(value)

        return unique_values
