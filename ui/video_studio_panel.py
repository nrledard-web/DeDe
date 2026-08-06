"""
DeDe - Video Studio Panel

Streamlit sidebar interface for interchangeable
video-generation providers.
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
                "Generate short AI videos with "
                "interchangeable providers."
            )

            provider_labels = {
                "Hugging Face — Free monthly credits": (
                    "huggingface"
                ),
                "Pollinations — Paid credits": (
                    "pollinations"
                ),
            }

            selected_provider_label = st.selectbox(
                "Video provider",
                list(
                    provider_labels.keys()
                ),
                index=0,
                key="video_generator_provider",
            )

            selected_provider = provider_labels[
                selected_provider_label
            ]

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

            tool_name = ""
            tool_arguments: dict[str, Any] = {
                "prompt": video_prompt,
            }

            if selected_provider == "huggingface":
                tool_name = (
                    "huggingface_video_generator"
                )

                st.caption(
                    "Hugging Face provides approximately "
                    "$0.10 of free inference credits "
                    "per month. Video availability and "
                    "duration depend on the provider."
                )

            else:
                tool_name = (
                    "pollinations_video_generator"
                )

                model_labels = {
                    "WAN Fast — Faster": (
                        "wan-fast"
                    ),
                    "Seedance 2.0 — Balanced": (
                        "seedance-2.0"
                    ),
                    "Veo — High Quality": (
                        "veo"
                    ),
                }

                selected_model_label = st.selectbox(
                    "Video model",
                    list(
                        model_labels.keys()
                    ),
                    index=0,
                    key="pollinations_video_model",
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
                    key="pollinations_video_format",
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
                        "pollinations_video_duration_"
                        f"{selected_model}"
                    ),
                )

                generate_audio = st.checkbox(
                    "Generate audio when supported",
                    value=False,
                    key="pollinations_video_audio",
                )

                tool_arguments.update(
                    {
                        "model": selected_model,
                        "duration": duration,
                        "aspect_ratio": (
                            aspect_ratio
                        ),
                        "audio": generate_audio,
                    }
                )

                st.caption(
                    "Pollinations charges for each "
                    "generated video."
                )

            if st.button(
                "Generate AI video",
                key="generate_ai_video_button",
                type="primary",
                use_container_width=True,
            ):
                _generate_video(
                    tool_manager=tool_manager,
                    provider=selected_provider,
                    tool_name=tool_name,
                    arguments=tool_arguments,
                )

            _show_generated_video()


def _generate_video(
    tool_manager: Any,
    provider: str,
    tool_name: str,
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
        provider == "huggingface"
        and "HF_TOKEN" not in st.secrets
    ):
        st.error(
            "HF_TOKEN is missing from "
            "Streamlit secrets."
        )
        return

    if (
        provider == "pollinations"
        and "POLLINATIONS_API_KEY"
        not in st.secrets
    ):
        st.error(
            "POLLINATIONS_API_KEY is missing "
            "from Streamlit secrets."
        )
        return

    if provider == "huggingface":
        spinner_message = (
            "DeDe is generating the video "
            "through Hugging Face. "
            "This can take several minutes..."
        )

    else:
        spinner_message = (
            "DeDe is generating the video "
            "through Pollinations. "
            "This can take several minutes..."
        )

    with st.spinner(
        spinner_message
    ):
        tool_result = tool_manager.run(
            tool_name=tool_name,
            arguments=arguments,
        )

    normalized_result = {
        "tool": tool_result.get(
            "tool",
            tool_name,
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
            "AI",
        )

        model = generated_video.get(
            "model",
            "unknown",
        )

        st.caption(
            f"Provider: {provider} | "
            f"Model: {model}"
        )

    elif status:
        st.error(
            generated_video.get(
                "error",
                "Video generation failed.",
            )
        )
