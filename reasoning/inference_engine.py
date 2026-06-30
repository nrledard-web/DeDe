"""
DeDe - Inference Engine

Detects cognitive graph patterns before interpretation.

This layer does not explain yet.
It detects structures:
- causal chains
- closure loops
- revisability supports
- reduction pressure
- filter influence
- central concept dominance
"""

from typing import Any


class InferenceEngine:
    """
    Detects reusable cognitive patterns from graph query results.
    """

    name = "inference_engine"

    def analyze(
        self,
        graph_queries: dict[str, Any],
    ) -> dict[str, Any]:

        central_nodes = graph_queries.get("central_nodes", [])
        llm_context = graph_queries.get("llm_context", {})
        causal_paths = llm_context.get("causal_paths", [])
        key_paths = graph_queries.get("key_paths", {})

        patterns = []

        nodes = [
            item.get("node")
            for item in central_nodes
            if isinstance(item, dict) and item.get("node")
        ]

        # --------------------------------------------------
        # Central dominance patterns
        # --------------------------------------------------

        if "mecroyance" in nodes:
            patterns.append(
                {
                    "type": "central_concept",
                    "name": "mecroyance_centrality",
                    "description": "Mecroyance appears as a central organizing concept.",
                    "confidence": 0.8,
                }
            )

        if "certainty" in nodes and "understanding" in nodes:
            patterns.append(
                {
                    "type": "concept_tension",
                    "name": "certainty_understanding_tension",
                    "description": "Certainty and understanding are both central, suggesting a possible calibration tension.",
                    "confidence": 0.75,
                }
            )

        if "revisability" in nodes:
            patterns.append(
                {
                    "type": "regulation",
                    "name": "revisability_present",
                    "description": "Revisability is structurally present and may regulate closure.",
                    "confidence": 0.75,
                }
            )

        # --------------------------------------------------
        # Causal path patterns
        # --------------------------------------------------

        for path_data in causal_paths:
            path = path_data.get("path", [])
            signature = self._path_signature(path)

            if signature == [
                "certainty.can_increase.closure",
                "closure.reduces.revisability",
            ]:
                patterns.append(
                    {
                        "type": "causal_chain",
                        "name": "certainty_to_closure_to_low_revisability",
                        "description": "Certainty may increase closure, which may reduce revisability.",
                        "confidence": 0.9,
                    }
                )

            if signature == [
                "reduction.can_produce.closure",
                "closure.reduces.revisability",
            ]:
                patterns.append(
                    {
                        "type": "causal_chain",
                        "name": "reduction_to_closure_to_low_revisability",
                        "description": "Reduction may produce closure, which may reduce revisability.",
                        "confidence": 0.9,
                    }
                )

            if signature == [
                "revisability.limits.mecroyance",
            ]:
                patterns.append(
                    {
                        "type": "protective_relation",
                        "name": "revisability_limits_mecroyance",
                        "description": "Revisability appears as a limiting force against mecroyance.",
                        "confidence": 0.9,
                    }
                )

            if signature == [
                "cognitive_filter.shapes.understanding",
            ]:
                patterns.append(
                    {
                        "type": "filter_effect",
                        "name": "filter_shapes_understanding",
                        "description": "A cognitive filter appears to shape understanding.",
                        "confidence": 0.85,
                    }
                )

        # --------------------------------------------------
        # Key path patterns
        # --------------------------------------------------

        if key_paths.get("certainty_to_revisability"):
            patterns.append(
                {
                    "type": "revisability_path",
                    "name": "certainty_remains_revisable",
                    "description": "Certainty is connected to revisability rather than only closure.",
                    "confidence": 0.8,
                }
            )

        if key_paths.get("reduction_to_revisability"):
            patterns.append(
                {
                    "type": "reduction_path",
                    "name": "reduction_affects_revisability",
                    "description": "Reduction may affect revisability through closure.",
                    "confidence": 0.85,
                }
            )

        if key_paths.get("cognitive_filter_to_understanding"):
            patterns.append(
                {
                    "type": "filter_path",
                    "name": "filter_affects_understanding",
                    "description": "Understanding appears partly shaped by a cognitive filter.",
                    "confidence": 0.85,
                }
            )

        return {
            "engine": self.name,
            "status": "ready",
            "pattern_count": len(patterns),
            "patterns": self._unique_patterns(patterns),
        }

    def _path_signature(
        self,
        path: list[dict[str, Any]],
    ) -> list[str]:

        signature = []

        for edge in path:
            source = edge.get("source")
            relation = edge.get("relation")
            target = edge.get("target")

            if source and relation and target:
                signature.append(f"{source}.{relation}.{target}")

        return signature

    def _unique_patterns(
        self,
        patterns: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        seen = set()
        unique = []

        for pattern in patterns:
            name = pattern.get("name")

            if name not in seen:
                seen.add(name)
                unique.append(pattern)

        return unique
