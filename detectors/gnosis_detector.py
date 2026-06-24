"""
DeDe - Gnosis Detector

Detects articulated knowledge signals:
facts, sources, dates, numbers, references and verification markers.
"""

from typing import Any


class GnosisDetector:
    """
    Estimates the density of articulated knowledge in a text.
    """

    source_markers = [
        "according to",
        "source",
        "study",
        "research",
        "paper",
        "report",
        "data",
        "evidence",
        "citation",
        "reference",
        "document",
    ]

    factual_markers = [
        "date",
        "year",
        "number",
        "percentage",
        "statistics",
        "law",
        "article",
        "constitution",
        "experiment",
        "observation",
        "measurement",
    ]

    verification_markers = [
        "verify",
        "verified",
        "check",
        "confirmed",
        "tested",
        "replicable",
        "falsifiable",
        "peer reviewed",
    ]

    def analyze(self, text: str) -> dict[str, Any]:
        normalized = text.lower()

        source_hits = self._find(normalized, self.source_markers)
        factual_hits = self._find(normalized, self.factual_markers)
        verification_hits = self._find(normalized, self.verification_markers)
        numeric_hits = self._count_numbers(normalized)

        gnosis_score = min(
            1.0,
            0.25
            + len(source_hits) * 0.10
            + len(factual_hits) * 0.08
            + len(verification_hits) * 0.12
            + numeric_hits * 0.03,
        )

        return {
            "source_hits": source_hits,
            "factual_hits": factual_hits,
            "verification_hits": verification_hits,
            "numeric_hits": numeric_hits,
            "gnosis_score": gnosis_score,
            "summary": (
                "High articulated knowledge density detected."
                if gnosis_score > 0.70
                else "Limited or moderate articulated knowledge density detected."
            ),
        }

    def _find(self, text: str, markers: list[str]) -> list[str]:
        return [marker for marker in markers if marker in text]

    def _count_numbers(self, text: str) -> int:
        return sum(1 for token in text.split() if any(char.isdigit() for char in token))
