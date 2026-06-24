"""
DeDe - Doxa Engine

Core symbolic engine for evaluating certainty, epistemic rigidity
and cognitive closure.
"""

from typing import Any


class DoxaEngine:
    """
    Computes symbolic Doxa indicators.
    """

    certainty_markers = [
        "always",
        "never",
        "certain",
        "obviously",
        "everyone",
        "nobody",
        "undeniable",
        "must",
        "cannot",
        "impossible",
        "definitely",
        "absolutely",
        "without doubt",
    ]

    nuance_markers = [
        "maybe",
        "perhaps",
        "possible",
        "might",
        "could",
        "sometimes",
        "depends",
        "uncertain",
        "hypothesis",
        "open question",
    ]

    def analyze(self, text: str) -> dict[str, Any]:
        text = text.lower()

        certainty_count = self._count_markers(text, self.certainty_markers)
        nuance_count = self._count_markers(text, self.nuance_markers)

        doxa_level = min(
            1.0,
            max(
                0.0,
                0.40 + certainty_count * 0.10 - nuance_count * 0.06,
            ),
        )

        closure_level = max(0.0, doxa_level - 0.60)

        return {
            "doxa_level": doxa_level,
            "closure_level": closure_level,
            "certainty_markers": certainty_count,
            "nuance_markers": nuance_count,
            "cognitive_closure": doxa_level > 0.75,
        }

    def _count_markers(self, text: str, markers: list[str]) -> int:
        return sum(1 for marker in markers if marker in text)
