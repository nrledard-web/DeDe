"""
Revision Agent

Uses detector results to decide whether a response
should be improved before being returned.
"""


class RevisionAgent:

    def revise(
        self,
        answer: str,
        analysis: dict,
    ) -> dict:

        vector = analysis["cognitive_vector"]

        improvements = []

        if vector["gnosis"] < 0.45:
            improvements.append(
                "Increase factual grounding."
            )

        if vector["nous"] < 0.45:
            improvements.append(
                "Add conceptual explanation."
            )

        if vector["revisability"] < 0.50:
            improvements.append(
                "Increase nuance."
            )

        if vector["reduction"] > 0.60:
            improvements.append(
                "Reduce conceptual reduction."
            )

        return {
            "needs_revision": len(improvements) > 0,
            "suggestions": improvements,
        }
