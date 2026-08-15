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

        conflicts = reasoning.get(
            "conflicts",
            [],
        )

        hypotheses = reasoning.get(
            "hypotheses",
            [],
        )

        # ---------------------------------------------
        # Structural state
        # ---------------------------------------------
        #
        # Do not infer cognitive state from exact English
        # phrases contained in narrative strings.
        #
        # We use the presence and quantity of structured
        # committee outputs instead.
        # ---------------------------------------------

        strength_count = (
            len(strengths)
            if isinstance(strengths, list)
            else 0
        )

        weakness_count = (
            len(weaknesses)
            if isinstance(weaknesses, list)
            else 0
        )

        diagnosis_count = (
            len(diagnoses)
            if isinstance(diagnoses, list)
            else 0
        )

        conflict_count = (
            len(conflicts)
            if isinstance(conflicts, list)
            else 0
        )

        hypothesis_count = (
            len(hypotheses)
            if isinstance(hypotheses, list)
            else 0
        )

        # ---------------------------------------------
        # Narrative
        # ---------------------------------------------

        if (
            strength_count > 0
            and weakness_count > 0
        ):
            opening = (
                "The committee identified both cognitive strengths "
                "and dimensions that remain insufficiently integrated."
            )

        elif strength_count > 0:
            opening = (
                "The committee identified a stable basis "
                "for the current analysis."
            )

        elif (
            weakness_count > 0
            or diagnosis_count > 0
        ):
            opening = (
                "The committee identified cognitive dimensions "
                "that require further integration or verification."
            )

        else:
            opening = (
                "The committee found no major cognitive imbalance."
            )

        if conflict_count > 0:
            middle = (
                "Some internal tensions remain unresolved, so the "
                "current interpretation should remain revisable."
            )

        elif hypothesis_count > 0:
            middle = (
                "Alternative hypotheses remain available and should "
                "be preserved before the interpretation stabilizes."
            )

        else:
            middle = (
                "The current interpretation should remain revisable."
            )

        if (
            isinstance(next_steps, list)
            and next_steps
        ):

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
