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

        previous_speaker = "committee"

        for obs in observations:

            signals = obs.signals or {}

            statement = signals.get(
                "committee_reply",
                obs.observation,
            )

            agent_positions.append(
                {
                    "agent": obs.agent,
                    "confidence": obs.confidence,
                    "statement": statement,
                }
            )

            discussion.append(
                {
                    "speaker": obs.agent,
                    "statement": statement,
                    "confidence": obs.confidence,
                }
            )

            round_table.append(
                {
                    "speaker": obs.agent,
                    "responds_to": previous_speaker,
                    "statement": statement,
                    "confidence": obs.confidence,
                }
            )

            previous_speaker = obs.agent

            if obs.confidence >= 0.70:
                strong_agreements.append(
                    obs.agent
                )

            if obs.confidence <= 0.40:
                concerns.append(
                    obs.agent
                )

            # --------------------------------------------------
            # Structured recommendations
            # --------------------------------------------------
            #
            # Recommendations come from structured cognitive
            # signals rather than wording contained in
            # committee statements.
            # --------------------------------------------------

            grounding = signals.get(
                "grounding"
            )

            integration = signals.get(
                "integration"
            )

            reduction = signals.get(
                "reduction"
            )

            recalibration_needed = signals.get(
                "recalibration_needed"
            )

            revisability_level = signals.get(
                "revisability_level"
            )

            forgotten_reduction = signals.get(
                "forgotten_reduction"
            )

            excessive_reduction = signals.get(
                "excessive_reduction"
            )

            # ----------------------------------------------
            # Grounding
            # ----------------------------------------------

            if (
                isinstance(
                    grounding,
                    (int, float),
                )
                and grounding < 0.40
            ):
                recommendations.append(
                    "Increase factual grounding."
                )

            # ----------------------------------------------
            # Integration
            # ----------------------------------------------

            if (
                isinstance(
                    integration,
                    (int, float),
                )
                and integration < 0.45
            ):
                recommendations.append(
                    "Strengthen conceptual integration."
                )

            # ----------------------------------------------
            # Reduction
            # ----------------------------------------------

            if (
                forgotten_reduction is True
                or excessive_reduction is True
            ):
                recommendations.append(
                    "Check for possible excessive "
                    "or forgotten reductions."
                )

            elif (
                isinstance(
                    reduction,
                    (int, float),
                )
                and reduction >= 0.60
            ):
                recommendations.append(
                    "Check reduction pressure."
                )

            # ----------------------------------------------
            # Revisability / recalibration
            # ----------------------------------------------

            if recalibration_needed is True:
                recommendations.append(
                    "Consider cognitive recalibration."
                )

            elif (
                isinstance(
                    revisability_level,
                    (int, float),
                )
                and revisability_level < 0.50
            ):
                recommendations.append(
                    "Strengthen revisability."
                )

        # --------------------------------------------------
        # Committee summary
        # --------------------------------------------------
        #
        # IMPORTANT:
        # This block belongs AFTER the observation loop.
        # --------------------------------------------------

        committee_confidence = (
            sum(
                obs.confidence
                for obs in observations
            )
            / max(
                1,
                len(observations),
            )
        )

        summary = (
            f"{len(observations)} agents participated. "
            f"{len(strong_agreements)} strong agreements, "
            f"{len(concerns)} concerns, "
            f"committee confidence "
            f"{round(committee_confidence * 100)}%."
        )

        return {
            "committee_size": len(
                observations
            ),
            "agent_positions": (
                agent_positions
            ),
            "discussion": (
                discussion
            ),
            "round_table": (
                round_table
            ),
            "strong_agreements": (
                strong_agreements
            ),
            "concerns": (
                concerns
            ),
            "recommendations": sorted(
                set(
                    recommendations
                )
            ),
            "committee_confidence": (
                committee_confidence
            ),
            "summary": summary,
        }
