"""
DeDe - Image Generator

Generates images through the OpenAI Images API.

This module is independent from the main cognitive engine.
It can later be exposed as a callable DeDe tool.
"""

from __future__ import annotations

import base64
import os
from typing import Any

from openai import OpenAI


class ImageGenerator:
    """
    Generate one image from a natural-language description.
    """

    name = "image_generator"

    description = (
        "Generate one image from a natural-language description."
    )

    input_schema = {
        "prompt": {
            "type": "string",
            "required": True,
        },
        "size": {
            "type": "string",
            "required": False,
            "default": "1024x1024",
        },
        "quality": {
            "type": "string",
            "required": False,
            "default": "medium",
        },
        "transparent_background": {
            "type": "boolean",
            "required": False,
            "default": False,
        },
    }

    ALLOWED_SIZES = {
        "1024x1024",
        "1024x1536",
        "1536x1024",
    }

    ALLOWED_QUALITIES = {
        "low",
        "medium",
        "high",
    }

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        resolved_api_key = (
            api_key
            or os.environ.get("OPENAI_API_KEY")
        )

        if not resolved_api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing."
            )

        self.client = OpenAI(
            api_key=resolved_api_key,
        )

    def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "medium",
        transparent_background: bool = False,
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

        if size not in self.ALLOWED_SIZES:
            return {
                "tool": self.name,
                "status": "invalid_size",
                "error": f"Unsupported image size: {size}",
                "image_bytes": None,
            }

        if quality not in self.ALLOWED_QUALITIES:
            return {
                "tool": self.name,
                "status": "invalid_quality",
                "error": f"Unsupported image quality: {quality}",
                "image_bytes": None,
            }

        background = (
            "transparent"
            if transparent_background
            else "opaque"
        )

        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=cleaned_prompt,
                size=size,
                quality=quality,
                background=background,
                n=1,
            )

            if not response.data:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "The image provider returned "
                        "no generated image."
                    ),
                    "image_bytes": None,
                }

            encoded_image = response.data[0].b64_json

            if not encoded_image:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "The generated image contained "
                        "no image data."
                    ),
                    "image_bytes": None,
                }

            image_bytes = base64.b64decode(
                encoded_image
            )

            return {
                "tool": self.name,
                "status": "success",
                "provider": "openai",
                "model": "gpt-image-1",
                "prompt": cleaned_prompt,
                "size": size,
                "quality": quality,
                "background": background,
                "image_bytes": image_bytes,
                "mime_type": "image/png",
                "summary": (
                    "Image generated successfully."
                ),
            }

        except Exception as error:
            return {
                "tool": self.name,
                "status": "error",
                "error": str(error),
                "image_bytes": None,
            }

    def run(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "medium",
        transparent_background: bool = False,
    ) -> dict[str, Any]:
        """
        Standard ToolManager entry point.
        """

        return self.generate(
            prompt=prompt,
            size=size,
            quality=quality,
            transparent_background=transparent_background,
        )
