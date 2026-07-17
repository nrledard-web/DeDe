"""
DeDe - Cloudflare Image Generator

Generates images through Cloudflare Workers AI.

This module is independent from the OpenAI image generator
and from the main cognitive engine.
"""

from __future__ import annotations

import base64
import os
import random
from typing import Any

import requests


class CloudflareImageGenerator:
    """
    Generate one image through Cloudflare Workers AI.
    """

    name = "cloudflare_image_generator"

    description = (
        "Generate one image through Cloudflare Workers AI."
    )

    model = "@cf/black-forest-labs/flux-1-schnell"

    input_schema = {
        "prompt": {
            "type": "string",
            "required": True,
        },
        "steps": {
            "type": "integer",
            "required": False,
            "default": 4,
        },
        "seed": {
            "type": "integer",
            "required": False,
        },
    }

    MIN_STEPS = 1
    MAX_STEPS = 8

    def __init__(
        self,
        account_id: str | None = None,
        api_token: str | None = None,
    ) -> None:

        self.account_id = (
            account_id
            or os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        )

        self.api_token = (
            api_token
            or os.environ.get("CLOUDFLARE_API_TOKEN")
        )

        if not self.account_id:
            raise ValueError(
                "CLOUDFLARE_ACCOUNT_ID is missing."
            )

        if not self.api_token:
            raise ValueError(
                "CLOUDFLARE_API_TOKEN is missing."
            )

        self.endpoint = (
            "https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

    def generate(
        self,
        prompt: str,
        steps: int = 4,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate an image and return its binary content.
        """

        cleaned_prompt = str(
            prompt or ""
        ).strip()

        if not cleaned_prompt:
            return {
                "tool": self.name,
                "status": "invalid_request",
                "error": "The image description is empty.",
                "image_bytes": None,
            }

        try:
            resolved_steps = int(steps)
        except (TypeError, ValueError):
            resolved_steps = 4

        resolved_steps = max(
            self.MIN_STEPS,
            min(resolved_steps, self.MAX_STEPS),
        )

        if seed is None:
            resolved_seed = random.randint(
                1,
                2_147_483_647,
            )
        else:
            try:
                resolved_seed = int(seed)
            except (TypeError, ValueError):
                resolved_seed = random.randint(
                    1,
                    2_147_483_647,
                )

        payload = {
            "prompt": cleaned_prompt,
            "steps": resolved_steps,
            "seed": resolved_seed,
        }

        headers = {
            "Authorization": (
                f"Bearer {self.api_token}"
            ),
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

            response_data = response.json()

            if not response_data.get("success"):
                return {
                    "tool": self.name,
                    "status": "provider_error",
                    "error": response_data.get(
                        "errors",
                        "Cloudflare returned an error.",
                    ),
                    "image_bytes": None,
                }

            result = response_data.get(
                "result",
                {},
            )

            encoded_image = result.get(
                "image"
            )

            if not encoded_image:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "Cloudflare returned no image data."
                    ),
                    "image_bytes": None,
                }

            image_bytes = base64.b64decode(
                encoded_image
            )

            return {
                "tool": self.name,
                "status": "success",
                "provider": "cloudflare",
                "model": self.model,
                "prompt": cleaned_prompt,
                "steps": resolved_steps,
                "seed": resolved_seed,
                "image_bytes": image_bytes,
                "mime_type": "image/jpeg",
                "summary": (
                    "Image generated successfully "
                    "through Cloudflare Workers AI."
                ),
            }

        except requests.Timeout:
            return {
                "tool": self.name,
                "status": "timeout",
                "error": (
                    "Cloudflare image generation timed out."
                ),
                "image_bytes": None,
            }

        except requests.RequestException as error:
            return {
                "tool": self.name,
                "status": "error",
                "error": str(error),
                "image_bytes": None,
            }

        except (
            ValueError,
            KeyError,
            TypeError,
            base64.binascii.Error,
        ) as error:
            return {
                "tool": self.name,
                "status": "invalid_response",
                "error": str(error),
                "image_bytes": None,
            }

    def run(
        self,
        prompt: str,
        steps: int = 4,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Standard ToolManager entry point.
        """

        return self.generate(
            prompt=prompt,
            steps=steps,
            seed=seed,
        )
