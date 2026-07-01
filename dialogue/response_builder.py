"""
DeDe - Response Builder

Builds a clear user-facing answer from DeDe's cognitive report.
"""

from typing import Any


class ResponseBuilder:

    name = "response_builder"

    def build(
        self,
        report: dict[str, Any],
    ) -> dict[str, Any]:

        knowledge = report.get("knowledge", {})
        dialogue_decision = report.get("dialogue_decision", {})
        cognitive_feedback = report.get("cognitive_feedback", {})
        llm_bridge_response = report.get("llm_bridge_response", {})
        summary = report.get("summary", {})

        answer_parts = []

        if knowledge.get("found"):
            answer_parts.append(knowledge.get("answer", ""))

        llm_json = llm_bridge_response.get("parsed_json")

        if llm_json and llm_json.get("summary"):
            answer_parts.append(llm_json["summary"])

        if not answer_parts:
            answer_parts.append(summary.get("diagnosis", ""))

        final_answer = "\n\n".join(
            part for part in answer_parts if part
        )

        if not final_answer:
            final_answer = (
                "DeDe has analyzed the input, but no clear user-facing "
                "answer could be generated yet."
            )

        follow_up_question = self._build_follow_up_question(
            dialogue_decision,
            cognitive_feedback,
        )

        return {
            "builder": self.name,
            "status": "ready",
            "conversation_mode": dialogue_decision.get(
                "strategy",
                "direct_answer",
            ),
            "final_answer": final_answer,
            "follow_up_question": follow_up_question,
            "used_llm": llm_bridge_response.get("status") == "success",
            "used_local_knowledge": knowledge.get("found", False),
            "summary": "User-facing response built from DeDe report.",
        }

    def _build_follow_up_question(
        self,
        dialogue_decision: dict[str, Any],
        cognitive_feedback: dict[str, Any],
    ) -> str | None:

        questions = cognitive_feedback.get("new_questions", [])

        if questions:
            return questions[0]

        missing_dimensions = cognitive_feedback.get(
            "new_missing_dimensions",
            [],
        )

        if missing_dimensions:
            return (
                "Souhaites-tu préciser cette dimension : "
                f"{missing_dimensions[0]}"
            )

        if dialogue_decision.get("needs_clarification"):
            return (
                "Souhaites-tu une réponse courte, technique, "
                "philosophique ou orientée application ?"
            )

        return None
