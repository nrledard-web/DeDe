"""
DeDe - LLM Bridge

Provider-independent bridge between DeDe and external LLMs.

The bridge receives an LLM package prepared by DeDe and delegates
the call to the selected provider.
"""

from typing import Any

from llm.openai_bridge import OpenAIBridge


class LLMBridge:
    """
    Generic LLM bridge.

    It keeps DeDe independent from a specific LLM provider.
    """

    name = "llm_bridge"

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-5.5",
    ):
        self.provider = provider
        self.model = model

        self.providers = {
            "openai": OpenAIBridge(model=model),
        }

    def ask(
        self,
        llm_package: dict[str, Any],
        enabled: bool = False,
    ) -> dict[str, Any]:

        if not enabled:
            return {
                "bridge": self.name,
                "status": "disabled",
                "provider": self.provider,
                "model": self.model,
                "response": None,
                "summary": (
                    "LLM Bridge is ready but disabled. "
                    "No external model call was made."
                ),
            }

        provider_bridge = self.providers.get(self.provider)

        if not provider_bridge:
            return {
                "bridge": self.name,
                "status": "error",
                "provider": self.provider,
                "model": self.model,
                "response": None,
                "error": f"Unsupported LLM provider: {self.provider}",
            }

        return provider_bridge.ask(llm_package)
