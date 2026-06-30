"""
DeDe - Inference Engine

Detects cognitive graph patterns before interpretation.

Architecture:
Graph Queries
    ↓
Pattern Library
    ↓
Pattern Matcher
    ↓
Inference Patterns
"""

from typing import Any

from reasoning.pattern_library import PatternLibrary
from reasoning.pattern_matcher import PatternMatcher


class InferenceEngine:
    """
    Detects reusable cognitive patterns from graph query results.
    """

    name = "inference_engine"

    def __init__(self):
        self.pattern_library = PatternLibrary()
        self.pattern_matcher = PatternMatcher()

    def analyze(
        self,
        graph_queries: dict[str, Any],
    ) -> dict[str, Any]:

        patterns = self.pattern_library.get_patterns()

        detected_patterns = self.pattern_matcher.match(
            patterns=patterns,
            graph_queries=graph_queries,
        )

        return {
            "engine": self.name,
            "status": "ready",
            "available_pattern_count": len(patterns),
            "detected_pattern_count": len(detected_patterns),
            "patterns": detected_patterns,
            "summary": self._build_summary(detected_patterns),
        }

    def _build_summary(
        self,
        patterns: list[dict[str, Any]],
    ) -> str:

        if not patterns:
            return "No cognitive graph pattern detected."

        names = [
            pattern.get("name", "unknown_pattern")
            for pattern in patterns
        ]

        return (
            "Detected cognitive graph patterns: "
            + ", ".join(names)
            + "."
        )
