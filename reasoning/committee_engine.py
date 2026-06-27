"""
Committee Engine

Transforms shared workspace observations into a structured
cognitive committee deliberation report.
"""


class CommitteeEngine:

    def deliberate(
        self,
        workspace,
    ):
        observations = workspace.get_all()

        strong_agreements = []
        concerns = []
        recommendations = []

        for obs in observations:
            if obs.confidence >= 0.70:
                strong_agreements.append(obs.agent)

            if obs.confidence <= 0.40:
                concerns.append(obs.agent)

            text = obs.observation.lower()

            if "grounding" in text:
                recommendations.append("Increase factual grounding.")

            if "revision" in text or "recalibration" in text:
                recommendations.append("Consider cognitive recalibration.")

            if "reduction" in text:
                recommendations.append("Check for possible forgotten reductions.")

        return {
            "committee_size": len(observations),
            "strong_agreements": strong_agreements,
            "concerns": concerns,
            "recommendations": sorted(set(recommendations)),
            "summary": (
                f"{len(observations)} agents participated in the cognitive committee. "
                f"{len(strong_agreements)} strong agreements and "
                f"{len(concerns)} concerns were detected."
            ),
        }
