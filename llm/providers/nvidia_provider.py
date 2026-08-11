"""
DeDe - NVIDIA Provider

NVIDIA NIM LLM provider for DeDe.
"""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


class NvidiaProvider:

    name = "nvidia"

    def __init__(
        self,
    ) -> None:

        self.api_key = os.getenv(
            "NVIDIA_API_KEY"
        )

        self.base_url = (
            "https://integrate.api.nvidia.com/v1"
        )

        self.default_model = (
            "nvidia/nemotron-3-nano-30b-a3b"
        )

    def ask(
        self,
        prompt: str,
        model: str | None = None,
        fast_mode: bool = False,
    ) -> dict[str, Any]:

        selected_model = (
            model
            or self.default_model
        )

        if not self.api_key:
            return {
                "provider": self.name,
                "status": "missing_api_key",
                "model": selected_model,
                "response": "",
                "summary": (
                    "NVIDIA API key is missing."
                ),
            }

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            if fast_mode:
                response = (
                    client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        temperature=0.2,
                        top_p=1.0,
                        max_tokens=1024,
                        extra_body={
                            "top_k": 1,
                            "chat_template_kwargs": {
                                "enable_thinking": False,
                            },
                        },
                    )
                )

            else:
                response = (
                    client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        temperature=0.6,
                        top_p=0.95,
                        max_tokens=4096,
                        extra_body={
                            "reasoning_budget": 2048,
                        },
                    )
                )

            content = (
                response
                .choices[0]
                .message
                .content
                or ""
            )

            return {
                "provider": self.name,
                "status": "success",
                "model": selected_model,
                "response": content,
                "mode": (
                    "fast_instruct"
                    if fast_mode
                    else "reasoning"
                ),
                "summary": (
                    "NVIDIA response generated "
                    f"with {selected_model}."
                ),
            }

        except Exception as error:
            return {
                "provider": self.name,
                "status": "error",
                "model": selected_model,
                "response": "",
                "mode": (
                    "fast_instruct"
                    if fast_mode
                    else "reasoning"
                ),
                "summary": (
                    "NVIDIA request failed."
                ),
                "error": str(error),
            }
