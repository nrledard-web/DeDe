"""
Committee Reasoner

Interprets the cognitive committee as a whole and produces
cross-agent diagnoses, hypotheses, strengths, weaknesses
and recommended next steps.
"""


class CommitteeReasoner:

    def reason(
        self,
        workspace,
        committee,
    ):
        diagnoses = []
        hypotheses = []
        strengths = []
        weaknesses = []
        conflicts = []
        recommended_next_steps = []

        knowledge = workspace.find("Knowledge")
        nous = workspace.find("Nous")
        doxa = workspace.find("Doxa")
        reduction = workspace.find("Reduction")
        nouscope = workspace.find("NOUSCOPE")
        therapy = workspace.find("Cognitive Therapy")

        if knowledge and knowledge.confidence > 0.80:
            strengths.append(
                "Knowledge basis is present."
            )

        if nous and nous.confidence < 0.50:
            weaknesses.append(
                "Integrated understanding remains weak."
            )

        if doxa and nous and doxa.confidence > nous.confidence:
            diagnoses.append(
                "Certainty currently exceeds integrated understanding."
            )
            hypotheses.append(
                "The cognitive structure may be stabilizing before full conceptual integration."
            )

        if knowledge and nous and knowledge.confidence > 0.80 and nous.confidence < 0.50:
            diagnoses.append(
                "Knowledge is available but remains weakly integrated."
            )
            recommended_next_steps.append(
                "Strengthen conceptual explanation and contextual integration."
            )

        if doxa and reduction and doxa.confidence > 0.60 and reduction.confidence > 0.60:
            diagnoses.append(
                "Possible mecroyance pattern: certainty and reduction reinforce each other."
            )
            conflicts.append(
                "Doxa and Reduction jointly increase closure pressure."
            )

        if reduction and nouscope and reduction.confidence > 0.50 and nouscope.confidence > 0.50:
            diagnoses.append(
                "Cognitive filters may amplify conceptual reductions."
            )
            hypotheses.append(
                "Interpretation may be shaped by a prior cognitive frame."
            )

        if therapy and therapy.confidence > 0.70:
            diagnoses.append(
                "The committee recommends cognitive recalibration."
            )
            recommended_next_steps.append(
                "Apply revision strategies proposed by Cognitive Therapy."
            )

        if not diagnoses:
            diagnoses.append(
                "No major cognitive imbalance detected by the committee."
            )

        if not recommended_next_steps:
            recommended_next_steps.append(
                "Maintain revisability and continue monitoring committee signals."
            )

        return {
            "diagnoses": sorted(set(diagnoses)),
            "hypotheses": sorted(set(hypotheses)),
            "strengths": sorted(set(strengths)),
            "weaknesses": sorted(set(weaknesses)),
            "conflicts": sorted(set(conflicts)),
            "recommended_next_steps": sorted(set(recommended_next_steps)),
        }
