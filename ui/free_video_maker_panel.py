"""
DeDe - Free Video Maker Panel

Streamlit sidebar interface for creating an MP4
locally from stored or uploaded images.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import streamlit as st


MOVIE_MAKER_LIBRARY_KEY = (
    "movie_maker_image_library"
)

MAX_LIBRARY_IMAGES = 30
MAX_VIDEO_IMAGES = 12


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
                "Create an MP4 locally. "
                "Drag images here on a computer, "
                "or choose photos from a smartphone."
            )

            uploaded_images = st.file_uploader(
                (
                    "Drag and drop images "
                    "or browse your device"
                ),
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                ],
                accept_multiple_files=True,
                key="free_video_maker_images",
                help=(
                    "On a smartphone, tap "
                    "Browse files to choose photos."
                ),
            )

            if uploaded_images:
                added_count = (
                    _store_uploaded_images(
                        uploaded_images
                    )
                )

                if added_count:
                    st.success(
                        f"{added_count} image(s) "
                        "stored for Movie Maker."
                    )

            camera_image = st.camera_input(
                "Take a photo with this device",
                key="free_video_maker_camera",
            )

            if camera_image:
                added_count = (
                    _store_uploaded_images(
                        [camera_image],
                        source="Camera",
                    )
                )

                if added_count:
                    st.success(
                        "Photo stored for "
                        "Movie Maker."
                    )

            library = (
                st.session_state.setdefault(
                    MOVIE_MAKER_LIBRARY_KEY,
                    [],
                )
            )

            st.markdown(
                "#### Movie Maker image library"
            )

            if not library:
                st.info(
                    "No stored image yet."
                )

            else:
                st.caption(
                    f"{len(library)} stored "
                    "image(s). Select up to "
                    f"{MAX_VIDEO_IMAGES} "
                    "for one video."
                )

                _render_library(
                    library
                )

            selected_items = [
                item
                for item in library
                if item.get(
                    "selected",
                    True,
                )
            ]

            selected_items = (
                selected_items[
                    :MAX_VIDEO_IMAGES
                ]
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

            selected_background = (
                st.selectbox(
                    "Background",
                    list(
                        background_labels.keys()
                    ),
                    index=0,
                    key=(
                        "free_video_maker_"
                        "background"
                    ),
                )
            )

            background_color = (
                background_labels[
                    selected_background
                ]
            )

            total_duration = (
                len(selected_items)
                * seconds_per_image
            )

            st.caption(
                f"Selected: "
                f"{len(selected_items)} | "
                "Estimated duration: "
                f"{total_duration} seconds."
            )

            if st.button(
                "Create free video",
                key=(
                    "create_free_video_button"
                ),
                type="primary",
                use_container_width=True,
            ):
                _create_free_video(
                    tool_manager=tool_manager,
                    selected_items=(
                        selected_items
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


def _store_uploaded_images(
    uploaded_images: Any,
    source: str = "Upload",
) -> int:
    """
    Store uploaded images in the session library.
    """

    library = st.session_state.setdefault(
        MOVIE_MAKER_LIBRARY_KEY,
        [],
    )

    added_count = 0

    for uploaded_image in uploaded_images:
        if (
            len(library)
            >= MAX_LIBRARY_IMAGES
        ):
            st.warning(
                "The library is limited to "
                f"{MAX_LIBRARY_IMAGES} images."
            )
            break

        try:
            content = bytes(
                uploaded_image.getvalue()
            )

        except Exception:
            content = b""

        if not content:
            continue

        image_id = hashlib.sha256(
            content
        ).hexdigest()

        deleted_image_ids = (
            st.session_state.setdefault(
                "movie_maker_deleted_image_ids",
                set(),
            )
        )

        if image_id in deleted_image_ids:
            continue

        if any(
            item.get("id") == image_id
            for item in library
        ):
            continue

        image_name = getattr(
            uploaded_image,
            "name",
            "smartphone_photo.jpg",
        )

        mime_type = getattr(
            uploaded_image,
            "type",
            "image/jpeg",
        )

        library.append(
            {
                "id": image_id,
                "name": image_name,
                "mime_type": mime_type,
                "image_bytes": content,
                "source": source,
                "selected": True,
            }
        )

        added_count += 1

    return added_count


def _render_library(
    library: list[dict[str, Any]],
) -> None:
    """
    Display stored images and ordering controls.
    """

    for index, item in enumerate(
        list(library)
    ):
        image_id = item["id"]

        st.image(
            item["image_bytes"],
            caption=(
                f"{index + 1}. "
                f"{item['name']}"
            ),
            width="stretch",
        )

        item["selected"] = st.checkbox(
            "Use in video",
            value=item.get(
                "selected",
                True,
            ),
            key=(
                "movie_maker_selected_"
                f"{image_id}"
            ),
        )

        left_column, middle_column, (
            right_column
        ) = st.columns(3)

        if left_column.button(
            "⬆️",
            key=f"movie_up_{image_id}",
            disabled=(index == 0),
            help="Move image up",
        ):
            (
                library[index - 1],
                library[index],
            ) = (
                library[index],
                library[index - 1],
            )

            st.rerun()

        if middle_column.button(
            "⬇️",
            key=f"movie_down_{image_id}",
            disabled=(
                index
                == len(library) - 1
            ),
            help="Move image down",
        ):
            (
                library[index + 1],
                library[index],
            ) = (
                library[index],
                library[index + 1],
            )

            st.rerun()

        if right_column.button(
            "🗑️",
            key=(
                f"movie_delete_{image_id}"
            ),
            help="Remove image",
        ):
            deleted_image_ids = (
                st.session_state.setdefault(
                    "movie_maker_deleted_image_ids",
                    set(),
                )
            )

            deleted_image_ids.add(
                image_id
            )

            del library[index]

            st.session_state.pop(
                (
                    "movie_maker_selected_"
                    f"{image_id}"
                ),
                None,
            )

            st.rerun()

        st.download_button(
            label="Download this image",
            data=item["image_bytes"],
            file_name=item["name"],
            mime=item["mime_type"],
            key=(
                f"movie_download_{image_id}"
            ),
            use_container_width=True,
        )


def _create_free_video(
    tool_manager: Any,
    selected_items: list[
        dict[str, Any]
    ],
    aspect_ratio: str,
    seconds_per_image: int,
    background_color: str,
) -> None:
    """
    Create the MP4 from selected stored images.
    """

    if not selected_items:
        st.warning(
            "Select at least one stored image "
            "before creating the video."
        )
        return

    image_bytes = [
        item["image_bytes"]
        for item in selected_items
    ]

    with st.spinner(
        "DeDe is assembling "
        "the free video..."
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
