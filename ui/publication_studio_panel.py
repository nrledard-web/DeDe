"""
DeDe - Publication Studio interface.

Provides the Publication Studio launcher,
workspace and session state.
"""

from __future__ import annotations

import streamlit as st


PUBLICATION_TYPES = [
    "Document",
    "Article",
    "Book chapter",
    "LinkedIn post",
    "Facebook post",
    "Instagram post",
    "X post",
    "Newsletter",
    "Custom",
]

PUBLICATION_FORMATS = [
    "A4 Portrait",
    "A4 Landscape",
    "Square 1:1",
    "Portrait 4:5",
    "Story 9:16",
]

PUBLICATION_FONTS = [
    "Arial",
    "Calibri",
    "Georgia",
    "Garamond",
    "Helvetica",
    "Times New Roman",
    "Verdana",
]

PUBLICATION_ALIGNMENTS = [
    "Left",
    "Center",
    "Right",
    "Justified",
]


def ensure_publication_studio_state() -> None:
    """
    Initialize Publication Studio state.
    """

    defaults = {
        "publication_studio_open": False,
        "publication_title": "",
        "publication_type": (
            PUBLICATION_TYPES[0]
        ),
        "publication_format": (
            PUBLICATION_FORMATS[0]
        ),
        "publication_font": (
            PUBLICATION_FONTS[1]
        ),
        "publication_font_size": 12,
        "publication_alignment": (
            PUBLICATION_ALIGNMENTS[0]
        ),
        "publication_bold": False,
        "publication_italic": False,
        "publication_content": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_publication_studio_launcher() -> None:
    """
    Render the Publication Studio button.
    """

    ensure_publication_studio_state()

    if st.button(
        "📰 Publication Studio",
        key="open_publication_studio",
        use_container_width=True,
    ):
        st.session_state[
            "publication_studio_open"
        ] = True


def render_publication_studio_workspace() -> None:
    """
    Render the Publication Studio workspace.
    """

    ensure_publication_studio_state()

    if not st.session_state.get(
        "publication_studio_open",
        False,
    ):
        return

    st.markdown("---")

    title_column, close_column = (
        st.columns([0.85, 0.15])
    )

    with title_column:
        st.markdown(
            "## 📰 Publication Studio"
        )

        st.caption(
            "Format and prepare documents "
            "and social media publications."
        )

    with close_column:
        if st.button(
            "✕",
            key="close_publication_studio",
            help="Close Publication Studio",
            use_container_width=True,
        ):
            st.session_state[
                "publication_studio_open"
            ] = False

            st.rerun()

    st.text_input(
        "Publication title",
        key="publication_title",
        placeholder=(
            "Give your publication "
            "a title..."
        ),
    )

    type_column, format_column = (
        st.columns(2)
    )

    with type_column:
        st.selectbox(
            "Publication type",
            PUBLICATION_TYPES,
            key="publication_type",
        )

    with format_column:
        st.selectbox(
            "Page or social format",
            PUBLICATION_FORMATS,
            key="publication_format",
        )

    font_column, size_column = (
        st.columns(2)
    )

    with font_column:
        st.selectbox(
            "Font",
            PUBLICATION_FONTS,
            key="publication_font",
        )

    with size_column:
        st.number_input(
            "Font size",
            min_value=8,
            max_value=72,
            step=1,
            key="publication_font_size",
        )

    alignment_column, style_column = (
        st.columns(2)
    )

    with alignment_column:
        st.selectbox(
            "Text alignment",
            PUBLICATION_ALIGNMENTS,
            key="publication_alignment",
        )

    with style_column:
        bold_column, italic_column = (
            st.columns(2)
        )

        with bold_column:
            st.checkbox(
                "Bold",
                key="publication_bold",
            )

        with italic_column:
            st.checkbox(
                "Italic",
                key="publication_italic",
            )

    st.text_area(
        "Publication content",
        key="publication_content",
        placeholder=(
            "Write, paste or import "
            "your text here..."
        ),
        height=300,
    )

    current_content = str(
        st.session_state.get(
            "publication_content",
            "",
        )
        or ""
    )

    word_count = len(
        current_content.split()
    )

    character_count = len(
        current_content
    )

    st.caption(
        f"{word_count} words | "
        f"{character_count} characters"
    )

    st.caption(
        "Document preview and export controls "
        "will be added in the next step."
    )
