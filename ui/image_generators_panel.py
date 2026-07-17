"""
DeDe - Image Generators Panel

Streamlit sidebar interface for interchangeable
image-generation providers.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_image_generators_panel(
    tool_manager: Any,
) -> None:
    """
    Render the image generators inside the sidebar.
    """

    with st.sidebar:
        with st.expander(
            "🎨 Image Generators",
            expanded=False,
        ):
            st.caption(
                "Generate images with interchangeable "
                "AI providers."
            )

            provider_labels = {
                "OpenAI Image — High Quality": "openai",
                "Cloudflare FLUX — Free": "cloudflare",
            }

            selected_provider_label = st.selectbox(
                "Image Provider",
                list(provider_labels.keys()),
                key="image_generator_provider",
            )

            selected_provider = provider_labels[
                selected_provider_label
            ]

            image_prompt = st.text_area(
                "Describe the image",
                placeholder=(
                    "Example: A cinematic sunset over "
                    "Barcelona, realistic photography."
                ),
                key="image_generator_prompt",
                height=120,
            )

            tool_name = ""
            tool_arguments: dict[str, Any] = {
                "prompt": image_prompt,
            }

            if selected_provider == "openai":
                tool_name = "image_generator"

                format_labels = {
                    "Square — 1:1": "1024x1024",
                    "Portrait — 2:3": "1024x1536",
                    "Landscape — 3:2": "1536x1024",
                }

                selected_format = st.selectbox(
                    "Image format",
                    list(format_labels.keys()),
                    key="openai_image_format",
                )

                image_size = format_labels[
                    selected_format
                ]

                image_quality = st.selectbox(
                    "Quality",
                    [
                        "low",
                        "medium",
                        "high",
                    ],
                    index=1,
                    key="openai_image_quality",
                )

                transparent_background = st.checkbox(
                    "Transparent background",
                    value=False,
                    key="openai_image_transparent",
                )

                tool_arguments.update(
                    {
                        "size": image_size,
                        "quality": image_quality,
                        "transparent_background": (
                            transparent_background
                        ),
                    }
                )

            else:
                tool_name = (
                    "cloudflare_image_generator"
                )

                generation_steps = st.slider(
                    "Generation steps",
                    min_value=1,
                    max_value=8,
                    value=4,
                    help=(
                        "More steps can improve the image "
                        "but take slightly longer."
                    ),
                    key="cloudflare_image_steps",
                )

                tool_arguments.update(
                    {
                        "steps": generation_steps,
                    }
                )

                st.caption(
                    "Cloudflare FLUX uses the free daily "
                    "Workers AI allowance."
                )

            if st.button(
                "Generate image",
                key="generate_image_button",
                type="primary",
                use_container_width=True,
            ):
                _generate_image(
                    tool_manager=tool_manager,
                    provider=selected_provider,
                    tool_name=tool_name,
                    arguments=tool_arguments,
                )

            _show_generated_image()


def _generate_image(
    tool_manager: Any,
    provider: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> None:
    """
    Validate the request and execute the selected tool.
    """

    prompt = str(
        arguments.get(
            "prompt",
            "",
        )
    ).strip()

    if not prompt:
        st.warning(
            "Describe the image before starting generation."
        )
        return

    if (
        provider == "openai"
        and "OPENAI_API_KEY" not in st.secrets
    ):
        st.error(
            "OPENAI_API_KEY is missing "
            "from Streamlit secrets."
        )
        return

    if (
        provider == "cloudflare"
        and (
            "CLOUDFLARE_ACCOUNT_ID"
            not in st.secrets
            or "CLOUDFLARE_API_TOKEN"
            not in st.secrets
        )
    ):
        st.error(
            "Cloudflare credentials are missing "
            "from Streamlit secrets."
        )
        return

    with st.spinner(
        "DeDe is generating the image..."
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
            "error",
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
        "last_generated_image"
    ] = normalized_result


def _show_generated_image() -> None:
    """
    Display and expose the last generated image.
    """

    generated_image = st.session_state.get(
        "last_generated_image",
        {},
    )

    status = generated_image.get(
        "status"
    )

    if status == "success":
        image_bytes = generated_image.get(
            "image_bytes"
        )

        if not image_bytes:
            st.error(
                "The provider returned no image data."
            )
            return

        mime_type = generated_image.get(
            "mime_type",
            "image/png",
        )

        extension = (
            "jpg"
            if mime_type == "image/jpeg"
            else "png"
        )

        provider = generated_image.get(
            "provider",
            "AI",
        )

        model = generated_image.get(
            "model",
            "unknown",
        )

        st.image(
            image_bytes,
            caption=(
                f"Generated by DeDe with {provider}"
            ),
            width="stretch",
        )

        st.download_button(
            label=f"Download {extension.upper()}",
            data=image_bytes,
            file_name=(
                f"dede_generated_image.{extension}"
            ),
            mime=mime_type,
            key="download_generated_image",
            use_container_width=True,
        )

        st.caption(
            f"Provider: {provider} | Model: {model}"
        )

    elif status:
        st.error(
            generated_image.get(
                "error",
                "Image generation failed.",
            )
        )
