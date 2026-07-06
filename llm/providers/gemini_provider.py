"""
DeDe - Gemini LLM Provider
"""

from typing import Any
import os

from google import genai

from llm.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return {
                "provider": self.name,
                "status": "missing_api_key",
                "response": "",
                "summary": "Google Gemini API key is missing.",
            }

        client = genai.Client(
            api_key=api_key,
        )

        selected_model = model or "gemini-2.5-flash"

        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
        )

        return {
            "provider": self.name,
            "status": "success",
            "model": selected_model,
            "response": response.text or "",
            "summary": "Gemini response generated.",
        }
