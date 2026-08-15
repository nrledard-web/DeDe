"""
Meta Agent
Cognitive Committee
"""

from core.shared_workspace import SharedCognitiveWorkspace
from reasoning.committee_engine import CommitteeEngine
from reasoning.committee_reasoner import CommitteeReasoner


class MetaAgent:

    def __init__(self):
        self.committee_engine = CommitteeEngine()
        self.committee_reasoner = CommitteeReasoner()

    def analyze(
        self,
        workspace: SharedCognitiveWorkspace,
    ):

        committee = self.committee_engine.deliberate(
            workspace
        )

        reasoning = self.committee_reasoner.reason(
            workspace,
            committee,
        )

        narrative = self._build_narrative(
            reasoning
        )

        return {
            "agent": "meta",
            "committee_size": committee["committee_size"],
            "agreements": committee["strong_agreements"],
            "concerns": committee["concerns"],
            "recommendations": committee["recommendations"],
            "agent_positions": committee["agent_positions"],
            "discussion": committee["discussion"],
            "round_table": committee["round_table"],
            "committee_confidence": committee["committee_confidence"],
            "summary": narrative,
            "technical_summary": committee["summary"],
            "confidence": 0.95,
            "coherence": committee["committee_confidence"],
            "reasoning": reasoning,
            "diagnoses": reasoning["diagnoses"],
            "hypotheses": reasoning["hypotheses"],
            "strengths": reasoning["strengths"],
            "weaknesses": reasoning["weaknesses"],
            "conflicts": reasoning["conflicts"],
            "recommended_next_steps": reasoning["recommended_next_steps"],
            "narrative": narrative,
        }

    def _build_narrative(
        self,
        reasoning,
    ):

        strengths = reasoning.get(
            "strengths",
            [],
        )

        weaknesses = reasoning.get(
            "weaknesses",
            [],
        )

        diagnoses = reasoning.get(
            "diagnoses",
            [],
        )

        next_steps = reasoning.get(
            "recommended_next_steps",
            [],
        )

        metrics = reasoning.get(
            "metrics",
            {},
        )

        if not isinstance(
            metrics,
            dict,
        ):
            metrics = {}

        # ---------------------------------------------
        # Structured cognitive state
        # ---------------------------------------------

        gnosis = self._safe_level(
            metrics.get(
                "gnosis",
                reasoning.get(
                    "gnosis",
                    0.0,
                ),
            )
        )

        nous = self._safe_level(
            metrics.get(
                "nous",
                reasoning.get(
                    "nous",
                    0.0,
                ),
            )
        )

        doxa = self._safe_level(
            metrics.get(
                "doxa",
                reasoning.get(
                    "doxa",
                    0.0,
                ),
            )
        )

        integration = self._safe_level(
            metrics.get(
                "integration",
                reasoning.get(
                    "integration",
                    nous,
                ),
            )
        )

        # ---------------------------------------------
        # Structural interpretation
        # ---------------------------------------------

        has_knowledge = (
            gnosis >= 0.45
        )

        weak_integration = (
            integration < 0.45
            or nous < 0.45
        )

        certainty_exceeds_understanding = (
            doxa > nous
        )

        # ---------------------------------------------
        # Narrative
        # ---------------------------------------------

        if (
            has_knowledge
            and weak_integration
        ):

            opening = (
                "The committee has a factual basis, "
                "but integrated understanding remains weak."
            )

        elif has_knowledge:

            opening = (
                "The committee has a factual basis for analysis."
            )

        elif weak_integration:

            opening = (
                "The committee detects weak conceptual integration."
            )

        else:

            opening = (
                "The committee found no major cognitive imbalance."
            )

        if certainty_exceeds_understanding:

            middle = (
                "Certainty should therefore remain cautious "
                "until understanding becomes more integrated."
            )

        else:

            middle = (
                "The current interpretation should remain revisable."
            )

        if next_steps:

            first_step = str(
                next_steps[0]
            ).strip()

            if first_step:

                closing = (
                    "The recommended next step is to "
                    f"{first_step[0].lower()}"
                    f"{first_step[1:]}"
                )

            else:

                closing = (
                    "The recommended next step is "
                    "to maintain revisability."
                )

        else:

            closing = (
                "The recommended next step is "
                "to maintain revisability."
            )

        return (
            f"{opening} "
            f"{middle} "
            f"{closing}"
        )

    @staticmethod
    def _safe_level(
        value,
    ) -> float:

        try:
            level = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if level > 1.0:
            level = (
                level / 100.0
            )

        return max(
            0.0,
            min(
                1.0,
                level,
            ),
        )
