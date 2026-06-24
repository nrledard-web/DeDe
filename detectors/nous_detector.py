"""
DeDe - Nous Detector

Detects integrated understanding:
coherence, nuance, synthesis and conceptual integration.
"""

from typing import Any


class NousDetector:
    """
    Estimates integrated understanding.
    """

    nuance_markers = [
        "however",
        "although",
        "on the other hand",
        "while",
        "despite",
        "nevertheless",
        "yet",
    ]

    synthesis_markers = [
        "therefore",
        "thus",
        "overall",
        "in summary",
        "consequently",
        "hence",
    ]

    relation_markers = [
        "because",
        "therefore",
        "depends",
        "relationship",
        "interaction",
        "context",
        "system",
    ]

    uncertainty_markers = [
        "may",
        "might",
        "could",
        "possibly",
        "probably",
        "hypothesis",
    ]

    def analyze(self, text: str) -> dict[str, Any]:

        t = text.lower()

        nuance = self._find(t, self.nuance_markers)
        synthesis = self._find(t, self.synthesis_markers)
        relations = self._find(t, self.relation_markers)
        uncertainty = self._find(t, self.uncertainty_markers)

        nous_score = min(
            1.0,
            0.20
            + len(nuance) * 0.12
            + len(synthesis) * 0.10
            + len(relations) * 0.09
            + len(uncertainty) * 0.08,
        )

        return {
            "nuance_hits": nuance,
            "synthesis_hits": synthesis,
            "relation_hits": relations,
            "uncertainty_hits": uncertainty,
            "nous_score": nous_score,
            "summary": (
                "High integrated understanding detected."
                if nous_score > 0.70
                else "Limited or moderate integrated understanding."
            ),
        }

    def _find(
        self,
        text: str,
        markers: list[str],
    ) -> list[str]:

        return [
            marker
            for marker in markers
            if marker in text
        ]
