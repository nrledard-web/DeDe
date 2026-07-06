"""
DeDe - LLM Provider Interface
"""

from typing import Any


class LLMProvider:
    name = "base_provider"

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError
