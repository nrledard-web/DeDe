"""
DeDe - Cognitive Reasoner

Intermediate reasoning layer between graph queries and agents.

The Cognitive Reasoner uses:
- semantic graph structure
- graph query results
- workspace context

It produces:
- hypotheses
- contradictions
- explanations
- missing links
- predictions
- counterfactuals
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
        important_nodes = graph_queries.get("important_nodes", [])
        causal_paths = graph_queries.get("causal_paths", [])
        key_paths = graph_queries.get("key_paths", [])

        nodes = self._extract_node_names(
            central_nodes,
            important_nodes,
        )

        node_set = set(nodes)

        hypotheses = []
        contradictions = []
        explanations = []
        missing_links = []
        predictions = []
        counterfactuals = []

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

        if causal_paths:
            explanations.append(
                "Causal paths suggest that some concepts organize the direction of reasoning."
            )

        if key_paths:
            hypotheses.append(
                "Key semantic paths may reveal the internal architecture of the argument."
            )

        if not hypotheses:
            hypotheses.append(
                "No strong cognitive hypothesis detected from the current graph structure."
            )

        return {
            "status": "ready",
            "nodes_considered": sorted(node_set),
            "hypotheses": hypotheses,
            "contradictions": contradictions,
            "explanations": explanations,
            "missing_links": missing_links,
            "predictions": predictions,
            "counterfactuals": counterfactuals,
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
