"""
DeDe - Hugging Face Video Generator

Generates short AI videos through Hugging Face
Inference Providers.
"""

from __future__ import annotations

import os
from typing import Any

from huggingface_hub import (
    InferenceClient,
)


class HuggingFaceVideoGenerator:
    """
    Generate one short video through Hugging Face.
    """

    name = "huggingface_video_generator"

    description = (
        "Generate one short AI video through "
        "Hugging Face Inference Providers."
    )

    model = "Wan-AI/Wan2.2-TI2V-5B"

    input_schema = {
        "prompt": {
            "type": "string",
            "required": True,
        },
    }

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:

        self.api_key = (
            api_key
            or os.environ.get(
                "HF_TOKEN"
            )
        )

        if not self.api_key:
            raise ValueError(
                "HF_TOKEN is missing."
            )

        self.client = InferenceClient(
            provider="wavespeed",
            api_key=self.api_key,
        )

    def generate(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """
        Generate a video and return its binary content.
        """

        cleaned_prompt = str(
            prompt or ""
        ).strip()

        if not cleaned_prompt:
            return {
                "tool": self.name,
                "status": "invalid_request",
                "error": (
                    "The video description is empty."
                ),
                "video_bytes": None,
            }

        try:
            video = self.client.text_to_video(
                cleaned_prompt,
                model=self.model,
            )

            if not video:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "Hugging Face returned "
                        "no generated video."
                    ),
                    "video_bytes": None,
                }

            if isinstance(
                video,
                bytes,
            ):
                video_bytes = video

            elif isinstance(
                video,
                bytearray,
            ):
                video_bytes = bytes(
                    video
                )

            elif hasattr(
                video,
                "read",
            ):
                video_bytes = video.read()

            else:
                return {
                    "tool": self.name,
                    "status": "invalid_response",
                    "error": (
                        "Hugging Face returned an "
                        "unsupported video format."
                    ),
                    "video_bytes": None,
                }

            if not video_bytes:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "The generated video "
                        "contained no data."
                    ),
                    "video_bytes": None,
                }

            return {
                "tool": self.name,
                "status": "success",
                "provider": "huggingface",
                "model": self.model,
                "prompt": cleaned_prompt,
                "video_bytes": video_bytes,
                "mime_type": "video/mp4",
                "summary": (
                    "Video generated successfully "
                    "through Hugging Face."
                ),
            }

        except Exception as error:
            error_message = str(
                error
            )

            lowered_error = (
                error_message.lower()
            )

            if (
                "credit" in lowered_error
                or "balance" in lowered_error
                or "payment" in lowered_error
                or "402" in lowered_error
            ):
                status = "insufficient_credits"

                user_error = (
                    "The monthly Hugging Face "
                    "inference credits are insufficient "
                    "or have already been consumed. "
                    f"{error_message}"
                )

            elif (
                "unauthorized" in lowered_error
                or "authentication" in lowered_error
                or "401" in lowered_error
                or "403" in lowered_error
            ):
                status = "authentication_error"

                user_error = (
                    "The Hugging Face token is invalid "
                    "or does not have Inference Providers "
                    "permission. "
                    f"{error_message}"
                )

            elif (
                "timeout" in lowered_error
                or "timed out" in lowered_error
            ):
                status = "timeout"

                user_error = (
                    "Hugging Face video generation "
                    "timed out. "
                    f"{error_message}"
                )

            else:
                status = "error"
                user_error = error_message

            return {
                "tool": self.name,
                "status": status,
                "error": user_error,
                "video_bytes": None,
            }

    def run(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """
        Standard ToolManager entry point.
        """

        return self.generate(
            prompt=prompt,
        )
