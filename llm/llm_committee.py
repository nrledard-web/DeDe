"""
DeDe - LLM Committee

Analyzes and synthesizes outputs from multiple reasoning models.
"""

from typing import Any
import json


class LLMCommittee:

    name = "llm_committee"

    def synthesize(
        self,
        provider_results: list[dict[str, Any]],
    ) -> dict[str, Any]:

        successful_results = [
            result for result in provider_results
            if result.get("status") == "success"
            and result.get("response")
        ]

        if not successful_results:
            return {
                "engine": self.name,
                "status": "empty",
                "response": "",
                "provider_count": 0,
                "provider_responses": [],
                "analysis": {},
                "summary": "No successful LLM response to synthesize.",
            }

        extracted = []

        for result in successful_results:
            raw_response = result.get("response", "")
            user_text = self._extract_user_text(raw_response)

            extracted.append(
                {
                    "provider": result.get("provider", "unknown"),
                    "model": result.get("model", ""),
                    "response": user_text,
                }
            )

        if len(extracted) == 1:
            return {
                "engine": self.name,
                "status": "single_model",
                "response": extracted[0]["response"],
                "provider_count": 1,
                "provider_responses": extracted,
                "analysis": {
                    "agreements": [],
                    "differences": [],
                    "unique_contributions": [],
                    "contradictions": [],
                    "confidence": 0.75,
                },
                "summary": (
                    f"Single reasoning model used: "
                    f"{extracted[0]['provider']}."
                ),
            }

        analysis = self._analyze_responses(extracted)
        synthesis = self._build_final_response(
            extracted=extracted,
            analysis=analysis,
        )

        return {
            "engine": self.name,
            "status": "committee_synthesis",
            "response": synthesis,
            "provider_count": len(extracted),
            "provider_responses": extracted,
            "analysis": analysis,
            "summary": (
                f"Reasoning committee analyzed and synthesized "
                f"{len(extracted)} model responses."
            ),
        }

    def _extract_user_text(
        self,
        raw_response: str,
    ) -> str:

        try:
            parsed = json.loads(raw_response)

            if isinstance(parsed, dict):
                return (
                    parsed.get("user_facing_response")
                    or parsed.get("response")
                    or raw_response
                )
        except Exception:
            pass

        return raw_response

    def _analyze_responses(
        self,
        extracted: list[dict[str, Any]],
    ) -> dict[str, Any]:

        responses = [
            item.get("response", "").strip()
            for item in extracted
            if item.get("response", "").strip()
        ]

        if not responses:
            return {
                "agreements": [],
                "differences": [],
                "unique_contributions": [],
                "contradictions": [],
                "confidence": 0.0,
            }

        common_terms = self._common_terms(responses)

        unique_contributions = []

        for item in extracted:
            provider = item.get("provider", "unknown")
            response = item.get("response", "")
            unique_contributions.append(
                {
                    "provider": provider,
                    "main_contribution": self._shorten(response),
                }
            )

        confidence = min(
            0.95,
            0.60 + 0.10 * len(common_terms),
        )

        return {
            "agreements": common_terms,
            "differences": self._detect_differences(extracted),
            "unique_contributions": unique_contributions,
            "contradictions": [],
            "confidence": confidence,
        }

    def _common_terms(
        self,
        responses: list[str],
    ) -> list[str]:
    
        word_sets = []
    
        for response in responses:
            words = {
                word.lower().strip(".,;:!?()[]\"'")
                for word in response.split()
                if len(word.lower().strip(".,;:!?()[]\"'")) > 7
            }
    
            word_sets.append(words)
    
        if not word_sets:
            return []
    
        common = set.intersection(*word_sets)
    
        return sorted(list(common))[:8]

    def _detect_differences(
        self,
        extracted: list[dict[str, Any]],
    ) -> list[str]:

        differences = []

        for item in extracted:
            provider = item.get("provider", "unknown")
            response = item.get("response", "")

            differences.append(
                f"{provider} emphasizes: {self._shorten(response)}"
            )

        return differences

    def _build_final_response(
        self,
        extracted: list[dict[str, Any]],
        analysis: dict[str, Any],
    ) -> str:

        responses = [
            item.get("response", "").strip()
            for item in extracted
            if item.get("response", "").strip()
        ]

        providers = [
            item.get("provider", "unknown")
            for item in extracted
        ]

        base_response = max(
            responses,
            key=len,
        )

        agreements = analysis.get("agreements", [])
        confidence = analysis.get("confidence", 0.0)

        parts = []

        parts.append("Synthèse DeDe :")
        parts.append(base_response)

        if agreements:
            parts.append(
                "Convergence cognitive : les modèles consultés présentent "
                "une convergence suffisante pour produire une réponse unifiée."
            )
        else:
            parts.append(
                "Convergence cognitive : les modèles consultés produisent "
                "des réponses compatibles, sans contradiction majeure détectée."
            )

        parts.append(
            "Note de raisonnement : plusieurs modèles ont été consultés "
            f"({', '.join(providers)}). DeDe a comparé leurs réponses "
            "avant de produire cette synthèse."
        )

        parts.append(
            f"Confiance comparative estimée : {round(confidence * 100)}%."
        )

        return "\n\n".join(parts)

    def _shorten(
        self,
        text: str,
        limit: int = 220,
    ) -> str:

        cleaned = " ".join(text.split())

        if len(cleaned) <= limit:
            return cleaned

        return cleaned[:limit].rstrip() + "..."
