"""
DeDe - LLM Engine

Reasoning model orchestrator.
"""

from typing import Any

from llm.llm_profile import LLMProfile
from llm.providers.openai_provider import OpenAIProvider
from llm.providers.gemini_provider import GeminiProvider
from llm.llm_committee import LLMCommittee
from llm.providers.mistral_provider import MistralProvider

class LLMEngine:
    name = "llm_engine"

    def __init__(self) -> None:
        self.profile_engine = LLMProfile()

        self.providers = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "mistral": MistralProvider(),
        }

        self.committee = LLMCommittee()

    def ask(
        self,
        prompt: str,
        profile: str = "fast",
        providers: list[str] | None = None,
        model: str | None = None,
        enabled: bool = False,
    ) -> dict[str, Any]:

        if not enabled:
            return {
                "engine": self.name,
                "status": "disabled",
                "profile": profile,
                "providers": [],
                "provider_results": [],
                "committee": {},
                "response": "",
                "summary": "LLM reasoning disabled.",
            }

        profile_data = None

        if providers:
            selected_providers = providers
        else:
            profile_data = self.profile_engine.resolve(profile)
            selected_providers = profile_data["active_providers"]

        provider_results = []

        for provider_name in selected_providers:
            provider = self.providers.get(provider_name)

            if not provider:
                provider_results.append(
                    {
                        "provider": provider_name,
                        "status": "planned_not_connected",
                        "response": "",
                        "summary": (
                            f"LLM provider '{provider_name}' is planned "
                            "but not connected yet."
                        ),
                    }
                )
                continue

            try:
                result = provider.ask(
                    prompt=prompt,
                    model=model,
                )
            except Exception as error:
                result = {
                    "provider": provider_name,
                    "status": "error",
                    "response": "",
                    "summary": f"{provider_name} failed.",
                    "error": str(error),
                }

            provider_results.append(result)

        committee_result = self.committee.synthesize(
            provider_results
        )

        return {
            "engine": self.name,
            "status": committee_result.get("status", "empty"),
            "profile": profile_data,
            "providers": selected_providers,
            "provider_results": provider_results,
            "committee": committee_result,
            "response": committee_result.get("response", ""),
            "summary": committee_result.get("summary", ""),
        }
