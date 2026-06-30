"""
DeDe - Cognitive Compiler

Compiles graph queries and inference patterns into a compact cognitive state.

The Cognitive Compiler does not reason.
It prepares a structured cognitive state for:
- Cognitive Reasoner
- LLM Connector
- future Daimon memory
"""

from typing import Any


class CognitiveCompiler:
    """
    Builds a compact cognitive state from graph queries and inference patterns.
    """

    name = "cognitive_compiler"

    def compile(
        self,
        graph_queries: dict[str, Any],
        inference_patterns: dict[str, Any],
    ) -> dict[str, Any]:

        central_nodes = graph_queries.get("central_nodes", [])
        patterns = inference_patterns.get("patterns", [])

        support = []
        pressure = []
        protective_mechanisms = []
        detected_dynamics = []
        missing_dimensions = []
        cognitive_focus = []

        for item in central_nodes:
            node = item.get("node")
            degree = item.get("degree", 0)

            if node:
                cognitive_focus.append(
                    {
                        "node": node,
                        "degree": degree,
                    }
                )

        for pattern in patterns:
            name = pattern.get("name")
            pattern_type = pattern.get("type")
            description = pattern.get("description")
            confidence = pattern.get("confidence", 0)

            if pattern_type in [
                "regulation",
                "protective_relation",
                "revisability_path",
            ]:
                protective_mechanisms.append(
                    self._pattern_entry(
                        name,
                        description,
                        confidence,
                    )
                )

            elif pattern_type in [
                "causal_chain",
                "concept_tension",
                "reduction_path",
                "filter_effect",
                "filter_path",
            ]:
                pressure.append(
                    self._pattern_entry(
                        name,
                        description,
                        confidence,
                    )
                )

            elif pattern_type == "central_concept":
                detected_dynamics.append(
                    self._pattern_entry(
                        name,
                        description,
                        confidence,
                    )
                )

        if self._has_pattern(patterns, "certainty_understanding_tension"):
            missing_dimensions.append(
                "Clarify whether certainty is grounded in knowledge, experience, authority, repetition, or social reinforcement."
            )

        if self._has_pattern(patterns, "reduction_affects_revisability"):
            missing_dimensions.append(
                "Clarify whether reduction is explicit, acknowledged, forgotten, or hidden."
            )

        if self._has_pattern(patterns, "filter_affects_understanding"):
            missing_dimensions.append(
                "Clarify which cognitive filters shape the current interpretation."
            )

        if self._has_pattern(patterns, "revisability_present"):
            support.append(
                {
                    "name": "revisability_support",
                    "description": "Revisability is available as a stabilizing support.",
                    "confidence": 0.75,
                }
            )

        confidence = self._compile_confidence(patterns)

        orientation = self._compile_orientation(
            pressure=pressure,
            protective_mechanisms=protective_mechanisms,
        )

        return {
            "compiler": self.name,
            "status": "ready",
            "orientation": orientation,
            "confidence": confidence,
            "cognitive_focus": cognitive_focus,
            "support": support,
            "pressure": pressure,
            "protective_mechanisms": protective_mechanisms,
            "detected_dynamics": detected_dynamics,
            "missing_dimensions": missing_dimensions,
            "summary": self._build_summary(
                orientation=orientation,
                confidence=confidence,
                support=support,
                pressure=pressure,
                protective_mechanisms=protective_mechanisms,
                missing_dimensions=missing_dimensions,
            ),
        }

    def _pattern_entry(
        self,
        name: str | None,
        description: str | None,
        confidence: float,
    ) -> dict[str, Any]:

        return {
            "name": name or "unknown_pattern",
            "description": description or "",
            "confidence": confidence,
        }

    def _has_pattern(
        self,
        patterns: list[dict[str, Any]],
        name: str,
    ) -> bool:

        return any(
            pattern.get("name") == name
            for pattern in patterns
        )

    def _compile_confidence(
        self,
        patterns: list[dict[str, Any]],
    ) -> float:

        if not patterns:
            return 0.0

        confidence_values = [
            pattern.get("confidence", 0)
            for pattern in patterns
        ]

        return round(
            sum(confidence_values) / len(confidence_values),
            3,
        )

    def _compile_orientation(
        self,
        pressure: list[dict[str, Any]],
        protective_mechanisms: list[dict[str, Any]],
    ) -> str:

        pressure_strength = sum(
            item.get("confidence", 0)
            for item in pressure
        )

        protection_strength = sum(
            item.get("confidence", 0)
            for item in protective_mechanisms
        )

        if pressure_strength > protection_strength * 1.25:
            return "pressure_dominant"

        if protection_strength > pressure_strength * 1.25:
            return "revisability_dominant"

        return "balanced"

    def _build_summary(
        self,
        orientation: str,
        confidence: float,
        support: list[dict[str, Any]],
        pressure: list[dict[str, Any]],
        protective_mechanisms: list[dict[str, Any]],
        missing_dimensions: list[str],
    ) -> str:

        return (
            f"Cognitive state compiled with orientation '{orientation}' "
            f"and confidence {round(confidence * 100)}%. "
            f"Support: {len(support)}. "
            f"Pressure: {len(pressure)}. "
            f"Protective mechanisms: {len(protective_mechanisms)}. "
            f"Missing dimensions: {len(missing_dimensions)}."
        )
