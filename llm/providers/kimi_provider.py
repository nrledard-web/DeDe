"""
DeDe - KIMI Provider

KIMI LLM provider through NVIDIA NIM.
"""

import os
from typing import Any

from openai import OpenAI


class KimiProvider:

    name = "kimi"

    def __init__(self) -> None:
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.default_model = "moonshotai/kimi-k2.6"

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:

        selected_model = model or self.default_model

        if not self.api_key:
            print(
                "KIMI PROVIDER: NVIDIA API key missing.",
                flush=True,
            )

            return {
                "provider": self.name,
                "status": "missing_api_key",
                "model": selected_model,
                "response": "",
                "summary": "NVIDIA API key is missing.",
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
                temperature=1,
                top_p=1,
                max_tokens=4096,
            )

            content = response.choices[0].message.content or ""

            return {
                "provider": self.name,
                "status": "success",
                "model": selected_model,
                "response": content,
                "summary": (
                    "KIMI response generated through NVIDIA "
                    f"with {selected_model}."
                ),
            }

        except Exception as error:
            print(
                "KIMI NVIDIA PROVIDER ERROR:",
                repr(error),
                flush=True,
            )

            return {
                "provider": self.name,
                "status": "error",
                "model": selected_model,
                "response": "",
                "summary": "KIMI NVIDIA request failed.",
                "error": str(error),
            }
