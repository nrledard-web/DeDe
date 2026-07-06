"""
DeDe - LLM Committee

Synthesizes outputs from multiple reasoning models.
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
                "summary": (
                    f"Single reasoning model used: "
                    f"{extracted[0]['provider']}."
                ),
            }

        synthesis = self._build_dede_synthesis(extracted)

        return {
            "engine": self.name,
            "status": "committee_synthesis",
            "response": synthesis,
            "provider_count": len(extracted),
            "provider_responses": extracted,
            "summary": (
                f"Reasoning committee synthesized "
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

    def _build_dede_synthesis(
        self,
        extracted: list[dict[str, Any]],
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

        if not responses:
            return ""

        combined_text = "\n\n".join(responses)

        synthesis = []

        synthesis.append(
            "Synthèse DeDe :"
        )

        synthesis.append(
            self._build_main_synthesis(combined_text)
        )

        synthesis.append(
            self._build_model_note(providers)
        )

        return "\n\n".join(
            part for part in synthesis if part
        )

    def _build_main_synthesis(
        self,
        combined_text: str,
    ) -> str:

        # First simple version:
        # keep the strongest shared answer while removing the visible
        # separation between models.

        paragraphs = [
            paragraph.strip()
            for paragraph in combined_text.split("\n")
            if paragraph.strip()
        ]

        if not paragraphs:
            return combined_text.strip()

        # Prefer the most complete paragraph as the base synthesis.
        base = max(
            paragraphs,
            key=len,
        )

        return base

    def _build_model_note(
        self,
        providers: list[str],
    ) -> str:

        clean_providers = ", ".join(
            provider for provider in providers
            if provider
        )

        return (
            f"Note de raisonnement : cette réponse a été construite "
            f"à partir de plusieurs modèles consultés "
            f"({clean_providers}). DeDe conserve cette comparaison "
            f"comme matière de raisonnement, sans déléguer son rôle "
            f"de synthèse à un seul modèle."
        )
