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

        synthesis = self._build_simple_synthesis(extracted)

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

    def _build_simple_synthesis(
        self,
        extracted: list[dict[str, Any]],
    ) -> str:

        parts = []

        parts.append(
            "Synthèse du comité de raisonnement :"
        )

        for item in extracted:
            provider = item.get("provider", "unknown")
            response = item.get("response", "")

            parts.append(
                f"\n[{provider}]\n{response}"
            )

        parts.append(
            "\nLecture DeDe : plusieurs modèles ont été consultés. "
            "La réponse ci-dessus conserve leurs apports séparés afin de "
            "préserver la comparaison avant une synthèse plus avancée."
        )

        return "\n".join(parts)
