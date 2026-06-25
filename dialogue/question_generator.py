"""
DeDe - Question Generator

Generates cognitive recalibration questions from detector results.
"""


class QuestionGenerator:
    """
    Generates questions that help restore revisability,
    explore alternatives and reduce cognitive closure.
    """

    def generate(self, report: dict) -> list[str]:
        detectors = report.get("detectors", {})
        mecroyance = detectors.get("mecroyance", {})
        scores = mecroyance.get("scores", {})

        questions = []

        if scores.get("mecroyance_risk", 0) > 0.50:
            questions.append(
                "What would make this interpretation less certain or more revisable?"
            )

        if scores.get("cognitive_closure", 0) > 0.25:
            questions.append(
                "Which alternative hypothesis could challenge this conclusion?"
            )

        if scores.get("overconfidence", 0) > 0.25:
            questions.append(
                "What evidence would be needed to justify this level of certainty?"
            )

        reduction = detectors.get("reduction", {})

        if reduction.get("forgotten_reduction", False):
            questions.append(
                "Which dimensions may have been reduced, simplified or left outside the frame?"
            )

        gnosis = scores.get("gnosis", 0)
        nous = scores.get("nous", 0)

        if gnosis < 0.40:
            questions.append(
                "What sources, facts or observations could strengthen the grounding of this claim?"
            )

        if nous < 0.40:
            questions.append(
                "How could the reasoning be connected more clearly to context, nuance and meaning?"
            )

        if not questions:
            questions.append(
                "What would be the most useful next question to deepen this reasoning?"
            )

        return questions
