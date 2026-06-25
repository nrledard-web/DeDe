"""
DeDe - Cognitive Interpreter

Interprets DeDe's cognitive vector, formula variants and core metrics.

This module does not detect markers and does not compute formulas.
It translates cognitive mechanics into readable diagnostic observations.
"""

from typing import Any


class CognitiveInterpreter:
    """
    Produces symbolic cognitive interpretations from DeDe reports.
    """

    def interpret(self, detector_results: dict[str, Any]) -> dict[str, Any]:
        vector = detector_results.get("cognitive_vector", {})
        metrics = detector_results.get("metrics", {})
        formulas = detector_results.get("formulas", {})

        core = metrics.get("core", {})
        derived = metrics.get("derived", {})
        mecroyance_variants = formulas.get("mecroyance_variants", {})

        observations = []
        risks = []
        strengths = []

        m0 = mecroyance_variants.get("M0_base", 0.0)
        m1 = mecroyance_variants.get("M1_revisable", 0.0)
        m2 = mecroyance_variants.get("M2_reduction_aware", 0.0)

        if m0 > 0:
            strengths.append(
                "Base grounding currently exceeds doxastic pressure."
            )
        else:
            risks.append(
                "Doxastic pressure exceeds the combined base of knowledge and understanding."
            )

        if m1 > m0:
            strengths.append(
                "Revisability improves the cognitive balance of the statement."
            )

        if m2 < 0:
            risks.append(
                "When reduction is included, the cognitive balance becomes negative."
            )

        if derived.get("forgotten_reduction_pressure", 0.0) > 0.25:
            risks.append(
                "The main pressure appears to come from reduction exceeding revisability."
            )

        if derived.get("cognitive_closure", 0.0) > 0.25:
            risks.append(
                "Cognitive closure pressure is present."
            )

        if derived.get("surconfidence", 0.0) > 0.25:
            risks.append(
                "Certainty exceeds the available grounding."
            )

        if vector.get("gnosis", 0.0) < 0.35:
            observations.append(
                "The statement currently has low articulated knowledge density."
            )

        if vector.get("nous", 0.0) < 0.35:
            observations.append(
                "The statement currently shows limited integrated understanding."
            )

        if vector.get("revisability", 0.0) >= 0.35:
            strengths.append(
                "Some revisability remains available in the cognitive structure."
            )

        diagnosis = self._build_diagnosis(
            risks=risks,
            strengths=strengths,
            observations=observations,
            cognitive_balance=core.get("cognitive_balance", 0.0),
        )

        return {
            "diagnosis": diagnosis,
            "observations": observations,
            "risks": risks,
            "strengths": strengths,
        }

    def _build_diagnosis(
        self,
        risks: list[str],
        strengths: list[str],
        observations: list[str],
        cognitive_balance: float,
    ) -> str:
        if cognitive_balance < -0.25 and risks:
            return "Reduction-aware cognitive imbalance detected."

        if risks and strengths:
            return "Mixed cognitive state: risks are present, but some revisability remains."

        if risks:
            return "Cognitive risk detected."

        if strengths:
            return "Cognitive structure appears relatively balanced."

        if observations:
            return "Limited cognitive signal detected."

        return "No strong cognitive pattern detected."
