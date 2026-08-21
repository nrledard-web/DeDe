"""
DeDe - Text Creator interface.
"""

from __future__ import annotations

import streamlit as st


TEXT_TYPES = [
    "Article",
    "Book chapter",
    "Essay",
    "Letter",
    "LinkedIn post",
    "Story",
    "Poem",
    "Report",
    "Custom",
]

TEXT_LANGUAGES = [
    "Automatic",
    "French",
    "English",
    "Spanish",
    "German",
    "Italian",
    "Portuguese",
]

TEXT_TONES = [
    "Natural",
    "Professional",
    "Academic",
    "Philosophical",
    "Literary",
    "Persuasive",
    "Concise",
    "Custom",
]

TEXT_LENGTHS = [
    "Short",
    "Medium",
    "Long",
    "Custom",
]


def ensure_text_creator_state() -> None:
    """
    Initialize Text Creator state.
    """

    defaults = {
        "text_creator_open": False,
        "text_creator_title": "",
        "text_creator_type": (
            TEXT_TYPES[0]
        ),
        "text_creator_language": (
            TEXT_LANGUAGES[0]
        ),
        "text_creator_tone": (
            TEXT_TONES[0]
        ),
        "text_creator_length": (
            TEXT_LENGTHS[1]
        ),
        "text_creator_instruction": "",
        "text_creator_content": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_text_creator_launcher() -> None:
    """
    Render the Text Creator button.
    """

    ensure_text_creator_state()

    if st.button(
        "✍️ Text Creator",
        key="open_text_creator",
        use_container_width=True,
    ):
        st.session_state[
            "text_creator_open"
        ] = True


def render_text_creator_workspace() -> (
    dict[str, str] | None
):
    """
    Render the Text Creator workspace.
    """

    ensure_text_creator_state()

    if not st.session_state.get(
        "text_creator_open",
        False,
    ):
        return

    st.markdown("---")

    title_column, close_column = (
        st.columns([0.85, 0.15])
    )

    with title_column:
        st.markdown(
            "## ✍️ Text Creator"
        )

        st.caption(
            "Create, edit and refine "
            "text with DeDe."
        )

    with close_column:
        if st.button(
            "✕",
            key="close_text_creator",
            help="Close Text Creator",
            use_container_width=True,
        ):
            st.session_state[
                "text_creator_open"
            ] = False

            st.rerun()

    st.text_input(
        "Title",
        key="text_creator_title",
        placeholder=(
            "Give your document "
            "a title..."
        ),
    )

    type_column, language_column = (
        st.columns(2)
    )

    with type_column:
        st.selectbox(
            "Text type",
            TEXT_TYPES,
            key="text_creator_type",
        )

    with language_column:
        st.selectbox(
            "Language",
            TEXT_LANGUAGES,
            key="text_creator_language",
        )

    tone_column, length_column = (
        st.columns(2)
    )

    with tone_column:
        st.selectbox(
            "Tone",
            TEXT_TONES,
            key="text_creator_tone",
        )

    with length_column:
        st.selectbox(
            "Length",
            TEXT_LENGTHS,
            key="text_creator_length",
        )

    st.text_area(
        "Instruction for DeDe",
        key="text_creator_instruction",
        placeholder=(
            "Describe the text you want "
            "to create..."
        ),
        height=120,
    )

    st.caption(
        "The generation controls will use "
        "the selected DeDe reasoning model."
    )

    create_draft = st.button(
        "✨ Create Draft",
        key="text_creator_create_draft",
        type="primary",
        use_container_width=True,
    )

    if create_draft:
        instruction = str(
            st.session_state.get(
                "text_creator_instruction",
                "",
            )
            or ""
        ).strip()

        title = str(
            st.session_state.get(
                "text_creator_title",
                "",
            )
            or ""
        ).strip()

        if not instruction and not title:
            st.warning(
                "Add a title or an instruction "
                "before creating the draft."
            )

        else:
            return {
                "action": "create_draft",
                "title": title,
                "text_type": str(
                    st.session_state.get(
                        "text_creator_type",
                        "Article",
                    )
                ),
                "language": str(
                    st.session_state.get(
                        "text_creator_language",
                        "Automatic",
                    )
                ),
                "tone": str(
                    st.session_state.get(
                        "text_creator_tone",
                        "Natural",
                    )
                ),
                "length": str(
                    st.session_state.get(
                        "text_creator_length",
                        "Medium",
                    )
                ),
                "instruction": instruction,
            }

    st.text_area(
        "Editor",
        key="text_creator_content",
        placeholder=(
            "Write here or ask DeDe "
            "to generate a draft..."
        ),
        height=180,
    )

    current_content = str(
        st.session_state.get(
            "text_creator_content",
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
