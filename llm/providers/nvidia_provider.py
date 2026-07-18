"""
DeDe - NVIDIA Provider

NVIDIA NIM LLM provider for DeDe.
"""

import os
from typing import Any

from openai import OpenAI


class NvidiaProvider:

    name = "nvidia"

    def __init__(self) -> None:
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.default_model = (
            "nvidia/nemotron-3-nano-30b-a3b"
        )

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:

        selected_model = model or self.default_model

        if not self.api_key:
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
                temperature=0.2,
                top_p=0.90,
                max_tokens=4096,
                extra_body={
                    "reasoning_budget": 2048,
                },
            )

            content = response.choices[0].message.content or ""

            return {
                "provider": self.name,
                "status": "success",
                "model": selected_model,
                "response": content,
                "summary": (
                    f"NVIDIA response generated with "
                    f"{selected_model}."
                ),
            }

        except Exception as error:
            return {
                "provider": self.name,
                "status": "error",
                "model": selected_model,
                "response": "",
                "summary": "NVIDIA request failed.",
                "error": str(error),
            }
