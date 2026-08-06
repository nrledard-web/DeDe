"""
DeDe - Video Studio Panel

Streamlit sidebar interface for video generation.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_video_studio_panel(
    tool_manager: Any,
) -> None:
    """
    Render Video Studio inside the sidebar.
    """

    with st.sidebar:
        with st.expander(
            "🎬 Video Studio",
            expanded=False,
        ):
            st.caption(
                "Generate short MP4 videos "
                "through Pollinations."
            )

            video_prompt = st.text_area(
                "Describe the video",
                placeholder=(
                    "Example: A cinematic flight "
                    "over Barcelona at sunset, "
                    "smooth camera motion."
                ),
                key="video_generator_prompt",
                height=120,
            )

            model_labels = {
                "WAN Fast — Faster": "wan-fast",
                "Seedance 2.0 — Balanced": (
                    "seedance-2.0"
                ),
                "Veo — High Quality": "veo",
            }

            selected_model_label = st.selectbox(
                "Video model",
                list(
                    model_labels.keys()
                ),
                index=0,
                key="video_generator_model",
            )

            selected_model = model_labels[
                selected_model_label
            ]

            format_labels = {
                "Vertical — 9:16": "9:16",
                "Horizontal — 16:9": "16:9",
            }

            selected_format = st.selectbox(
                "Video format",
                list(
                    format_labels.keys()
                ),
                index=0,
                key="video_generator_format",
            )

            aspect_ratio = format_labels[
                selected_format
            ]

            duration_options = {
                "wan-fast": [
                    5,
                    10,
                ],
                "seedance-2.0": [
                    4,
                    5,
                    8,
                    10,
                    15,
                ],
                "veo": [
                    4,
                    6,
                    8,
                ],
            }

            duration = st.selectbox(
                "Duration (seconds)",
                duration_options[
                    selected_model
                ],
                index=0,
                key=(
                    "video_generator_duration_"
                    f"{selected_model}"
                ),
            )

            generate_audio = st.checkbox(
                "Generate audio when supported",
                value=False,
                key="video_generator_audio",
            )

            st.caption(
                "Generation can take several "
                "minutes and consumes "
                "Pollinations credits."
            )

            if st.button(
                "Generate video",
                key="generate_video_button",
                type="primary",
                use_container_width=True,
            ):
                _generate_video(
                    tool_manager=tool_manager,
                    arguments={
                        "prompt": video_prompt,
                        "model": selected_model,
                        "duration": duration,
                        "aspect_ratio": (
                            aspect_ratio
                        ),
                        "audio": generate_audio,
                    },
                )

            _show_generated_video()


def _generate_video(
    tool_manager: Any,
    arguments: dict[str, Any],
) -> None:
    """
    Validate the request and execute video generation.
    """

    prompt = str(
        arguments.get(
            "prompt",
            "",
        )
    ).strip()

    if not prompt:
        st.warning(
            "Describe the video before "
            "starting generation."
        )
        return

    if (
        "POLLINATIONS_API_KEY"
        not in st.secrets
    ):
        st.error(
            "POLLINATIONS_API_KEY is missing "
            "from Streamlit secrets."
        )
        return

    with st.spinner(
        "DeDe is generating the video. "
        "This can take several minutes..."
    ):
        tool_result = tool_manager.run(
            tool_name=(
                "pollinations_video_generator"
            ),
            arguments=arguments,
        )

    normalized_result = {
        "tool": tool_result.get(
            "tool",
            "pollinations_video_generator",
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
        "last_generated_video"
    ] = normalized_result


def _show_generated_video() -> None:
    """
    Display and expose the latest generated video.
    """

    generated_video = (
        st.session_state.get(
            "last_generated_video",
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
                "The provider returned "
                "no video data."
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
            label="Download MP4",
            data=video_bytes,
            file_name=(
                "dede_generated_video.mp4"
            ),
            mime=mime_type,
            key="download_generated_video",
            use_container_width=True,
        )

        provider = generated_video.get(
            "provider",
            "pollinations",
        )

        model = generated_video.get(
            "model",
            "unknown",
        )

        duration = generated_video.get(
            "duration",
            "?",
        )

        st.caption(
            f"Provider: {provider} | "
            f"Model: {model} | "
            f"Duration: {duration}s"
        )

    elif status:
        st.error(
            generated_video.get(
                "error",
                "Video generation failed.",
            )
        )
