"""
DeDe - LLM JSON Schema

Expected structured cognitive response from external LLMs.
"""

LLM_RESPONSE_SCHEMA = {
    "summary": "",
    "confidence": 0.0,
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

Use exactly this schema:

{
  "summary": "string",
  "confidence": 0.0,
  "concepts": ["string"],
  "relations": [
    {
      "source": "string",
      "relation": "string",
      "target": "string"
    }
  ],
  "hypotheses": ["string"],
  "contradictions": ["string"],
  "questions": ["string"],
  "missing_dimensions": ["string"],
  "counterfactuals": ["string"],
  "recommendations": ["string"]
}
"""
