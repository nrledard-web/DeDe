"""
DeDe - Graph Query Engine

Provides symbolic graph queries for agents and future LLM connectors.
"""

from collections import deque
from typing import Any


class GraphQueryEngine:
    name = "graph_query_engine"

    def analyze(self, graph: dict[str, Any]) -> dict[str, Any]:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        return {
            "engine": self.name,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "central_nodes": self.central_nodes(edges),
            "llm_context": self.build_llm_context(graph),
            "key_paths": {
                "certainty_to_revisability": self.find_path(
                    edges,
                    "certainty",
                    "revisability",
                ),
                "reduction_to_revisability": self.find_path(
                    edges,
                    "reduction",
                    "revisability",
                ),
                "cognitive_filter_to_understanding": self.find_path(
                    edges,
                    "cognitive_filter",
                    "understanding",
                ),
            },
        }

    def neighbors(
        self,
        edges: list[dict[str, Any]],
        node_id: str,
    ) -> list[dict[str, Any]]:
        return [
            edge
            for edge in edges
            if edge.get("source") == node_id or edge.get("target") == node_id
        ]

    def find_path(
        self,
        edges: list[dict[str, Any]],
        start: str,
        target: str,
        max_depth: int = 4,
    ) -> list[dict[str, Any]]:
        graph = {}

        for edge in edges:
            graph.setdefault(edge["source"], []).append(edge)

        queue = deque([(start, [])])
        visited = set()

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path

            if len(path) >= max_depth:
                continue

            if current in visited:
                continue

            visited.add(current)

            for edge in graph.get(current, []):
                next_node = edge["target"]
                queue.append((next_node, path + [edge]))

        return []

    def central_nodes(
        self,
        edges: list[dict[str, Any]],
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        degree = {}

        for edge in edges:
            degree[edge["source"]] = degree.get(edge["source"], 0) + 1
            degree[edge["target"]] = degree.get(edge["target"], 0) + 1

        ranked = sorted(
            degree.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            {"node": node, "degree": value}
            for node, value in ranked[:limit]
        ]

    def build_llm_context(self, graph: dict[str, Any]) -> dict[str, Any]:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        causal_paths = graph.get("causal_paths", [])

        important_node_types = {
            "concept",
            "core_concept",
            "claim",
            "assumption",
            "missing_dimension",
            "alternative_hypothesis",
            "recalibration_strategy",
        }

        compact_nodes = [
            {
                "id": node.get("id"),
                "label": node.get("label"),
                "type": node.get("type"),
            }
            for node in nodes
            if node.get("type") in important_node_types
        ]

        compact_edges = [
            {
                "source": edge.get("source"),
                "relation": edge.get("relation"),
                "target": edge.get("target"),
            }
            for edge in edges
            if edge.get("relation")
            not in {
                "mentions",
                "adjacent_concept",
                "has_metric",
                "produces",
            }
        ]

        return {
            "purpose": "Structured cognitive context for future LLM reasoning.",
            "nodes": compact_nodes,
            "relations": compact_edges,
            "causal_paths": causal_paths,
        }
