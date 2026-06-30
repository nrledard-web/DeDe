"""
DeDe - Pattern Library

Reusable cognitive graph pattern definitions.
"""


class PatternLibrary:
    """
    Stores known cognitive pattern signatures.
    """

    def get_patterns(self) -> list[dict]:
        return [
            {
                "name": "mecroyance_centrality",
                "type": "central_concept",
                "required_nodes": ["mecroyance"],
                "description": "Mecroyance appears as a central organizing concept.",
                "confidence": 0.8,
            },
            {
                "name": "certainty_understanding_tension",
                "type": "concept_tension",
                "required_nodes": ["certainty", "understanding"],
                "description": (
                    "Certainty and understanding are both central, "
                    "suggesting a possible calibration tension."
                ),
                "confidence": 0.75,
            },
            {
                "name": "revisability_present",
                "type": "regulation",
                "required_nodes": ["revisability"],
                "description": (
                    "Revisability is structurally present and may regulate closure."
                ),
                "confidence": 0.75,
            },
            {
                "name": "certainty_to_closure_to_low_revisability",
                "type": "causal_chain",
                "required_path": [
                    "certainty.can_increase.closure",
                    "closure.reduces.revisability",
                ],
                "description": (
                    "Certainty may increase closure, which may reduce revisability."
                ),
                "confidence": 0.9,
            },
            {
                "name": "reduction_to_closure_to_low_revisability",
                "type": "causal_chain",
                "required_path": [
                    "reduction.can_produce.closure",
                    "closure.reduces.revisability",
                ],
                "description": (
                    "Reduction may produce closure, which may reduce revisability."
                ),
                "confidence": 0.9,
            },
            {
                "name": "revisability_limits_mecroyance",
                "type": "protective_relation",
                "required_path": [
                    "revisability.limits.mecroyance",
                ],
                "description": (
                    "Revisability appears as a limiting force against mecroyance."
                ),
                "confidence": 0.9,
            },
            {
                "name": "filter_shapes_understanding",
                "type": "filter_effect",
                "required_path": [
                    "cognitive_filter.shapes.understanding",
                ],
                "description": (
                    "A cognitive filter appears to shape understanding."
                ),
                "confidence": 0.85,
            },
            {
                "name": "certainty_remains_revisable",
                "type": "revisability_path",
                "required_key_path": "certainty_to_revisability",
                "description": (
                    "Certainty is connected to revisability rather than only closure."
                ),
                "confidence": 0.8,
            },
            {
                "name": "reduction_affects_revisability",
                "type": "reduction_path",
                "required_key_path": "reduction_to_revisability",
                "description": (
                    "Reduction may affect revisability through closure."
                ),
                "confidence": 0.85,
            },
            {
                "name": "filter_affects_understanding",
                "type": "filter_path",
                "required_key_path": "cognitive_filter_to_understanding",
                "description": (
                    "Understanding appears partly shaped by a cognitive filter."
                ),
                "confidence": 0.85,
            },
        ]
