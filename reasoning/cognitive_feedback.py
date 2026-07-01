"""
DeDe - Cognitive Feedback

Extracts structured cognitive feedback from an LLM response.

This component prepares the future feedback loop:
LLM Response
    ↓
Structured cognitive feedback
    ↓
Future graph enrichment
"""

from typing import Any


class CognitiveFeedback:

    name = "cognitive_feedback"

    def analyze(
        self,
        llm_response: str | None,
        parsed_json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Preferred path: structured JSON from the LLM
        # --------------------------------------------------
        if parsed_json:
            return {
                "engine": self.name,
                "status": "ready_from_json",
                "new_concepts": parsed_json.get("concepts", []),
                "new_relations": parsed_json.get("relations", []),
                "new_hypotheses": parsed_json.get("hypotheses", []),
                "new_questions": parsed_json.get("questions", []),
                "new_missing_dimensions": parsed_json.get(
                    "missing_dimensions",
                    [],
                ),
                "new_counterfactuals": parsed_json.get(
                    "counterfactuals",
                    [],
                ),
                "confidence": parsed_json.get("confidence", 0.0),
                "summary": parsed_json.get(
                    "summary",
                    "Structured LLM feedback extracted from JSON.",
                ),
                "recommendations": parsed_json.get("recommendations", []),
                "contradictions": parsed_json.get("contradictions", []),
                "source": "llm_json",
            }

        # --------------------------------------------------
        # Fallback path: no LLM response available
        # --------------------------------------------------
        if not llm_response:
            return {
                "engine": self.name,
                "status": "no_llm_response",
                "new_concepts": [],
                "new_relations": [],
                "new_hypotheses": [],
                "new_questions": [],
                "new_missing_dimensions": [],
                "new_counterfactuals": [],
                "confidence": 0.0,
                "summary": "No LLM response available for feedback extraction.",
                "recommendations": [],
                "contradictions": [],
                "source": "none",
            }

        # --------------------------------------------------
        # Fallback path: heuristic extraction from text
        # --------------------------------------------------
        text = llm_response.lower()

        new_concepts = self._extract_concepts(text)
        new_hypotheses = self._extract_hypotheses(llm_response)
        new_questions = self._extract_questions(llm_response)
        new_missing_dimensions = self._extract_missing_dimensions(llm_response)
        new_counterfactuals = self._extract_counterfactuals(llm_response)

        new_relations = self._build_relations(new_concepts)

        confidence = self._estimate_confidence(
            new_concepts,
            new_hypotheses,
            new_missing_dimensions,
            new_counterfactuals,
        )

        return {
            "engine": self.name,
            "status": "ready_from_text",
            "new_concepts": new_concepts,
            "new_relations": new_relations,
            "new_hypotheses": new_hypotheses,
            "new_questions": new_questions,
            "new_missing_dimensions": new_missing_dimensions,
            "new_counterfactuals": new_counterfactuals,
            "confidence": confidence,
            "summary": self._build_summary(
                new_concepts,
                new_relations,
                new_hypotheses,
                new_missing_dimensions,
                new_counterfactuals,
                confidence,
            ),
            "recommendations": [],
            "contradictions": [],
            "source": "llm_text_fallback",
        }

    def _extract_concepts(
        self,
        text: str,
    ) -> list[str]:

        candidates = [
            "certainty",
            "understanding",
            "reduction",
            "closure",
            "revisability",
            "cognitive_filter",
            "grounding",
            "belief",
            "belief_state",
            "misconfiguration",
            "social_reinforcement",
            "authority",
            "experience",
            "integration",
        ]

        concepts = []

        for concept in candidates:
            marker = concept.replace("_", " ")

            if marker in text or concept in text:
                concepts.append(concept)

        return self._unique(concepts)

    def _extract_hypotheses(
        self,
        text: str,
    ) -> list[str]:

        hypotheses = []

        markers = [
            "may ",
            "might ",
            "could ",
            "seems to",
            "appears to",
        ]

        for sentence in self._sentences(text):
            lowered = sentence.lower()

            if any(marker in lowered for marker in markers):
                hypotheses.append(sentence.strip())

        return self._unique(hypotheses[:6])

    def _extract_questions(
        self,
        text: str,
    ) -> list[str]:

        questions = []

        for sentence in self._sentences(text):
            if "?" in sentence:
                questions.append(sentence.strip())

        return self._unique(questions[:6])

    def _extract_missing_dimensions(
        self,
        text: str,
    ) -> list[str]:

        missing = []

        markers = [
            "missing dimensions",
            "what grounds",
            "is the reduction",
            "which cognitive filters",
            "remain important",
        ]

        for sentence in self._sentences(text):
            lowered = sentence.lower()

            if any(marker in lowered for marker in markers):
                missing.append(sentence.strip())

        return self._unique(missing[:6])

    def _extract_counterfactuals(
        self,
        text: str,
    ) -> list[str]:

        counterfactuals = []

        markers = [
            "if ",
            "unless ",
            "would ",
            "could become",
        ]

        for sentence in self._sentences(text):
            lowered = sentence.lower()

            if any(marker in lowered for marker in markers):
                counterfactuals.append(sentence.strip())

        return self._unique(counterfactuals[:6])

    def _build_relations(
        self,
        concepts: list[str],
    ) -> list[dict[str, Any]]:

        relations = []

        if "certainty" in concepts and "understanding" in concepts:
            relations.append(
                {
                    "source": "certainty",
                    "relation": "may_exceed",
                    "target": "understanding",
                    "source_layer": "llm_feedback",
                }
            )

        if "reduction" in concepts and "closure" in concepts:
            relations.append(
                {
                    "source": "reduction",
                    "relation": "may_produce",
                    "target": "closure",
                    "source_layer": "llm_feedback",
                }
            )

        if "revisability" in concepts and "closure" in concepts:
            relations.append(
                {
                    "source": "revisability",
                    "relation": "may_prevent",
                    "target": "closure",
                    "source_layer": "llm_feedback",
                }
            )

        if "cognitive_filter" in concepts and "understanding" in concepts:
            relations.append(
                {
                    "source": "cognitive_filter",
                    "relation": "may_shape",
                    "target": "understanding",
                    "source_layer": "llm_feedback",
                }
            )

        return relations

    def _estimate_confidence(
        self,
        concepts: list[str],
        hypotheses: list[str],
        missing_dimensions: list[str],
        counterfactuals: list[str],
    ) -> float:

        score = 0.0

        score += min(len(concepts) * 0.05, 0.35)
        score += min(len(hypotheses) * 0.08, 0.25)
        score += min(len(missing_dimensions) * 0.08, 0.20)
        score += min(len(counterfactuals) * 0.05, 0.20)

        return round(min(score, 1.0), 3)

    def _build_summary(
        self,
        concepts: list[str],
        relations: list[dict[str, Any]],
        hypotheses: list[str],
        missing_dimensions: list[str],
        counterfactuals: list[str],
        confidence: float,
    ) -> str:

        return (
            "LLM cognitive feedback extracted: "
            f"{len(concepts)} concepts, "
            f"{len(relations)} relations, "
            f"{len(hypotheses)} hypotheses, "
            f"{len(missing_dimensions)} missing dimensions, "
            f"{len(counterfactuals)} counterfactuals. "
            f"Confidence: {round(confidence * 100)}%."
        )

    def _sentences(
        self,
        text: str,
    ) -> list[str]:

        normalized = text.replace("\n", " ")
        parts = normalized.split(".")

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:

        seen = set()
        unique_values = []

        for value in values:
            if value not in seen:
                seen.add(value)
                unique_values.append(value)

        return unique_values
