"""
DeDe - Mistral Provider

Mistral AI LLM provider for DeDe.
"""

import os
from typing import Any


try:
    from mistralai import Mistral
except ImportError:
    from mistralai.client import Mistral


class MistralProvider:

    name = "mistral"

    def __init__(self) -> None:
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.default_model = "mistral-large-latest"

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:

        if not self.api_key:
            return {
                "provider": self.name,
                "status": "missing_api_key",
                "model": model or self.default_model,
                "response": "",
                "summary": "Mistral API key is missing.",
            }

        selected_model = model or self.default_model

        try:
            client = Mistral(api_key=self.api_key)

            response = client.chat.complete(
                model=selected_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            content = response.choices[0].message.content

            return {
                "provider": self.name,
                "status": "success",
                "model": selected_model,
                "response": content,
                "summary": f"Mistral response generated with {selected_model}.",
            }

        except Exception as error:
            return {
                "provider": self.name,
                "status": "error",
                "model": selected_model,
                "response": "",
                "summary": "Mistral request failed.",
                "error": str(error),
            }
