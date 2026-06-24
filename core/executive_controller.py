"""
DeDe - Executive Controller

Dynamic cognitive decision layer.

The ExecutiveController decides which cognitive agents should be activated
depending on the user's input, context, urgency and cognitive needs.
"""


class ExecutiveController:
    """
    Decides which parts of DeDe's cognitive architecture should be activated.
    """

    def __init__(self):
        self.default_plan = [
            "intent_analysis",
            "memory_retrieval",
            "nous_integration",
            "response_synthesis",
        ]

    def create_plan(self, user_input: str, context: dict | None = None) -> dict:
        """
        Create a dynamic cognitive execution plan.
        """

        context = context or {}
        text = user_input.lower()

        plan = list(self.default_plan)
        reasons = []

        if self._requires_factual_grounding(text):
            plan.append("gnosis_analysis")
            reasons.append("The input appears to require factual grounding or verification.")

        if self._requires_doxa_analysis(text):
            plan.append("doxa_evaluation")
            reasons.append("The input may involve certainty, dogmatism, closure or overconfidence.")

        if self._requires_reduction_analysis(text):
            plan.append("reduction_detection")
            reasons.append("The input may contain assumptions, simplifications or hidden reductions.")

        if self._requires_nouscope_analysis(text):
            plan.append("nouscope_filtering")
            reasons.append("The input may involve cognitive filters, perception or interpretation patterns.")

        if self._requires_cognitive_support(text):
            plan.append("cognitive_recalibration")
            reasons.append("The input may require emotional support, reframing or cognitive recalibration.")

        plan = self._deduplicate(plan)

        return {
            "user_input": user_input,
            "context": context,
            "execution_plan": plan,
            "reasons": reasons,
            "status": "executive_plan_created",
        }

    def _requires_factual_grounding(self, text: str) -> bool:
        markers = [
            "fact",
            "source",
            "verify",
            "evidence",
            "proof",
            "true",
            "false",
            "history",
            "science",
            "law",
            "constitution",
            "research",
        ]
        return any(marker in text for marker in markers)

    def _requires_doxa_analysis(self, text: str) -> bool:
        markers = [
            "certainty",
            "dogma",
            "belief",
            "mecroyance",
            "mécroyance",
            "closure",
            "overconfidence",
            "ideology",
            "doxa",
            "consensus",
        ]
        return any(marker in text for marker in markers)

    def _requires_reduction_analysis(self, text: str) -> bool:
        markers = [
            "reduction",
            "assumption",
            "simplification",
            "frame",
            "model",
            "counting",
            "2+2",
            "real",
            "reality",
        ]
        return any(marker in text for marker in markers)

    def _requires_nouscope_analysis(self, text: str) -> bool:
        markers = [
            "filter",
            "perception",
            "bias",
            "interpretation",
            "nouscope",
            "cognitive filter",
            "mental model",
        ]
        return any(marker in text for marker in markers)

    def _requires_cognitive_support(self, text: str) -> bool:
        markers = [
            "lost",
            "sad",
            "afraid",
            "anxious",
            "stress",
            "death",
            "grief",
            "pain",
            "alone",
            "confused",
            "overwhelmed",
        ]
        return any(marker in text for marker in markers)

    def _deduplicate(self, items: list[str]) -> list[str]:
        """
        Preserve order while removing duplicates.
        """

        seen = set()
        result = []

        for item in items:
            if item not in seen:
                result.append(item)
                seen.add(item)

        return result
