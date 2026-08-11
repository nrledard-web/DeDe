"""
DeDe - Free Video Maker

Creates an MP4 video locally from uploaded images.

No external video-generation API is required.
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from PIL import (
    Image,
    ImageColor,
)

from moviepy import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
)


class FreeVideoMaker:
    """
    Assemble uploaded images into an MP4 video.
    """

    name = "free_video_maker"

    description = (
        "Create an MP4 video locally from "
        "a sequence of uploaded images."
    )

    input_schema = {
        "images": {
            "type": "array",
            "required": True,
        },
        "aspect_ratio": {
            "type": "string",
            "required": False,
            "default": "9:16",
        },
        "seconds_per_image": {
            "type": "number",
            "required": False,
            "default": 3,
        },
        "background_color": {
            "type": "string",
            "required": False,
            "default": "black",
        },
    }

    ALLOWED_ASPECT_RATIOS = {
        "9:16",
        "16:9",
        "1:1",
    }

    OUTPUT_SIZES = {
        "9:16": (
            720,
            1280,
        ),
        "16:9": (
            1280,
            720,
        ),
        "1:1": (
            720,
            720,
        ),
    }

    MAX_IMAGES = 12

    MIN_SECONDS_PER_IMAGE = 1.0
    MAX_SECONDS_PER_IMAGE = 10.0

    def create_video(
        self,
        images: list[bytes],
        aspect_ratio: str = "9:16",
        seconds_per_image: float = 3,
        background_color: str = "black",
    ) -> dict[str, Any]:
        """
        Build an MP4 video from image bytes.
        """

        if not images:
            return {
                "tool": self.name,
                "status": "invalid_request",
                "error": (
                    "No images were provided."
                ),
                "video_bytes": None,
            }

        if len(images) > self.MAX_IMAGES:
            return {
                "tool": self.name,
                "status": "too_many_images",
                "error": (
                    "A maximum of "
                    f"{self.MAX_IMAGES} images "
                    "can be used per video."
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
            resolved_duration = float(
                seconds_per_image
            )

        except (
            TypeError,
            ValueError,
        ):
            resolved_duration = 3.0

        resolved_duration = max(
            self.MIN_SECONDS_PER_IMAGE,
            min(
                resolved_duration,
                self.MAX_SECONDS_PER_IMAGE,
            ),
        )

        try:
            resolved_background = (
                ImageColor.getrgb(
                    background_color
                )
            )

        except ValueError:
            resolved_background = (
                0,
                0,
                0,
            )

        output_size = self.OUTPUT_SIZES[
            aspect_ratio
        ]

        clips = []

        try:
            for image_bytes in images:
                prepared_image = (
                    self._prepare_image(
                        image_bytes=image_bytes,
                        output_size=output_size,
                        background_color=(
                            resolved_background
                        ),
                    )
                )

                image_array = np.array(
                    prepared_image
                )

                clip = ImageClip(
                    image_array
                ).with_duration(
                    resolved_duration
                )

                clips.append(
                    clip
                )

            if not clips:
                return {
                    "tool": self.name,
                    "status": "empty",
                    "error": (
                        "No valid images could "
                        "be prepared."
                    ),
                    "video_bytes": None,
                }

            final_clip = concatenate_videoclips(
                clips,
                method="compose",
            )

            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = (
                    Path(temp_dir)
                    / "dede_free_video.mp4"
                )

                final_clip.write_videofile(
                    str(output_path),
                    fps=24,
                    codec="libx264",
                    audio=False,
                    logger=None,
                )

                video_bytes = (
                    output_path.read_bytes()
                )

            total_duration = (
                len(clips)
                * resolved_duration
            )

            return {
                "tool": self.name,
                "status": "success",
                "provider": "local",
                "model": "dede_free_video_maker",
                "image_count": len(clips),
                "aspect_ratio": aspect_ratio,
                "seconds_per_image": (
                    resolved_duration
                ),
                "duration": total_duration,
                "video_bytes": video_bytes,
                "mime_type": "video/mp4",
                "summary": (
                    "Video created successfully "
                    "inside DeDe."
                ),
            }

        except Exception as error:
            return {
                "tool": self.name,
                "status": "error",
                "error": str(error),
                "video_bytes": None,
            }

        finally:
            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass

            if "final_clip" in locals():
                try:
                    final_clip.close()
                except Exception:
                    pass

    def _prepare_image(
        self,
        image_bytes: bytes,
        output_size: tuple[int, int],
        background_color: tuple[int, int, int],
    ) -> Image.Image:
        """
        Resize one image while preserving its proportions.
        """

        if not isinstance(
            image_bytes,
            (
                bytes,
                bytearray,
            ),
        ):
            raise ValueError(
                "Unsupported image data."
            )

        with Image.open(
            io.BytesIO(
                bytes(image_bytes)
            )
        ) as source_image:

            source_image = (
                source_image
                .convert("RGB")
            )

            output_width = output_size[0]
            output_height = output_size[1]

            source_width = (
                source_image.width
            )

            source_height = (
                source_image.height
            )

            scale = min(
                output_width / source_width,
                output_height / source_height,
            )

            resized_width = max(
                1,
                round(
                    source_width
                    * scale
                ),
            )

            resized_height = max(
                1,
                round(
                    source_height
                    * scale
                ),
            )

            resized_image = source_image.resize(
                (
                    resized_width,
                    resized_height,
                ),
                Image.Resampling.LANCZOS,
            )

            canvas = Image.new(
                "RGB",
                output_size,
                background_color,
            )

            horizontal_position = (
                output_width
                - resized_width
            ) // 2

            vertical_position = (
                output_height
                - resized_height
            ) // 2

            canvas.paste(
                resized_image,
                (
                    horizontal_position,
                    vertical_position,
                ),
            )

            return canvas

    def run(
        self,
        images: list[bytes],
        aspect_ratio: str = "9:16",
        seconds_per_image: float = 3,
        background_color: str = "black",
    ) -> dict[str, Any]:
        """
        Standard ToolManager entry point.
        """

        return self.create_video(
            images=images,
            aspect_ratio=aspect_ratio,
            seconds_per_image=(
                seconds_per_image
            ),
            background_color=(
                background_color
            ),
        )
