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
        agent_positions = []
        discussion = []
        round_table = []

        for obs in observations:

            agent_positions.append(
                {
                    "agent": obs.agent,
                    "confidence": obs.confidence,
                    "observation": obs.observation,
                    "implication": obs.implication,
                }
            )

            discussion.append(
                {
                    "speaker": obs.agent,
                    "statement": obs.observation,
                    "implication": obs.implication,
                    "confidence": obs.confidence,
                }
            )

            round_table.append(
                {
                    "speaker": obs.agent,
                    "responds_to": "committee",
                    "statement": (
                        f"{obs.agent} contributes: "
                        f"{obs.observation}"
                    ),
                    "confidence": obs.confidence,
                }
            )

            if obs.confidence >= 0.70:
                strong_agreements.append(obs.agent)

            if obs.confidence <= 0.40:
                concerns.append(obs.agent)

            text = (
                obs.observation + " " + obs.implication
            ).lower()

            if "grounding" in text:
                recommendations.append(
                    "Increase factual grounding."
                )

            if (
                "revision" in text
                or "recalibration" in text
            ):
                recommendations.append(
                    "Consider cognitive recalibration."
                )

            if "reduction" in text:
                recommendations.append(
                    "Check for possible forgotten reductions."
                )

        committee_confidence = (
            sum(obs.confidence for obs in observations)
            / max(1, len(observations))
        )

        summary = (
            f"{len(observations)} agents participated. "
            f"{len(strong_agreements)} strong agreements, "
            f"{len(concerns)} concerns, "
            f"committee confidence "
            f"{round(committee_confidence * 100)}%."
        )

        return {
            "committee_size": len(observations),
            "agent_positions": agent_positions,
            "discussion": discussion,
            "round_table": round_table,
            "strong_agreements": strong_agreements,
            "concerns": concerns,
            "recommendations": sorted(
                set(recommendations)
            ),
            "committee_confidence": committee_confidence,
            "summary": summary,
        }
