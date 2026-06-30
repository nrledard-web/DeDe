"""
DeDe - Semantic Graph

Phase 4 symbolic semantic graph.

Builds and enriches a cognitive semantic graph from:
- concepts
- claims
- semantic reasoning
- agent interpretations
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
    Builds and enriches a symbolic cognitive graph.
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
            nodes,
            edges,
            assumptions,
            "assumption",
            "has_assumption",
            "mecroyance",
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
        self._store_result(workspace, result)

        return workspace

    def enrich_from_agents(
        self,
        workspace: CognitiveWorkspace,
        agent_results: dict[str, dict[str, Any]],
    ) -> CognitiveWorkspace:
        """
        Phase 4.2.

        Agents add cognitive nodes and relations to the existing graph.
        """

        graph = workspace.interpretations.get(self.name, {})

        nodes: dict[str, SemanticNode] = {
            node["id"]: SemanticNode(
                id=node["id"],
                label=node["label"],
                type=node.get("type", "concept"),
                weight=node.get("weight", 1.0),
                metadata=node.get("metadata", {}),
            )
            for node in graph.get("nodes", [])
        }

        edges: list[SemanticEdge] = [
            SemanticEdge(
                source=edge["source"],
                relation=edge["relation"],
                target=edge["target"],
                weight=edge.get("weight", 1.0),
                metadata=edge.get("metadata", {}),
            )
            for edge in graph.get("edges", [])
        ]

        for agent_name, result in agent_results.items():
            agent_node = f"agent:{agent_name}"

            self._add_node(
                nodes,
                agent_node,
                "cognitive_agent",
                label=agent_name,
                weight=0.9,
                metadata={"source": "agent_interpretation"},
            )

            summary = result.get("summary")

            if summary:
                summary_node = f"{agent_name}:summary"

                self._add_node(
                    nodes,
                    summary_node,
                    "agent_summary",
                    label=summary,
                    weight=0.7,
                    metadata={"agent": agent_name},
                )

                self._add_edge(
                    edges,
                    agent_node,
                    "produces",
                    summary_node,
                    weight=0.8,
                    metadata={"source": agent_name},
                )

            self._enrich_by_agent_type(
                nodes,
                edges,
                agent_name,
                result,
            )

        enriched_result = self._build_result(nodes, edges)
        enriched_result["enriched_by_agents"] = True
        enriched_result["agent_enrichment_count"] = len(agent_results)
        enriched_result[
            "summary"
        ] = "Semantic graph enriched by cognitive agent interpretations."

        self._store_result(workspace, enriched_result)

        return workspace

    def _enrich_by_agent_type(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticEdge],
        agent_name: str,
        result: dict[str, Any],
    ) -> None:
        agent_node = f"agent:{agent_name}"

        if agent_name == "nous":
            self._add_cognitive_assessment(
                nodes,
                edges,
                agent_node,
                "understanding",
                "assesses",
                "nous_level",
                result.get("nous_level"),
            )

            if result.get("integrated_understanding_needed"):
                self._add_cognitive_relation(
                    nodes,
                    edges,
                    "understanding",
                    "requires",
                    "integration",
                    agent_name,
                )

        elif agent_name == "doxa":
            self._add_cognitive_assessment(
                nodes,
                edges,
                agent_node,
                "certainty",
                "assesses",
                "doxa_level",
                result.get("doxa_level"),
            )

            if result.get("cognitive_closure"):
                self._add_cognitive_relation(
                    nodes,
                    edges,
                    "certainty",
                    "risks_producing",
                    "closure",
                    agent_name,
                )
            else:
                self._add_cognitive_relation(
                    nodes,
                    edges,
                    "certainty",
                    "remains_revisable_through",
                    "revisability",
                    agent_name,
                )

        elif agent_name == "reduction":
            self._add_cognitive_assessment(
                nodes,
                edges,
                agent_node,
                "reduction",
                "assesses",
                "reduction_level",
                result.get("reduction_level"),
            )

            if result.get("possible_hidden_assumptions"):
                self._add_cognitive_relation(
                    nodes,
                    edges,
                    "reduction",
                    "depends_on_hidden_assumption",
                    "assumption",
                    agent_name,
                )
            else:
                self._add_cognitive_relation(
                    nodes,
                    edges,
                    "reduction",
                    "currently_limited_by",
                    "grounding",
                    agent_name,
                )

        elif agent_name == "nouscope":
            self._add_cognitive_assessment(
                nodes,
                edges,
                agent_node,
                "cognitive_filter",
                "assesses",
                "cognitive_filter_level",
                result.get("cognitive_filter_level"),
            )

            self._add_cognitive_relation(
                nodes,
                edges,
                "cognitive_filter",
                "shapes",
                "understanding",
                agent_name,
            )

        elif agent_name == "cognitive_therapy":
            self._add_cognitive_assessment(
                nodes,
                edges,
                agent_node,
                "revisability",
                "assesses",
                "revisability_level",
                result.get("revisability_level"),
            )

            strategies = result.get("strategies", [])

            for index, strategy in enumerate(strategies):
                strategy_node = f"strategy:{index}"

                self._add_node(
                    nodes,
                    strategy_node,
                    "recalibration_strategy",
                    label=strategy,
                    weight=0.75,
                    metadata={"agent": agent_name},
                )

                self._add_edge(
                    edges,
                    "revisability",
                    "can_be_supported_by",
                    strategy_node,
                    weight=0.75,
                    metadata={"source": agent_name},
                )

    def _add_cognitive_assessment(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticEdge],
        agent_node: str,
        target: str,
        relation: str,
        metric_name: str,
        value: Any,
    ) -> None:
        metric_node = f"metric:{metric_name}"

        self._add_node(
            nodes,
            metric_node,
            "cognitive_metric",
            label=metric_name,
            weight=0.7,
            metadata={"value": value},
        )

        self._add_edge(
            edges,
            agent_node,
            relation,
            target,
            weight=0.8,
            metadata={"metric": metric_name, "value": value},
        )

        self._add_edge(
            edges,
            target,
            "has_metric",
            metric_node,
            weight=0.7,
            metadata={"value": value},
        )

    def _add_cognitive_relation(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticEdge],
        source: str,
        relation: str,
        target: str,
        agent_name: str,
    ) -> None:
        self._add_node(nodes, source, "core_concept")
        self._add_node(nodes, target, "core_concept")

        self._add_edge(
            edges,
            source,
            relation,
            target,
            weight=0.8,
            metadata={
                "source": agent_name,
                "type": "agent_cognitive_relation",
                "revisable": True,
            },
        )

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

    def _add_edge(
        self,
        edges: list[SemanticEdge],
        source: str,
        relation: str,
        target: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        edge = SemanticEdge(
            source=self._node_id(source),
            relation=relation,
            target=self._node_id(target),
            weight=weight,
            metadata=metadata or {},
        )

        if not self._edge_exists(edges, edge):
            edges.append(edge)

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

            self._add_edge(
                edges,
                anchor_id,
                relation,
                node_id,
                weight=0.8,
                metadata={"source": "semantic_reasoner"},
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

            self._add_edge(
                edges,
                source,
                relation,
                target,
                weight=0.9,
                metadata={
                    "source": "dede_core_ontology",
                    "revisable": True,
                },
            )

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

    def _store_result(
        self,
        workspace: CognitiveWorkspace,
        result: dict[str, Any],
    ) -> None:
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
            [
                ("cognitive_filter", "shapes", "understanding"),
            ],
            [
                ("revisability", "can_be_supported_by", "strategy:0"),
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
