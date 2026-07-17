"""
DeDe - KIMI Provider

Moonshot AI KIMI LLM provider for DeDe.
"""

import os
from typing import Any

from openai import OpenAI


class KimiProvider:

    name = "kimi"

    def __init__(self) -> None:
        self.api_key = os.getenv("KIMI_API_KEY")
        self.base_url = "https://api.moonshot.ai/v1"
        self.default_model = "kimi-k3"

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:

        selected_model = model or self.default_model

        if not self.api_key:
            print(
                "KIMI PROVIDER: API key missing.",
                flush=True,
            )

            return {
                "provider": self.name,
                "status": "missing_api_key",
                "model": selected_model,
                "response": "",
                "summary": "KIMI API key is missing.",
            }

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=4096,
            )

            content = response.choices[0].message.content or ""

            return {
                "provider": self.name,
                "status": "success",
                "model": selected_model,
                "response": content,
                "summary": (
                    f"KIMI response generated with "
                    f"{selected_model}."
                ),
            }

        except Exception as error:
            print(
                "KIMI PROVIDER ERROR:",
                repr(error),
                flush=True,
            )

            return {
                "provider": self.name,
                "status": "error",
                "model": selected_model,
                "response": "",
                "summary": "KIMI request failed.",
                "error": str(error),
            }
