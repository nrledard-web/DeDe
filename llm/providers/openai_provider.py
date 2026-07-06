"""
DeDe - OpenAI LLM Provider
"""

from typing import Any
import os
from openai import OpenAI

from llm.llm_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return {
                "provider": self.name,
                "status": "missing_api_key",
                "response": "",
                "summary": "OpenAI API key is missing.",
            }

        client = OpenAI(api_key=api_key)

        selected_model = model or "gpt-4o-mini"

        response = client.responses.create(
            model=selected_model,
            input=prompt,
        )

        return {
            "provider": self.name,
            "status": "success",
            "model": selected_model,
            "response": response.output_text,
            "summary": "OpenAI response generated.",
        }
