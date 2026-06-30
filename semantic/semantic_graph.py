"""
DeDe - Semantic Graph

Phase 4 symbolic semantic graph.

Transforms semantic descriptions and semantic reasoning into a structured
graph of concepts and relations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.cognitive_workspace import CognitiveWorkspace


@dataclass
class SemanticNode:
    id: str
    label: str
    type: str = "concept"
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "weight": self.weight,
            "metadata": self.metadata,
        }


@dataclass
class SemanticEdge:
    source: str
    relation: str
    target: str
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "weight": self.weight,
            "metadata": self.metadata,
        }


class SemanticGraph:
    """
    Builds a symbolic semantic graph from the current workspace.
    """

    name = "semantic_graph"

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        semantic = workspace.interpretations.get("semantic", {})
        reasoning = workspace.interpretations.get("semantic_reasoner", {})

        nodes: dict[str, SemanticNode] = {}
        edges: list[SemanticEdge] = []

        concepts = semantic.get("main_concepts", [])
        claims = semantic.get("claims", [])
        semantic_relations = semantic.get("relations", [])

        assumptions = reasoning.get("assumptions", [])
        uncertainties = reasoning.get("uncertainties", [])
        alternatives = reasoning.get("alternative_hypotheses", [])
        missing_dimensions = reasoning.get("missing_dimensions", [])
        causal_links = reasoning.get("causal_links", [])

        for concept in concepts:
            self._add_node(nodes, concept, "concept")

        for index, claim in enumerate(claims):
            claim_id = f"claim:{index}"

            self._add_node(
                nodes,
                claim_id,
                "claim",
                label=claim,
                metadata={"index": index},
            )

            for concept in concepts:
                if concept.lower() in claim.lower():
                    edges.append(
                        SemanticEdge(
                            source=claim_id,
                            relation="mentions",
                            target=self._node_id(concept),
                            weight=0.7,
                            metadata={"source": "semantic_claim"},
                        )
                    )

        for relation in semantic_relations:
            source = relation.get("source")
            target = relation.get("target")
            rel = relation.get("relation", "related_to")

            if not source or not target:
                continue

            self._add_node(nodes, source, "concept")
            self._add_node(nodes, target, "concept")

            edges.append(
                SemanticEdge(
                    source=self._node_id(source),
                    relation=rel,
                    target=self._node_id(target),
                    weight=0.6,
                    metadata={"source": "semantic_engine"},
                )
            )

        for link in causal_links:
            source = link.get("source")
            target = link.get("target")
            rel = link.get("relation", "influences")

            if not source or not target:
                continue

            self._add_node(nodes, source, "concept")
            self._add_node(nodes, target, "concept")

            edges.append(
                SemanticEdge(
                    source=self._node_id(source),
                    relation=rel,
                    target=self._node_id(target),
                    weight=1.0,
                    metadata={"source": "semantic_reasoner"},
                )
            )

        self._attach_reasoning_nodes(
            nodes, edges, assumptions, "assumption", "has_assumption", "mecroyance"
        )

        self._attach_reasoning_nodes(
            nodes,
            edges,
            uncertainties,
            "uncertainty",
            "has_uncertainty",
            "claim:0" if claims else None,
        )

        self._attach_reasoning_nodes(
            nodes,
            edges,
            alternatives,
            "alternative_hypothesis",
            "has_alternative",
            "mecroyance",
        )

        self._attach_reasoning_nodes(
            nodes,
            edges,
            missing_dimensions,
            "missing_dimension",
            "missing_dimension",
            "mecroyance",
        )

        self._add_dede_core_relations(nodes, edges)

        result = self._build_result(nodes, edges)

        workspace.set_raw(
            "semantic_node_count",
            result["node_count"],
            {"engine": self.name, "summary": "Number of semantic graph nodes."},
        )

        workspace.set_raw(
            "semantic_edge_count",
            result["edge_count"],
            {"engine": self.name, "summary": "Number of semantic graph edges."},
        )

        workspace.set_raw(
            "semantic_graph_density",
            result["density"],
            {"engine": self.name, "summary": "Semantic graph density."},
        )

        workspace.set_raw(
            "semantic_causal_path_count",
            result["causal_path_count"],
            {"engine": self.name, "summary": "Detected cognitive causal paths."},
        )

        workspace.add_interpretation(self.name, result)

        return workspace

    def _node_id(self, value: str) -> str:
        return str(value).strip().lower().replace(" ", "_")

    def _add_node(
        self,
        nodes: dict[str, SemanticNode],
        value: str,
        node_type: str,
        label: str | None = None,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        node_id = self._node_id(value)

        if node_id not in nodes:
            nodes[node_id] = SemanticNode(
                id=node_id,
                label=label or str(value),
                type=node_type,
                weight=weight,
                metadata=metadata or {},
            )

        return node_id

    def _attach_reasoning_nodes(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticEdge],
        items: list[str],
        node_type: str,
        relation: str,
        anchor: str | None,
    ) -> None:
        if not anchor:
            return

        anchor_id = self._node_id(anchor)

        if anchor_id not in nodes:
            self._add_node(nodes, anchor_id, "concept")

        for index, item in enumerate(items):
            node_id = f"{node_type}:{index}"

            self._add_node(
                nodes,
                node_id,
                node_type,
                label=item,
                weight=0.8,
                metadata={"index": index},
            )

            edges.append(
                SemanticEdge(
                    source=anchor_id,
                    relation=relation,
                    target=node_id,
                    weight=0.8,
                    metadata={"source": "semantic_reasoner"},
                )
            )

    def _add_dede_core_relations(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticEdge],
    ) -> None:
        core_relations = [
            ("mecroyance", "depends_on", "certainty"),
            ("mecroyance", "depends_on", "understanding"),
            ("mecroyance", "depends_on", "reduction"),
            ("reduction", "can_produce", "closure"),
            ("closure", "reduces", "revisability"),
            ("revisability", "limits", "mecroyance"),
            ("grounding", "supports", "understanding"),
            ("integration", "supports", "understanding"),
            ("certainty", "can_increase", "closure"),
        ]

        for source, relation, target in core_relations:
            self._add_node(nodes, source, "core_concept")
            self._add_node(nodes, target, "core_concept")

            edge = SemanticEdge(
                source=self._node_id(source),
                relation=relation,
                target=self._node_id(target),
                weight=0.9,
                metadata={
                    "source": "dede_core_ontology",
                    "revisable": True,
                },
            )

            if not self._edge_exists(edges, edge):
                edges.append(edge)

    def _edge_exists(self, edges: list[SemanticEdge], edge: SemanticEdge) -> bool:
        return any(
            existing.source == edge.source
            and existing.relation == edge.relation
            and existing.target == edge.target
            for existing in edges
        )

    def _build_result(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticEdge],
    ) -> dict[str, Any]:
        node_count = len(nodes)
        edge_count = len(edges)

        density = 0.0
        if node_count > 1:
            density = edge_count / (node_count * (node_count - 1))

        causal_paths = self._detect_cognitive_paths(edges)

        return {
            "engine": self.name,
            "nodes": [node.to_dict() for node in nodes.values()],
            "edges": [edge.to_dict() for edge in edges],
            "node_count": node_count,
            "edge_count": edge_count,
            "density": round(density, 4),
            "causal_paths": causal_paths,
            "causal_path_count": len(causal_paths),
            "summary": "Semantic graph built from concepts, claims and semantic reasoning.",
        }

    def _detect_cognitive_paths(
        self,
        edges: list[SemanticEdge],
    ) -> list[dict[str, Any]]:
        edge_set = {(edge.source, edge.relation, edge.target) for edge in edges}
        paths: list[dict[str, Any]] = []

        expected_paths = [
            [
                ("certainty", "can_increase", "closure"),
                ("closure", "reduces", "revisability"),
            ],
            [
                ("reduction", "can_produce", "closure"),
                ("closure", "reduces", "revisability"),
            ],
            [
                ("revisability", "limits", "mecroyance"),
            ],
            [
                ("certainty", "can_stabilize_faster_than", "understanding"),
            ],
        ]

        for path in expected_paths:
            if all(step in edge_set for step in path):
                paths.append(
                    {
                        "path": [
                            {
                                "source": source,
                                "relation": relation,
                                "target": target,
                            }
                            for source, relation, target in path
                        ],
                        "length": len(path),
                    }
                )

        return paths
