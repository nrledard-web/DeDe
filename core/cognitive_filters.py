"""
Cognitive Filters

Transforms detector and committee signals into structural modifiers
for the main cognitive dimensions: G, N, D, R and V.
"""

from dataclasses import dataclass


@dataclass
class CognitiveFilterResult:
    gnosis_modifier: float = 0.0
    nous_modifier: float = 0.0
    doxa_modifier: float = 0.0
    reduction_modifier: float = 0.0
    revisability_modifier: float = 0.0
    notes: list[str] | None = None


class CognitiveFilters:

    def apply(
        self,
        signals: dict,
    ) -> CognitiveFilterResult:

        notes = []

        doxa_modifier = 0.0
        nous_modifier = 0.0
        reduction_modifier = 0.0
        revisability_modifier = 0.0
        gnosis_modifier = 0.0

        if signals.get("strong_certainty", 0.0) > 0.60:
            doxa_modifier += 0.15
            revisability_modifier -= 0.05
            notes.append(
                "Strong certainty increases Doxa and slightly reduces revisability."
            )

        if signals.get("misleading_coherence", 0.0) > 0.50:
            nous_modifier -= 0.10
            doxa_modifier += 0.05
            notes.append(
                "Misleading coherence reduces integrated understanding."
            )

        if signals.get("strategic_omission", 0.0) > 0.50:
            reduction_modifier += 0.15
            nous_modifier -= 0.05
            notes.append(
                "Strategic omission increases reduction pressure."
            )

        if signals.get("argument_density", 0.0) > 0.50:
            nous_modifier += 0.10
            gnosis_modifier += 0.05
            notes.append(
                "Argument density supports Nous and Gnosis."
            )

        if signals.get("revisability", 0.0) > 0.50:
            revisability_modifier += 0.15
            doxa_modifier -= 0.05
            notes.append(
                "Revisability increases cognitive openness and reduces Doxa pressure."
            )

        if signals.get("amphibology", 0.0) > 0.40:
            reduction_modifier += 0.10
            nous_modifier -= 0.10
            notes.append(
                "Amphibology increases ambiguity and weakens integrated understanding."
            )

        return CognitiveFilterResult(
            gnosis_modifier=gnosis_modifier,
            nous_modifier=nous_modifier,
            doxa_modifier=doxa_modifier,
            reduction_modifier=reduction_modifier,
            revisability_modifier=revisability_modifier,
            notes=notes,
        )
