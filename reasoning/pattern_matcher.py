"""
DeDe - Pattern Matcher

Matches cognitive graph structures against pattern definitions.
"""

from typing import Any


class PatternMatcher:
    """
    Detects graph patterns from nodes, causal paths and key paths.
    """

    def match(
        self,
        patterns: list[dict[str, Any]],
        graph_queries: dict[str, Any],
    ) -> list[dict[str, Any]]:

        central_nodes = graph_queries.get("central_nodes", [])
        llm_context = graph_queries.get("llm_context", {})
        causal_paths = llm_context.get("causal_paths", [])
        key_paths = graph_queries.get("key_paths", {})

        node_names = self._extract_node_names(central_nodes)
        path_signatures = self._extract_path_signatures(causal_paths)

        detected = []

        for pattern in patterns:
            if self._matches_required_nodes(pattern, node_names):
                detected.append(pattern)

            elif self._matches_required_path(pattern, path_signatures):
                detected.append(pattern)

            elif self._matches_required_key_path(pattern, key_paths):
                detected.append(pattern)

        return self._unique_patterns(detected)

    def _extract_node_names(
        self,
        central_nodes: list[Any],
    ) -> set[str]:

        names = set()

        for item in central_nodes:
            if isinstance(item, str):
                names.add(item)

            elif isinstance(item, dict):
                node = item.get("node")

                if node:
                    names.add(str(node))

        return names

    def _extract_path_signatures(
        self,
        causal_paths: list[dict[str, Any]],
    ) -> list[list[str]]:

        signatures = []

        for path_data in causal_paths:
            path = path_data.get("path", [])
            signature = []

            for edge in path:
                source = edge.get("source")
                relation = edge.get("relation")
                target = edge.get("target")

                if source and relation and target:
                    signature.append(f"{source}.{relation}.{target}")

            if signature:
                signatures.append(signature)

        return signatures

    def _matches_required_nodes(
        self,
        pattern: dict[str, Any],
        node_names: set[str],
    ) -> bool:

        required_nodes = pattern.get("required_nodes")

        if not required_nodes:
            return False

        return all(node in node_names for node in required_nodes)

    def _matches_required_path(
        self,
        pattern: dict[str, Any],
        path_signatures: list[list[str]],
    ) -> bool:

        required_path = pattern.get("required_path")

        if not required_path:
            return False

        return required_path in path_signatures

    def _matches_required_key_path(
        self,
        pattern: dict[str, Any],
        key_paths: dict[str, Any],
    ) -> bool:

        required_key_path = pattern.get("required_key_path")

        if not required_key_path:
            return False

        return bool(key_paths.get(required_key_path))

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
