"""
DeDe - Free Video Maker Panel

Streamlit sidebar interface for creating an MP4
locally from uploaded images.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_free_video_maker_panel(
    tool_manager: Any,
) -> None:
    """
    Render the free local video maker.
    """

    with st.sidebar:
        with st.expander(
            "🎞️ Free Video Maker",
            expanded=False,
        ):
            st.caption(
                "Create an MP4 video locally "
                "from your images. No paid "
                "video API is required."
            )

            uploaded_images = st.file_uploader(
                "Choose images",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                ],
                accept_multiple_files=True,
                key="free_video_maker_images",
                help=(
                    "The images will appear "
                    "in the order selected."
                ),
            )

            if uploaded_images:
                st.caption(
                    f"{len(uploaded_images)} "
                    "image(s) selected."
                )

                if len(uploaded_images) > 12:
                    st.warning(
                        "Only the first 12 images "
                        "will be used."
                    )

            format_labels = {
                "Vertical — 9:16": "9:16",
                "Horizontal — 16:9": "16:9",
                "Square — 1:1": "1:1",
            }

            selected_format = st.selectbox(
                "Video format",
                list(
                    format_labels.keys()
                ),
                index=0,
                key="free_video_maker_format",
            )

            aspect_ratio = format_labels[
                selected_format
            ]

            seconds_per_image = st.slider(
                "Seconds per image",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
                key=(
                    "free_video_maker_"
                    "seconds_per_image"
                ),
            )

            background_labels = {
                "Black": "black",
                "White": "white",
                "Dark grey": "#202124",
                "Light grey": "#e5e7eb",
            }

            selected_background = st.selectbox(
                "Background",
                list(
                    background_labels.keys()
                ),
                index=0,
                key="free_video_maker_background",
            )

            background_color = background_labels[
                selected_background
            ]

            if uploaded_images:
                used_image_count = min(
                    len(uploaded_images),
                    12,
                )

                total_duration = (
                    used_image_count
                    * seconds_per_image
                )

                st.caption(
                    "Estimated duration: "
                    f"{total_duration} seconds."
                )

            st.caption(
                "The first version creates a clean "
                "image sequence. Transitions, text "
                "and narration will be added next."
            )

            if st.button(
                "Create free video",
                key="create_free_video_button",
                type="primary",
                use_container_width=True,
            ):
                _create_free_video(
                    tool_manager=tool_manager,
                    uploaded_images=(
                        uploaded_images
                    ),
                    aspect_ratio=aspect_ratio,
                    seconds_per_image=(
                        seconds_per_image
                    ),
                    background_color=(
                        background_color
                    ),
                )

            _show_free_video()


def _create_free_video(
    tool_manager: Any,
    uploaded_images: Any,
    aspect_ratio: str,
    seconds_per_image: int,
    background_color: str,
) -> None:
    """
    Validate uploaded images and create the MP4.
    """

    if not uploaded_images:
        st.warning(
            "Choose at least one image "
            "before creating the video."
        )
        return

    selected_images = (
        uploaded_images[:12]
    )

    image_bytes = []

    for uploaded_image in selected_images:
        try:
            content = (
                uploaded_image.getvalue()
            )

        except Exception:
            content = b""

        if content:
            image_bytes.append(
                content
            )

    if not image_bytes:
        st.error(
            "The selected files contained "
            "no readable image data."
        )
        return

    with st.spinner(
        "DeDe is assembling the free video..."
    ):
        tool_result = tool_manager.run(
            tool_name="free_video_maker",
            arguments={
                "images": image_bytes,
                "aspect_ratio": (
                    aspect_ratio
                ),
                "seconds_per_image": (
                    seconds_per_image
                ),
                "background_color": (
                    background_color
                ),
            },
        )

    normalized_result = {
        "tool": tool_result.get(
            "tool",
            "free_video_maker",
        ),
        "status": tool_result.get(
            "status",
            "error",
        ),
        "error": tool_result.get(
            "error"
        ),
        "summary": tool_result.get(
            "summary",
            "",
        ),
        **tool_result.get(
            "data",
            {},
        ),
    }

    st.session_state[
        "last_free_video"
    ] = normalized_result


def _show_free_video() -> None:
    """
    Display and expose the latest local MP4.
    """

    generated_video = (
        st.session_state.get(
            "last_free_video",
            {},
        )
    )

    status = generated_video.get(
        "status"
    )

    if status == "success":
        video_bytes = generated_video.get(
            "video_bytes"
        )

        if not video_bytes:
            st.error(
                "DeDe created no video data."
            )
            return

        mime_type = generated_video.get(
            "mime_type",
            "video/mp4",
        )

        st.video(
            video_bytes,
            format=mime_type,
        )

        st.download_button(
            label="Download free MP4",
            data=video_bytes,
            file_name=(
                "dede_free_video.mp4"
            ),
            mime=mime_type,
            key="download_free_video",
            use_container_width=True,
        )

        image_count = generated_video.get(
            "image_count",
            "?",
        )

        duration = generated_video.get(
            "duration",
            "?",
        )

        video_format = generated_video.get(
            "aspect_ratio",
            "?",
        )

        st.caption(
            f"Images: {image_count} | "
            f"Duration: {duration}s | "
            f"Format: {video_format}"
        )

    elif status:
        st.error(
            generated_video.get(
                "error",
                "Free video creation failed.",
            )
        )
