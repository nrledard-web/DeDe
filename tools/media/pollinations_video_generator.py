"""
DeDe - Pollinations Video Generator

Generates MP4 videos through the Pollinations unified API.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import requests


class PollinationsVideoGenerator:
    """
    Generate one short video from a text description.
    """

    name = "pollinations_video_generator"

    description = (
        "Generate one short MP4 video through Pollinations."
    )

    input_schema = {
        "prompt": {
            "type": "string",
            "required": True,
        },
        "model": {
            "type": "string",
            "required": False,
            "default": "wan-fast",
        },
        "duration": {
            "type": "integer",
            "required": False,
            "default": 5,
        },
        "aspect_ratio": {
            "type": "string",
            "required": False,
            "default": "9:16",
        },
        "audio": {
            "type": "boolean",
            "required": False,
            "default": False,
        },
    }

    ALLOWED_MODELS = {
        "wan-fast",
        "seedance-2.0",
        "veo",
    }

    ALLOWED_ASPECT_RATIOS = {
        "16:9",
        "9:16",
    }

    MODEL_DURATIONS = {
        "wan-fast": {
            5,
            10,
        },
        "seedance-2.0": {
            4,
            5,
            8,
            10,
            15,
        },
        "veo": {
            4,
            6,
            8,
        },
    }

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:

        self.api_key = (
            api_key
            or os.environ.get(
                "POLLINATIONS_API_KEY"
            )
        )

        if not self.api_key:
            raise ValueError(
                "POLLINATIONS_API_KEY is missing."
            )

        self.endpoint = (
            "https://gen.pollinations.ai/video"
        )

    def generate(
        self,
        prompt: str,
        model: str = "wan-fast",
        duration: int = 5,
        aspect_ratio: str = "9:16",
        audio: bool = False,
    ) -> dict[str, Any]:
        """
        Generate a video and return its MP4 content.
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

        cleaned_model = str(
            model or ""
        ).strip()

        if cleaned_model not in self.ALLOWED_MODELS:
            return {
                "tool": self.name,
                "status": "invalid_model",
                "error": (
                    "Unsupported video model: "
                    f"{cleaned_model}"
                ),
                "video_bytes": None,
            }

        if (
            aspect_ratio
            not in self.ALLOWED_ASPECT_RATIOS
        ):
            return {
                "tool": self.name,
                "status": "invalid_aspect_ratio",
                "error": (
                    "Unsupported video format: "
                    f"{aspect_ratio}"
                ),
                "video_bytes": None,
            }

        try:
            resolved_duration = int(
                duration
            )

        except (
            TypeError,
            ValueError,
        ):
            resolved_duration = 5

        allowed_durations = (
            self.MODEL_DURATIONS[
                cleaned_model
            ]
        )

        if (
            resolved_duration
            not in allowed_durations
        ):
            return {
                "tool": self.name,
                "status": "invalid_duration",
                "error": (
                    "Unsupported duration for "
                    f"{cleaned_model}: "
                    f"{resolved_duration} seconds."
                ),
                "video_bytes": None,
            }

        encoded_prompt = quote(
            cleaned_prompt,
            safe="",
        )

        url = (
            f"{self.endpoint}/"
            f"{encoded_prompt}"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Accept": "video/mp4",
        }

        params = {
            "model": cleaned_model,
            "duration": resolved_duration,
            "aspectRatio": aspect_ratio,
            "audio": str(
                bool(audio)
            ).lower(),
            "safe": "true",
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=(
                    30,
                    600,
                ),
            )

            response.raise_for_status()

            content_type = (
                response.headers.get(
                    "Content-Type",
                    "",
                ).lower()
            )

            if "video/" not in content_type:
                error_message = (
                    response.text[:500]
                )

                return {
                    "tool": self.name,
                    "status": "invalid_response",
                    "error": (
                        "Pollinations returned no "
                        "MP4 video. "
                        f"{error_message}"
                    ),
                    "video_bytes": None,
                }

            if not response.content:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "Pollinations returned "
                        "an empty video."
                    ),
                    "video_bytes": None,
                }

            return {
                "tool": self.name,
                "status": "success",
                "provider": "pollinations",
                "model": cleaned_model,
                "prompt": cleaned_prompt,
                "duration": resolved_duration,
                "aspect_ratio": aspect_ratio,
                "audio": bool(audio),
                "video_bytes": response.content,
                "mime_type": "video/mp4",
                "summary": (
                    "Video generated successfully "
                    "through Pollinations."
                ),
            }

        except requests.Timeout:
            return {
                "tool": self.name,
                "status": "timeout",
                "error": (
                    "Pollinations video generation "
                    "timed out."
                ),
                "video_bytes": None,
            }

        except requests.HTTPError as error:
            response = error.response
            details = ""

            if response is not None:
                details = (
                    response.text[:500]
                )

            return {
                "tool": self.name,
                "status": "provider_error",
                "error": (
                    "Pollinations request failed: "
                    f"{error}. {details}"
                ).strip(),
                "video_bytes": None,
            }

        except requests.RequestException as error:
            return {
                "tool": self.name,
                "status": "error",
                "error": str(error),
                "video_bytes": None,
            }

    def run(
        self,
        prompt: str,
        model: str = "wan-fast",
        duration: int = 5,
        aspect_ratio: str = "9:16",
        audio: bool = False,
    ) -> dict[str, Any]:
        """
        Standard ToolManager entry point.
        """

        return self.generate(
            prompt=prompt,
            model=model,
            duration=duration,
            aspect_ratio=aspect_ratio,
            audio=audio,
        )
