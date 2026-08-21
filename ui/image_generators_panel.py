"""
DeDe - Image Generators Panel

Streamlit sidebar interface for interchangeable
image-generation providers.
"""

from __future__ import annotations

import hashlib
from typing import Any

import streamlit as st
from tools.visual_prompt_compiler import VisualPromptCompiler


MOVIE_MAKER_LIBRARY_KEY = (
    "movie_maker_image_library"
)


def render_image_generators_panel(
    tool_manager: Any,
    save_control: Any = None,
) -> None:
    """
    Render the image generators inside the sidebar.
    """

    pending_prompt = (
        st.session_state.pop(
            "pending_image_generator_prompt",
            None,
        )
    )

    if pending_prompt is not None:
        st.session_state[
            "image_generator_prompt"
        ] = str(
            pending_prompt
        ).strip()

    open_image_panel = bool(
        st.session_state.pop(
            "open_image_generators_panel",
            False,
        )
    )

    with st.sidebar:
        with st.expander(
            "🎨 Image Generators",
            expanded=open_image_panel,
        ):
            st.caption(
                "Generate images with interchangeable "
                "AI providers."
            )

            provider_labels = {
                (
                    "OpenAI Image — High Quality"
                ): "openai",
                (
                    "Cloudflare FLUX — Free, "
                    "daily quota"
                ): "cloudflare",
            }

            selected_provider_label = st.selectbox(
                "Image Provider",
                list(provider_labels.keys()),
                index=1,
                key="image_generator_provider",
            )

            selected_provider = provider_labels[
                selected_provider_label
            ]

            image_prompt = st.text_area(
                "Describe the image",
                placeholder=(
                    "Example: A cinematic sunset "
                    "over Barcelona, realistic "
                    "photography."
                ),
                key="image_generator_prompt",
                height=120,
            )

            tool_arguments: dict[str, Any] = {
                "prompt": image_prompt,
            }

            if selected_provider == "openai":
                tool_name = "image_generator"

                format_labels = {
                    (
                        "Square — 1:1"
                    ): "1024x1024",
                    (
                        "Portrait — 2:3"
                    ): "1024x1536",
                    (
                        "Landscape — 3:2"
                    ): "1536x1024",
                }

                selected_format = st.selectbox(
                    "Image format",
                    list(format_labels.keys()),
                    key="openai_image_format",
                )

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

                transparent_background = (
                    st.checkbox(
                        "Transparent background",
                        value=False,
                        key=(
                            "openai_image_"
                            "transparent"
                        ),
                    )
                )

                tool_arguments.update(
                    {
                        "size": format_labels[
                            selected_format
                        ],
                        "quality": image_quality,
                        (
                            "transparent_background"
                        ): transparent_background,
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
                        "More steps can improve "
                        "the image but take longer."
                    ),
                    key="cloudflare_image_steps",
                )

                tool_arguments.update(
                    {
                        "steps": generation_steps,
                    }
                )

                st.caption(
                    "Cloudflare FLUX uses the free "
                    "daily Workers AI allowance."
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
            
            generated_image = (
                st.session_state.get(
                    "last_generated_image",
                    {},
                )
            )

            if (
                generated_image.get(
                    "status"
                )
                == "success"
                and callable(save_control)
            ):
                save_control()


def _generate_image(
    tool_manager: Any,
    provider: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> None:
    """
    Validate and execute image generation.
    """

    prompt = str(
        arguments.get(
            "prompt",
            "",
        )
    ).strip()

    if not prompt:
        st.warning(
            "Describe the image before "
            "starting generation."
        )
        return

    arguments = dict(
        arguments
    )

    arguments["prompt"] = (
        VisualPromptCompiler()
        .compile_generation(
            user_request=prompt,
        )
    )

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

    if normalized_result.get(
        "status"
    ) == "success":
        image_bytes = normalized_result.get(
            "image_bytes"
        )

        if image_bytes:
            mime_type = normalized_result.get(
                "mime_type",
                "image/png",
            )

            extension = (
                "jpg"
                if mime_type == "image/jpeg"
                else "png"
            )

            added = (
                _store_movie_maker_image(
                    image_bytes=bytes(
                        image_bytes
                    ),
                    name=(
                        "dede_generated_image."
                        f"{extension}"
                    ),
                    mime_type=mime_type,
                    source=(
                        "DeDe image generator"
                    ),
                )
            )

            if added:
                st.success(
                    "Image added to the "
                    "Movie Maker library."
                )


def _store_movie_maker_image(
    image_bytes: bytes,
    name: str,
    mime_type: str,
    source: str,
) -> bool:
    """
    Store one generated image for Movie Maker.
    """

    library = st.session_state.setdefault(
        MOVIE_MAKER_LIBRARY_KEY,
        [],
    )

    image_id = hashlib.sha256(
        image_bytes
    ).hexdigest()

    if any(
        item.get("id") == image_id
        for item in library
    ):
        return False

    library.append(
        {
            "id": image_id,
            "name": name,
            "mime_type": mime_type,
            "image_bytes": image_bytes,
            "source": source,
            "selected": True,
        }
    )

    return True


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
                "The provider returned "
                "no image data."
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
                "Generated by DeDe with "
                f"{provider}"
            ),
            width="stretch",
        )

        st.download_button(
            label=(
                f"Download {extension.upper()}"
            ),
            data=image_bytes,
            file_name=(
                "dede_generated_image."
                f"{extension}"
            ),
            mime=mime_type,
            key="download_generated_image",
            use_container_width=True,
        )

        st.caption(
            f"Provider: {provider} | "
            f"Model: {model}"
        )

    elif status:
        st.error(
            generated_image.get(
                "error",
                "Image generation failed.",
            )
        )
