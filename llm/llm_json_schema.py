"""
DeDe - LLM JSON Schema

Expected structured cognitive response from an external LLM.

The LLM supports DeDe's reasoning but does not replace DeDe.
It produces both:
- a natural user-facing response
- a structured cognitive analysis
"""

LLM_RESPONSE_SCHEMA = {
    "user_facing_response": "",
    "summary": "",
    "confidence": 0.0,
    "language": "",
    "concepts": [],
    "relations": [],
    "hypotheses": [],
    "contradictions": [],
    "questions": [],
    "missing_dimensions": [],
    "counterfactuals": [],
    "recommendations": [],
}


def build_json_instruction() -> str:
    return """
Return ONLY valid JSON.

Do not use markdown.
Do not add explanations outside the JSON.
Do not wrap the JSON in code fences.

The field "user_facing_response" must contain the natural response
that DeDe should say to the user.

The field "summary" must contain a short internal cognitive summary,
not intended to be shown directly to the user.

The language of "user_facing_response" MUST match the language used
by the user in the current message.

Use exactly this schema:

{
  "user_facing_response": "string",
  "summary": "string",
  "confidence": 0.0,
  "language": "string",
  "concepts": [
    "string"
  ],
  "relations": [
    {
      "source": "string",
      "relation": "string",
      "target": "string"
    }
  ],
  "hypotheses": [
    "string"
  ],
  "contradictions": [
    "string"
  ],
  "questions": [
    "string"
  ],
  "missing_dimensions": [
    "string"
  ],
  "counterfactuals": [
    "string"
  ],
  "recommendations": [
    "string"
  ]
}
"""
