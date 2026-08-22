import streamlit as st
from openai import OpenAI

import tempfile
import os
import time
from pathlib import Path

from textwrap import dedent

import streamlit.components.v1 as components

from ui.image_generators_panel import (
    render_image_generators_panel,
    _store_movie_maker_image,
)

from ui.document_studio_panel import (
    render_document_studio_panel,
)

from ui.text_creator_panel import (
    render_text_creator_launcher,
    render_text_creator_workspace,
)

from ui.coding_studio_panel import (
    render_coding_studio_launcher,
    render_coding_studio_workspace,
)

from ui.video_studio_panel import (
    render_video_studio_panel,
)

from ui.free_video_maker_panel import (
    render_free_video_maker_panel,
)

from engine.doxa_engine_phase2 import DoxaEnginePhase2
from memory.memory_portability import MemoryPortability
from core.real_world_anchor import RealWorldAnchor

from tools.tool_governor import ToolGovernor
from tools.github_readonly import GitHubReadOnly
from tools.tool_factory import build_tool_manager

from tools.cloudflare_vision import CloudflareVision
from tools.cloudflare_reference_image import CloudflareReferenceImage
from tools.visual_prompt_compiler import VisualPromptCompiler

def pct(value):
    if value is None:
        return "N/A"
    return f"{round(value * 100)}%"

def start_response_timer():
    """
    Start a browser-side timer while DeDe is working.
    """

    started_at = time.perf_counter()

    timer_placeholder = st.empty()

    with timer_placeholder:
        components.html(
            """
            <div style="
                display:flex;
                align-items:center;
                justify-content:center;
                gap:8px;
                font-family:Arial, sans-serif;
                color:#9aa0a6;
                font-size:14px;
                padding:6px;
            ">
                <span>⏱️ DeDe is thinking:</span>
                <strong id="dede-timer">0.0 s</strong>
            </div>

            <script>
                const timerStart = performance.now();
                const timerElement =
                    document.getElementById("dede-timer");

                setInterval(() => {
                    const elapsed =
                        (performance.now() - timerStart) / 1000;

                    timerElement.textContent =
                        elapsed.toFixed(1) + " s";
                }, 100);
            </script>
            """,
            height=45,
        )

    return {
        "started_at": started_at,
        "placeholder": timer_placeholder,
    }


def finish_response_timer(
    timer_state,
) -> float:
    """
    Stop the visual timer and show total response time.
    """

    elapsed = (
        time.perf_counter()
        - timer_state["started_at"]
    )

    timer_state[
        "placeholder"
    ].empty()

    st.caption(
        f"⏱️ Response time: {elapsed:.1f} seconds"
    )

    return elapsed


def show_metric(label, value):
    st.metric(label, pct(value))
    
def generate_speech(text: str) -> bytes | None:
    if not text:
        return None

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )

    return speech.content

def latest_savable_image() -> dict:
    """
    Return the latest generated image.

    If no generated image exists, use the active
    uploaded or remembered reference image.
    """
    panel_image = (
        st.session_state.get(
            "last_generated_image",
            {},
        )
    )

    if (
        panel_image.get("status")
        == "success"
        and panel_image.get(
            "image_bytes"
        )
    ):
        mime_type = panel_image.get(
            "mime_type",
            "image/jpeg",
        )

        if mime_type == "image/png":
            extension = "png"

        elif mime_type == "image/webp":
            extension = "webp"

        else:
            extension = "jpg"

        return {
            "image_bytes": panel_image.get(
                "image_bytes",
                b"",
            ),
            "mime_type": mime_type,
            "name": (
                "dede_generated_image."
                f"{extension}"
            ),
            "description": str(
                panel_image.get(
                    "prompt",
                    "",
                )
                or ""
            ).strip(),
            "source": "generated",
        }
        
    image_tool_names = {
        "image_generator",
        "cloudflare_image_generator",
        "cloudflare_reference_image",
    }

    tool_history = st.session_state.get(
        "tool_history",
        [],
    )

    for item in reversed(
        tool_history
    ):
        if item.get(
            "tool_name"
        ) not in image_tool_names:
            continue

        tool_result = item.get(
            "tool_result",
            {},
        )

        if tool_result.get(
            "status"
        ) != "success":
            continue

        image_data = tool_result.get(
            "data",
            {},
        )

        image_bytes = image_data.get(
            "image_bytes",
            b"",
        )

        if not image_bytes:
            continue

        mime_type = image_data.get(
            "mime_type",
            "image/png",
        )

        if mime_type == "image/jpeg":
            extension = "jpg"

        elif mime_type == "image/webp":
            extension = "webp"

        else:
            extension = "png"

        return {
            "image_bytes": image_bytes,
            "mime_type": mime_type,
            "name": (
                "dede_generated_image."
                f"{extension}"
            ),
            "description": str(
                image_data.get(
                    "prompt",
                    "",
                )
                or ""
            ).strip(),
            "source": "generated",
        }

    active_image = (
        st.session_state.get(
            "active_chat_image",
            {},
        )
    )

    if active_image.get(
        "image_bytes"
    ):
        active_analysis = (
            st.session_state.get(
                "active_image_analysis",
                {},
            )
        )

        return {
            "image_bytes": (
                active_image.get(
                    "image_bytes",
                    b"",
                )
            ),
            "mime_type": (
                active_image.get(
                    "mime_type",
                    "image/jpeg",
                )
            ),
            "name": (
                active_image.get(
                    "name",
                    "dede_image",
                )
            ),
            "description": str(
                active_analysis.get(
                    "analysis",
                    "",
                )
                or ""
            ).strip(),
            "source": "active_reference",
        }

    return {}

def persistent_folder_options(
    default_label: str,
) -> tuple[list[str], dict[str, str]]:
    """
    Return automatic memory categories and
    user-created persistent folders.
    """

    automatic_destinations = {
        "👤 Identity & Preferences": (
            "automatic:personal_fact"
        ),
        "📁 Projects & Decisions": (
            "automatic:project"
        ),
        "👥 People & Relationships": (
            "automatic:relationship"
        ),
        "📖 Personal History": (
            "automatic:autobiographical"
        ),
        "🤖 DeDe Identity": (
            "automatic:assistant_identity"
        ),
        "📦 Other Memories": (
            "automatic:interaction_note"
        ),
    }

    folder_labels = [
        default_label,
    ]

    folder_lookup = {
        default_label: "",
    }

    for (
        folder_label,
        destination,
    ) in automatic_destinations.items():
        if folder_label == default_label:
            folder_lookup[
                folder_label
            ] = destination

            continue

        folder_labels.append(
            folder_label
        )

        folder_lookup[
            folder_label
        ] = destination

    managed_memory = (
        st.session_state.engine
        .persistent_memory
        .get_memory()
    )

    custom_folders = managed_memory.get(
        "memory_folders",
        [],
    )

    if not isinstance(
        custom_folders,
        list,
    ):
        custom_folders = []

    for folder in custom_folders:
        if not isinstance(
            folder,
            dict,
        ):
            continue

        folder_id = str(
            folder.get(
                "folder_id",
                "",
            )
        ).strip()

        folder_name = str(
            folder.get(
                "name",
                "",
            )
        ).strip()

        if (
            not folder_id
            or not folder_name
        ):
            continue

        folder_label = (
            f"🗂️ {folder_name}"
        )

        folder_labels.append(
            folder_label
        )

        folder_lookup[
            folder_label
        ] = folder_id

    return (
        folder_labels,
        folder_lookup,
    )

def render_message_save_control(
    message_text: str,
    control_key: str,
    default_title: str = "DeDe response",
) -> None:
    """
    Save one specific DeDe response.

    The button is attached to the message and
    never saves another response by mistake.
    """

    cleaned_message = str(
        message_text or ""
    ).strip()

    if not cleaned_message:
        return

    with st.popover(
        "💾 Save",
        use_container_width=False,
    ):
        st.caption(
            "Save this response."
        )

        (
            folder_labels,
            folder_lookup,
        ) = persistent_folder_options(
            default_label=(
                "📦 Other Memories"
            )
        )

        save_as_title = st.text_input(
            "Save as...",
            value=(
                default_title
                or "DeDe response"
            ),
            key=(
                "message_save_title_"
                f"{control_key}"
            ),
        )

        selected_folder_label = (
            st.selectbox(
                "Folder",
                folder_labels,
                key=(
                    "message_save_folder_"
                    f"{control_key}"
                ),
            )
        )

        new_folder_name = st.text_input(
            "New folder name",
            key=(
                "message_new_folder_"
                f"{control_key}"
            ),
            placeholder=(
                "Example: Book, Research, "
                "Ideas..."
            ),
        )

        if st.button(
            "Create Folder",
            key=(
                "message_create_folder_"
                f"{control_key}"
            ),
            use_container_width=True,
        ):
            creation_result = (
                st.session_state.engine
                .persistent_memory
                .create_memory_folder(
                    new_folder_name
                )
            )

            if creation_result.get(
                "created",
                False,
            ):
                st.session_state[
                    "memory_manager_notice"
                ] = "Folder created."

                st.rerun()

            else:
                st.error(
                    creation_result.get(
                        "error",
                        (
                            "The folder could "
                            "not be created."
                        ),
                    )
                )

        if st.button(
            "Save Response",
            key=(
                "message_confirm_save_"
                f"{control_key}"
            ),
            type="primary",
            use_container_width=True,
        ):
            cleaned_title = str(
                save_as_title or ""
            ).strip()

            if not cleaned_title:
                st.error(
                    "Enter a title."
                )

                return

            selected_destination = (
                folder_lookup[
                    selected_folder_label
                ]
            )

            if selected_destination.startswith(
                "automatic:"
            ):
                selected_memory_type = (
                    selected_destination.split(
                        ":",
                        1,
                    )[1]
                )

                selected_folder_id = ""

            else:
                selected_memory_type = (
                    "interaction_note"
                )

                selected_folder_id = (
                    selected_destination
                )

            content_to_save = (
                f"{cleaned_title}\n\n"
                f"{cleaned_message}"
            )

            st.session_state.engine\
                .persistent_memory\
                .store_candidate(
                    candidate={
                        "content": (
                            content_to_save
                        ),
                        "memory_type": (
                            selected_memory_type
                        ),
                        "storage_scope": (
                            "persistent"
                        ),
                        "sensitivity": "low",
                        "confidence": 1.0,
                        "source": (
                            "manual_message_save"
                        ),
                        "project": None,
                        "folder_id": (
                            selected_folder_id
                        ),
                        "subject": (
                            cleaned_title
                        ),
                        "attribute": (
                            "saved_response"
                        ),
                        "value": (
                            cleaned_message
                        ),
                        "selection_origin": (
                            "user_save_button"
                        ),
                    },
                    storage_scope=(
                        "persistent"
                    ),
                )

            st.session_state[
                "memory_manager_notice"
            ] = (
                f"{cleaned_title} "
                "saved successfully."
            )

            st.rerun()

def render_image_save_control() -> None:
    """
    Show the permanent image Save button.

    Nothing is saved until the user confirms.
    """

    with st.popover(
        "💾 Save",
        use_container_width=False,
    ):
        image_to_save = (
            latest_savable_image()
        )

        if not image_to_save:
            st.info(
                "Upload or generate an image first."
            )

            return

        st.caption(
            "Save the latest available image "
            "only when you confirm."
        )

        st.image(
            image_to_save[
                "image_bytes"
            ],
            width="stretch",
        )

        (
            folder_labels,
            folder_lookup,
        ) = persistent_folder_options(
            default_label=(
                "🖼️ Image Memories"
            )
        )

        save_as_name = st.text_input(
            "Save as...",
            value=image_to_save.get(
                "name",
                "dede_image",
            ),
            key=(
                "persistent_image_save_as"
            ),
        )

        selected_folder_label = (
            st.selectbox(
                "Folder",
                folder_labels,
                key=(
                    "persistent_image_"
                    "save_folder"
                ),
            )
        )

        st.markdown(
            "##### Create a folder"
        )

        new_folder_name = st.text_input(
            "New folder name",
            key=(
                "persistent_image_"
                "new_folder"
            ),
            placeholder=(
                "Example: Family, Book, "
                "Images..."
            ),
        )

        if st.button(
            "Create Folder",
            key=(
                "persistent_image_"
                "create_folder"
            ),
            use_container_width=True,
        ):
            creation_result = (
                st.session_state.engine
                .persistent_memory
                .create_memory_folder(
                    new_folder_name
                )
            )

            if creation_result.get(
                "created",
                False,
            ):
                st.session_state[
                    "image_save_notice"
                ] = (
                    "Folder created."
                )

                st.rerun()

            else:
                st.error(
                    creation_result.get(
                        "error",
                        (
                            "The folder could "
                            "not be created."
                        ),
                    )
                )

        if st.button(
            "Save Image",
            key=(
                "persistent_image_"
                "confirm_save"
            ),
            type="primary",
            use_container_width=True,
        ):
            cleaned_name = str(
                save_as_name or ""
            ).strip()

            if not cleaned_name:
                st.error(
                    "Enter a file name."
                )

                return

            selected_folder_id = (
                folder_lookup[
                    selected_folder_label
                ]
            )

            save_result = (
                st.session_state.engine
                .image_memory
                .save_image(
                    image_bytes=(
                        image_to_save[
                            "image_bytes"
                        ]
                    ),
                    original_name=(
                        cleaned_name
                    ),
                    mime_type=(
                        image_to_save.get(
                            "mime_type",
                            "image/jpeg",
                        )
                    ),
                    description=(
                        image_to_save.get(
                            "description",
                            "",
                        )
                    ),
                    label=cleaned_name,
                    usage=[
                        image_to_save.get(
                            "source",
                            "image",
                        ),
                    ],
                    folder_id=(
                        selected_folder_id
                    ),
                )
            )

            if save_result.get(
                "status"
            ) == "success":
                st.session_state[
                    "image_save_notice"
                ] = (
                    f"{cleaned_name} "
                    "saved successfully."
                )

                st.rerun()

            else:
                st.error(
                    save_result.get(
                        "error",
                        (
                            "Image memory "
                            "save failed."
                        ),
                    )
                )


st.set_page_config(
    page_title="DeDe",
    page_icon="🧠",
    layout="wide",
)

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

if "CLOUDFLARE_ACCOUNT_ID" in st.secrets:
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = st.secrets[
        "CLOUDFLARE_ACCOUNT_ID"
    ]

if "CLOUDFLARE_API_TOKEN" in st.secrets:
    os.environ["CLOUDFLARE_API_TOKEN"] = st.secrets[
        "CLOUDFLARE_API_TOKEN"
    ]

if "POLLINATIONS_API_KEY" in st.secrets:
    os.environ["POLLINATIONS_API_KEY"] = st.secrets[
        "POLLINATIONS_API_KEY"
    ]

if "HF_TOKEN" in st.secrets:
    os.environ["HF_TOKEN"] = st.secrets[
        "HF_TOKEN"
    ]

# --------------------------------------------------
# DeDe Tool Layer
# --------------------------------------------------
if "tool_manager" not in st.session_state:
    st.session_state.tool_manager = (
        build_tool_manager()
    )

if "tool_history" not in st.session_state:
    st.session_state.tool_history = []

if "memory_portability" not in st.session_state:
    st.session_state.memory_portability = (
        MemoryPortability()
    )

# --------------------------------------------------
# Force light theme / mobile readability
# --------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        color-scheme: light !important;
    }

    html, body, .stApp {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    [data-testid="stToolbar"] {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f9fafb !important;
        color: #111827 !important;
    }

    h1, h2, h3, h4, h5, h6,
    p, span, div, label,
    .stMarkdown, .stText {
        color: #111827 !important;
    }

    input, textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
    }

    button {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }

        h1 {
            font-size: 1.6rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        p, div, span, label {
            font-size: 0.95rem !important;
        }

        [data-testid="stChatMessage"] {
            padding: 0.65rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BANNER_PATH = Path("assets/Banner01.png")

if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), width="stretch")
else:
    st.warning("Banner01.png not found in assets/")


st.html(
    dedent(
        """
    <style>
.dede-title {
    text-align: center;
    margin-bottom: 0.5rem;
    font-family: "Source Sans 3", "Source Sans Pro", sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 600 !important;
}

.dede-description {
    text-align: center;
    color: #6b7280 !important;
    font-family: "Source Sans 3", "Source Sans Pro", sans-serif !important;
    font-size: 1.08rem !important;
    font-weight: 400 !important;
    line-height: 1.6;
    margin-top: 0;
    margin-bottom: 0.3rem;
}

.dede-line {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    margin-bottom: 0.15rem;
}

.dede-line > span {
    color: #6b7280 !important;
    font-family: "Source Sans 3", "Source Sans Pro", sans-serif !important;
    font-size: 1.08rem !important;
    font-weight: 400 !important;
}

.dede-help {
    display: inline-block;
    position: relative;
}

.dede-help summary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.25rem;
    height: 1.25rem;
    padding: 0;
    border: 1px solid #9ca3af;
    border-radius: 50%;
    background-color: #f3f4f6;
    color: #374151 !important;
    font-family: "Source Sans 3", "Source Sans Pro", sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    line-height: 1;
    cursor: pointer;
    list-style: none;
    user-select: none;
}

.dede-help summary::-webkit-details-marker {
    display: none;
}

.dede-help[open] summary {
    background-color: #e5e7eb;
    border-color: #6b7280;
}

.dede-help-text {
    position: absolute;
    z-index: 1000;
    top: 1.65rem;
    left: 50%;
    transform: translateX(-50%);
    width: min(32rem, 82vw);
    padding: 0.95rem 1.05rem;
    background-color: #ffffff;
    color: #374151 !important;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
    font-family: "Source Sans 3", "Source Sans Pro", sans-serif !important;
    font-size: 0.96rem !important;
    font-weight: 400 !important;
    line-height: 1.55;
    text-align: left;
}

.dede-subtitle {
    text-align: center;
    color: #888888 !important;
    font-family: "Source Sans 3", "Source Sans Pro", sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    margin-top: 0.4rem;
    margin-bottom: 1rem;
}

    @media (max-width: 768px) {
        .dede-description {
            font-size: 0.92rem;
        }

        .dede-line {
            align-items: flex-start;
        }

        .dede-help summary {
            margin-top: 0.18rem;
        }

        .dede-help-text {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: calc(100vw - 2rem);
            max-width: 32rem;
            font-size: 0.88rem;
        }
    }
    </style>

    <div class="dede-line" style="margin-bottom:0.5rem;">
        <h2 class="dede-title" style="margin-bottom:0;">
            DeDe — Cognitive Daimon
        </h2>
    
        <details class="dede-help">
            <summary>?</summary>
    
            <div class="dede-help-text">
                <strong>What is a Daimon?</strong><br><br>
    
                In ancient Greek philosophy, the <em>daimōn</em> was not
                a demon, but a guiding presence associated with discernment,
                inner orientation and the conduct of life.
    
                Socrates famously described his <em>daimonion</em> as an
                inner sign that warned him against certain actions.
                Later philosophical traditions, including Stoicism,
                emphasized reason, self-examination, inner guidance
                and the disciplined interpretation of experience.

                <br><br>

                <strong>
                    DeDe reinterprets this ancient idea in cognitive form.
                </strong>

                <br><br>

                It is designed as a persistent companion for reflection,
                psychological support, self-understanding and emotional
                regulation — not an authority that thinks in your place,
                but a presence that helps you examine your beliefs,
                remember your history, recognize cognitive tensions,
                preserve doubt and revisability, and understand how
                your own thinking changes over time.

                <br><br>

                <strong>
                    Its Cognitive Therapy is based on Cognitive Mechanics.
                </strong>

                <br><br>

                DeDe follows the relation:

                <br><br>

                <strong>
                    M = (G + N) − D
                </strong>

                <br><br>

                where <strong>G — Gnosis</strong> represents articulated
                and grounded knowledge, <strong>N — Nous</strong>
                represents integrated understanding, and
                <strong>D — Doxa</strong> represents stabilized certainty
                and cognitive closure.

                <br><br>

                <strong>M — Mécroyance</strong> represents the current
                position of cognition on a spectrum. Mécroyance is not
                something a human being simply enters or leaves:
                every finite cognition necessarily works through
                incomplete representations of reality. The important
                question is therefore not whether Mécroyance exists,
                but <strong>where cognition currently lies within it</strong>.

                <br><br>

                DeDe can represent this position through a
                <strong>Mécroyance Life Bar</strong>, ranging theoretically
                from <strong>−10 to 20</strong>. The bar is not a measure
                of intelligence, mental health or personal worth.
                It is a cognitive orientation tool showing the evolving
                relation between knowledge, understanding and certainty.

                <br><br>

                When <strong>D exceeds G + N</strong>, M moves toward
                the negative part of the spectrum and toward
                <strong>cognitive closure</strong>. When knowledge and
                integrated understanding increase relative to certainty,
                cognition moves toward greater revisability.

                <br><br>

                DeDe can also compare this cognitive position over time.
                It can observe changes in Gnosis, Nous, Doxa and
                Mécroyance from one interaction to another, allowing
                the user to see whether a belief is becoming more
                grounded, more integrated, more rigid, or more open
                to revision.

                <br><br>

                <strong>
                    Reduction is another central part of this therapy.
                </strong>

                <br><br>

                Human cognition necessarily reduces reality: every word,
                category, theory and explanation selects some dimensions
                while leaving others outside the representation.
                Reduction itself is therefore not an error.

                <br><br>

                DeDe distinguishes between
                <strong>ordinary reduction</strong>,
                <strong>excessive reduction</strong>, and
                <strong>forgotten reduction</strong>. Excessive reduction
                appears when too many relevant dimensions are compressed
                or excluded. Forgotten reduction appears when a simplified
                representation is no longer recognized as a model of
                reality and begins to be treated as reality itself.

                <br><br>

                This is one of the principal mechanisms DeDe watches for,
                because excessive or forgotten reduction can weaken
                Gnosis and Nous while Doxa remains stable or increases,
                pushing cognition toward closure.

                <br><br>

                Cognitive Therapy therefore attempts to restore missing
                dimensions, identify hidden assumptions, introduce
                alternative hypotheses, strengthen grounding, improve
                contextual integration and recalibrate excessive certainty
                — <strong>without replacing the user's beliefs with
                DeDe's own beliefs</strong>.

                <br><br>

                DeDe can also examine
                <strong>cognitive tensions and possible dissonance</strong>
                across a person's expressed beliefs. The objective is not
                to label disagreement, ideology or doctrine as pathological,
                but to notice when two personally held principles become
                difficult to reconcile, particularly when certainty or
                group consensus makes revision harder.

                <br><br>

                The same principle applies to ideological, political,
                religious or philosophical systems. DeDe does not assume
                that an <em>-ism</em> is true or false because it is widely
                accepted or rejected. It distinguishes
                <strong>consensus from truth</strong>, examines the
                reductions contained within a doctrine, and looks at
                whether collective certainty may be stabilizing claims
                beyond their grounding.

                <br><br>

                Throughout this process, the user remains the author of
                their own thought. DeDe's role is to make cognitive
                structures more visible, preserve alternatives and help
                maintain the capacity to revise.

                <br><br>

                <strong>
                    DeDe does not replace professional mental-health care.
                </strong>
                Its role is to support reflection, cognitive orientation,
                psychological support and personal understanding.
            </div>
        </details>
    </div>

    <div class="dede-description">

        <div class="dede-line">
            <span>The First Agentic, Human-Like Cognitive AI Governor</span>

            <details class="dede-help">
                <summary>?</summary>
                <div class="dede-help-text">
                    DeDe is not merely a chatbot. It is a cognitive AI
                    governor capable of coordinating up to five AI models
                    simultaneously, comparing their reasoning, identifying
                    disagreements, and synthesizing their responses. This
                    deeper process may take longer than a standard chatbot
                    response, but it can provide greater depth, balance,
                    and reliability.
                </div>
            </details>
        </div>

        <div class="dede-line">
            <span>
                Designed for User-Owned, Private, and Portable Memory Storage
            </span>

            <details class="dede-help">
                <summary>?</summary>
                <div class="dede-help-text">
                    DeDe’s memory belongs to the user. It can be downloaded,
                    transferred, stored locally or in a personal cloud, and
                    encrypted for additional security. DeDe asks for permission
                    before saving durable personal information, allowing users
                    to retain control over what is remembered.
                </div>
            </details>
        </div>

        <div class="dede-line">
            <span>Powered by Combinable AI Models and Evolving Tools</span>

            <details class="dede-help">
                <summary>?</summary>
                <div class="dede-help-text">
                    DeDe can combine different AI models according to the task
                    instead of depending on a single provider. Its modular
                    architecture also supports evolving tools for web research,
                    image and video generation, document creation, voice
                    interaction, and future capabilities.
                </div>
            </details>
        </div>

        <div class="dede-line">
            <span>With a Built-In Epistemic Anti-Coherence Loop</span>

            <details class="dede-help">
                <summary>?</summary>
                <div class="dede-help-text">
                    DeDe’s Epistemic Anti-Coherence Loop is designed to prevent
                    internally coherent reasoning from becoming a closed
                    system. It examines assumptions, reductions, blind spots,
                    insufficiently grounded claims, and excessive certainty
                    to keep conclusions open to evidence, revision, and
                    alternative interpretations.
                </div>
            </details>
        </div>

    </div>

    <p class="dede-subtitle">
        A little more time to respond—for greater accuracy,
        privacy, and security.
    </p>
        """
    )
)

# --------------------------------------------------
# DeDe Sidebar Configuration
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚙️ DeDe Configuration")

    st.caption(
        "Identity, reasoning models and knowledge sources."
    )

    # --------------------------------------------------
    # Owner Identity
    # --------------------------------------------------

    st.markdown("### Identity")

    owner_id = st.text_input(
        "Owner ID",
        value=st.session_state.get("owner_id", ""),
        placeholder="Ex: nicolas, delia, test_user",
    )

    if owner_id:
        safe_owner_id = "".join(
            char for char in owner_id.lower().strip()
            if char.isalnum() or char in ["_", "-"]
        )

        if st.session_state.get("owner_id") != safe_owner_id:
            st.session_state.owner_id = safe_owner_id
            st.session_state.conversation_history = []
            st.session_state.engine = DoxaEnginePhase2(
                user_id=safe_owner_id,
            )
            st.success(
                f"Memory owner set to: {safe_owner_id}"
            )
    else:
        st.warning(
            "Enter an Owner ID to use an isolated persistent memory."
        )
        st.stop()

    # --------------------------------------------------
    # Memory Privacy
    # --------------------------------------------------
    
    st.markdown("### Memory Privacy")
    
    memory_mode_labels = {
        "off": "Off — No memory",
        "session": "Session Only — Temporary",
        "selective": "Selective — Ask before saving",
        "continuous": "Continuous — Automatic",
    }
    
    current_memory_mode = st.session_state.get(
        "memory_storage_mode",
        "selective",
    )
    
    if current_memory_mode not in memory_mode_labels:
        current_memory_mode = "selective"
    
    memory_storage_mode = st.selectbox(
        "Memory Storage",
        options=list(memory_mode_labels.keys()),
        index=list(
            memory_mode_labels.keys()
        ).index(current_memory_mode),
        format_func=lambda mode: (
            memory_mode_labels[mode]
        ),
        key="memory_storage_mode",
    )
    
    if memory_storage_mode == "off":
        st.caption(
            "No session or persistent memory is authorized."
        )
    
    elif memory_storage_mode == "session":
        st.caption(
            "Memory remains available only during "
            "the current session."
        )
    
    elif memory_storage_mode == "selective":
        st.caption(
            "DeDe asks for confirmation before "
            "saving durable information."
        )
    
    else:
        st.caption(
            "DeDe may save relevant durable information "
            "automatically according to its privacy policy."
        )

    # --------------------------------------------------
    # Delete Persistent Memory
    # --------------------------------------------------

    with st.expander(
        "🗑️ Delete Persistent Memory",
        expanded=False,
    ):
        st.warning(
            "This permanently deletes the active "
            "durable memory stored by DeDe. "
            "Downloaded backups are not deleted."
        )

        confirm_memory_deletion = st.checkbox(
            "I understand that this cannot be undone",
            value=False,
            key="confirm_persistent_memory_deletion",
        )

        if st.button(
            "Delete Persistent Memory",
            key="delete_persistent_memory",
            use_container_width=True,
        ):
            if not confirm_memory_deletion:
                st.error(
                    "Confirm permanent deletion first."
                )

            else:
                st.session_state.engine.persistent_memory.clear_memory()

                st.session_state.conversation_history = []
                st.session_state.tool_history = []

                st.session_state.pop(
                    "pending_memory_candidate",
                    None,
                )

                st.session_state.pop(
                    "prepared_memory_export",
                    None,
                )

                st.session_state.pop(
                    "voice_text",
                    None,
                )

                st.session_state.engine = (
                    DoxaEnginePhase2(
                        user_id=(
                            st.session_state.owner_id
                        ),
                    )
                )

                st.success(
                    "Persistent memory deleted. "
                    "DeDe now has a fresh memory."
                )

    # --------------------------------------------------
    # Memory Manager
    # --------------------------------------------------

    with st.expander(
        "🧠 Manage Memories",
        expanded=False,
    ):
        memory_manager_notice = (
            st.session_state.pop(
                "memory_manager_notice",
                None,
            )
        )

        if memory_manager_notice:
            st.success(
                memory_manager_notice
            )

        managed_memory = (
            st.session_state.engine
            .persistent_memory
            .get_memory()
        )

        managed_items = managed_memory.get(
            "memory_items",
            [],
        )

        if not isinstance(
            managed_items,
            list,
        ):
            managed_items = []

        custom_folders = managed_memory.get(
            "memory_folders",
            [],
        )

        if not isinstance(
            custom_folders,
            list,
        ):
            custom_folders = []

        st.caption(
            f"{len(managed_items)} durable "
            "memory item(s)"
        )

        # ----------------------------------------------
        # Create a personal folder
        # ----------------------------------------------

        st.markdown(
            "#### Personal folders"
        )

        new_folder_name = st.text_input(
            "New folder name",
            key="new_memory_folder_name",
            placeholder=(
                "Example: Family, Book, Health..."
            ),
        )

        if st.button(
            "Create Folder",
            key="create_memory_folder",
            use_container_width=True,
        ):
            creation_result = (
                st.session_state.engine
                .persistent_memory
                .create_memory_folder(
                    new_folder_name
                )
            )

            if creation_result.get(
                "created",
                False,
            ):
                st.session_state[
                    "memory_manager_notice"
                ] = (
                    "Memory folder created."
                )

                st.rerun()

            else:
                st.error(
                    creation_result.get(
                        "error",
                        "The folder could not be created.",
                    )
                )

        # ----------------------------------------------
        # Automatic folders
        # ----------------------------------------------

        automatic_folders = {
            "👤 Identity & Preferences": {
                "identity",
                "preference",
                "personal_fact",
            },
            "📁 Projects & Decisions": {
                "project",
                "decision",
            },
            "👥 People & Relationships": {
                "relationship",
            },
            "📖 Personal History": {
                "autobiographical",
            },
            "🤖 DeDe Identity": {
                "assistant_identity",
            },
            "📦 Other Memories": {
                "interaction_note",
                "temporary_task",
                "unknown",
            },
        }

        custom_folder_names = {}

        for folder in custom_folders:
            if not isinstance(
                folder,
                dict,
            ):
                continue

            folder_id = str(
                folder.get(
                    "folder_id",
                    "",
                )
            ).strip()

            folder_name = str(
                folder.get(
                    "name",
                    "",
                )
            ).strip()

            if folder_id and folder_name:
                custom_folder_names[
                    folder_id
                ] = folder_name

        folder_contents = {}

        for folder_name in automatic_folders:
            folder_key = (
                f"automatic:{folder_name}"
            )

            folder_contents[
                folder_key
            ] = []

        for (
            folder_id,
            folder_name,
        ) in custom_folder_names.items():
            folder_key = (
                f"custom:{folder_id}"
            )

            folder_contents[
                folder_key
            ] = []

        for memory_item in managed_items:
            if not isinstance(
                memory_item,
                dict,
            ):
                continue

            assigned_folder_id = str(
                memory_item.get(
                    "folder_id",
                    "",
                )
                or ""
            ).strip()

            custom_folder_key = (
                f"custom:{assigned_folder_id}"
            )

            if (
                assigned_folder_id
                and custom_folder_key
                in folder_contents
            ):
                folder_contents[
                    custom_folder_key
                ].append(
                    memory_item
                )

                continue

            memory_type = str(
                memory_item.get(
                    "memory_type",
                    "unknown",
                )
            ).strip().lower()

            automatic_folder_name = (
                "📦 Other Memories"
            )

            for (
                folder_name,
                accepted_types,
            ) in automatic_folders.items():
                if (
                    memory_type
                    in accepted_types
                ):
                    automatic_folder_name = (
                        folder_name
                    )
                    break

            automatic_folder_key = (
                "automatic:"
                f"{automatic_folder_name}"
            )

            folder_contents[
                automatic_folder_key
            ].append(
                memory_item
            )

        # ----------------------------------------------
        # Folder selector
        # ----------------------------------------------

        folder_labels = []
        folder_lookup = {}

        for folder_name in automatic_folders:
            folder_key = (
                f"automatic:{folder_name}"
            )

            folder_count = len(
                folder_contents.get(
                    folder_key,
                    [],
                )
            )

            folder_label = (
                f"{folder_name} "
                f"({folder_count})"
            )

            folder_labels.append(
                folder_label
            )

            folder_lookup[
                folder_label
            ] = folder_key

        for (
            folder_id,
            folder_name,
        ) in custom_folder_names.items():
            folder_key = (
                f"custom:{folder_id}"
            )

            folder_count = len(
                folder_contents.get(
                    folder_key,
                    [],
                )
            )

            folder_label = (
                f"🗂️ {folder_name} "
                f"({folder_count})"
            )

            folder_labels.append(
                folder_label
            )

            folder_lookup[
                folder_label
            ] = folder_key

        selected_folder_label = st.selectbox(
            "Memory folder",
            folder_labels,
            key="selected_memory_folder",
        )

        selected_folder_key = folder_lookup[
            selected_folder_label
        ]

        selected_items = folder_contents.get(
            selected_folder_key,
            [],
        )

        # ----------------------------------------------
        # Delete a personal folder
        # ----------------------------------------------

        if selected_folder_key.startswith(
            "custom:"
        ):
            selected_custom_folder_id = (
                selected_folder_key.split(
                    ":",
                    1,
                )[1]
            )

            if st.button(
                "Delete This Folder",
                key=(
                    "delete_memory_folder_"
                    f"{selected_custom_folder_id}"
                ),
                use_container_width=True,
            ):
                folder_deletion_result = (
                    st.session_state.engine
                    .persistent_memory
                    .delete_memory_folder(
                        selected_custom_folder_id
                    )
                )

                if folder_deletion_result.get(
                    "deleted",
                    False,
                ):
                    moved_item_count = (
                        folder_deletion_result.get(
                            "moved_item_count",
                            0,
                        )
                    )

                    st.session_state[
                        "memory_manager_notice"
                    ] = (
                        "Folder deleted. "
                        f"{moved_item_count} memory "
                        "item(s) returned to their "
                        "automatic folder."
                    )

                    st.rerun()

                else:
                    st.error(
                        "Memory folder was not found."
                    )

        # ----------------------------------------------
        # Selected folder contents
        # ----------------------------------------------

        if not selected_items:
            st.info(
                "This memory folder is empty."
            )

        for memory_item in selected_items:
            memory_id = str(
                memory_item.get(
                    "memory_id",
                    "",
                )
            ).strip()

            memory_type = str(
                memory_item.get(
                    "memory_type",
                    "unknown",
                )
            )

            memory_content = str(
                memory_item.get(
                    "content",
                    "",
                )
            ).strip()

            storage_scope = str(
                memory_item.get(
                    "storage_scope",
                    "persistent",
                )
            )

            sensitivity = str(
                memory_item.get(
                    "sensitivity",
                    "medium",
                )
            )

            created_at = str(
                memory_item.get(
                    "created_at",
                    "",
                )
            )

            current_folder_id = str(
                memory_item.get(
                    "folder_id",
                    "",
                )
                or ""
            ).strip()

            with st.container(
                border=True,
            ):
                st.markdown(
                    f"**{memory_type}**"
                )

                st.write(
                    memory_content
                )

                st.caption(
                    f"Scope: {storage_scope} | "
                    f"Sensitivity: {sensitivity}"
                )

                if created_at:
                    st.caption(
                        "Created: "
                        f"{created_at[:19]}"
                    )

                if custom_folder_names:
                    move_labels = [
                        "Automatic folder",
                    ]

                    move_lookup = {
                        "Automatic folder": None,
                    }

                    current_move_index = 0

                    for (
                        folder_id,
                        folder_name,
                    ) in custom_folder_names.items():
                        move_label = (
                            f"🗂️ {folder_name}"
                        )

                        move_labels.append(
                            move_label
                        )

                        move_lookup[
                            move_label
                        ] = folder_id

                        if (
                            folder_id
                            == current_folder_id
                        ):
                            current_move_index = (
                                len(
                                    move_labels
                                )
                                - 1
                            )

                    selected_move_label = (
                        st.selectbox(
                            "Move to folder",
                            move_labels,
                            index=(
                                current_move_index
                            ),
                            key=(
                                "move_memory_select_"
                                f"{memory_id}"
                            ),
                        )
                    )

                    if st.button(
                        "Move Memory",
                        key=(
                            "move_memory_button_"
                            f"{memory_id}"
                        ),
                        use_container_width=True,
                    ):
                        move_result = (
                            st.session_state.engine
                            .persistent_memory
                            .move_memory_item(
                                memory_id=memory_id,
                                folder_id=(
                                    move_lookup[
                                        selected_move_label
                                    ]
                                ),
                            )
                        )

                        if move_result.get(
                            "moved",
                            False,
                        ):
                            st.session_state[
                                "memory_manager_notice"
                            ] = (
                                "Memory moved successfully."
                            )

                            st.rerun()

                        else:
                            st.error(
                                "The memory could not "
                                "be moved."
                            )

                if st.button(
                    "Delete Memory",
                    key=(
                        "delete_memory_item_"
                        f"{memory_id}"
                    ),
                    use_container_width=True,
                ):
                    deletion_result = (
                        st.session_state.engine
                        .persistent_memory
                        .delete_memory_item(
                            memory_id
                        )
                    )

                    if deletion_result.get(
                        "deleted",
                        False,
                    ):
                        st.session_state[
                            "memory_manager_notice"
                        ] = (
                            "Memory deleted successfully."
                        )

                        st.rerun()

                    else:
                        st.error(
                            "Memory item was not found."
                        )

        # ----------------------------------------------
        # Image Memories
        # ----------------------------------------------

        st.divider()

        st.markdown(
            "#### 🖼️ Image Memories"
        )

        remembered_images = (
            st.session_state.engine
            .image_memory
            .list_images()
        )

        st.caption(
            f"{len(remembered_images)} "
            "remembered image(s)"
        )

        image_folder_labels = [
            "🖼️ All Images",
            "📥 Unfiled Images",
        ]

        image_folder_lookup = {
            "🖼️ All Images": None,
            "📥 Unfiled Images": "",
        }

        for (
            folder_id,
            folder_name,
        ) in custom_folder_names.items():
            folder_label = (
                f"📁 {folder_name}"
            )

            image_folder_labels.append(
                folder_label
            )

            image_folder_lookup[
                folder_label
            ] = folder_id

        selected_image_folder_label = (
            st.selectbox(
                "Image folder",
                image_folder_labels,
                key=(
                    "selected_image_"
                    "memory_folder"
                ),
            )
        )

        selected_image_folder_id = (
            image_folder_lookup[
                selected_image_folder_label
            ]
        )

        visible_images = []

        for remembered_image in (
            remembered_images
        ):
            if not isinstance(
                remembered_image,
                dict,
            ):
                continue

            assigned_folder_id = str(
                remembered_image.get(
                    "folder_id",
                    "",
                )
                or ""
            ).strip()

            if (
                selected_image_folder_id
                is None
            ):
                visible_images.append(
                    remembered_image
                )

            elif (
                assigned_folder_id
                == selected_image_folder_id
            ):
                visible_images.append(
                    remembered_image
                )

        if not remembered_images:

            st.info(
                "No persistent image memory yet."
            )

        elif not visible_images:

            st.info(
                "This image folder is empty."
            )

        for remembered_image in visible_images:

            if not isinstance(
                remembered_image,
                dict,
            ):
                continue

            remembered_image_id = str(
                remembered_image.get(
                    "image_id",
                    "",
                )
                or ""
            ).strip()

            remembered_label = str(
                remembered_image.get(
                    "label",
                    "",
                )
                or remembered_image.get(
                    "original_name",
                    "",
                )
                or remembered_image_id
            ).strip()

            remembered_description = str(
                remembered_image.get(
                    "description",
                    "",
                )
                or ""
            ).strip()

            image_result = (
                st.session_state.engine
                .image_memory
                .get_image(
                    remembered_image_id
                )
            )

            with st.container(
                border=True,
            ):

                st.markdown(
                    f"**{remembered_label}**"
                )

                if (
                    image_result.get(
                        "status"
                    )
                    == "success"
                ):

                    remembered_bytes = (
                        image_result.get(
                            "image_bytes",
                            b"",
                        )
                    )

                    if remembered_bytes:

                        st.image(
                            remembered_bytes,
                            width="stretch",
                        )

                if remembered_description:

                    st.caption(
                        remembered_description
                    )

                st.caption(
                    "Image ID: "
                    f"{remembered_image_id}"
                )

                activate_image = st.button(
                    "📌 Use as active reference",
                    key=(
                        "activate_memory_image_"
                        f"{remembered_image_id}"
                    ),
                    use_container_width=True,
                )

                if activate_image:

                    if (
                        image_result.get(
                            "status"
                        )
                        == "success"
                    ):

                        st.session_state[
                            "active_chat_image"
                        ] = {
                            "name": remembered_image.get(
                                "original_name",
                                remembered_label,
                            ),
                            "mime_type": remembered_image.get(
                                "mime_type",
                                "image/jpeg",
                            ),
                            "image_bytes": (
                                image_result.get(
                                    "image_bytes",
                                    b"",
                                )
                            ),
                            "memory_image_id": (
                                remembered_image_id
                            ),
                        }

                        st.session_state[
                            "active_image_analysis"
                        ] = {
                            "filename": remembered_image.get(
                                "original_name",
                                remembered_label,
                            ),
                            "analysis": (
                                remembered_description
                            ),
                            "provider": (
                                "persistent_image_memory"
                            ),
                            "model": "",
                        }

                        st.session_state[
                            "memory_manager_notice"
                        ] = (
                            "Image activated as "
                            "visual reference."
                        )

                        st.rerun()

                delete_image = st.button(
                    "🗑️ Delete Image Memory",
                    key=(
                        "delete_memory_image_"
                        f"{remembered_image_id}"
                    ),
                    use_container_width=True,
                )

                if delete_image:

                    delete_result = (
                        st.session_state.engine
                        .image_memory
                        .delete_image(
                            remembered_image_id
                        )
                    )

                    if (
                        delete_result.get(
                            "status"
                        )
                        == "success"
                    ):

                        st.session_state[
                            "memory_manager_notice"
                        ] = (
                            "Image memory deleted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            delete_result.get(
                                "error",
                                (
                                    "Image memory "
                                    "could not be deleted."
                                ),
                            )
                        )


    # --------------------------------------------------
    # Portable Memory
    # --------------------------------------------------

    with st.expander(
        "🧠 Memory Backup",
        expanded=False,
    ):
        current_memory_data = (
            st.session_state.engine
            .persistent_memory
            .get_memory()
        )

        memory_item_count = len(
            current_memory_data.get(
                "memory_items",
                [],
            )
        )

        st.caption(
            f"Durable memories: {memory_item_count}"
        )

        def activate_restored_memory(
            memory_data: dict,
        ) -> None:
            st.session_state.engine.persistent_memory.restore_memory(
                memory_data
            )

            st.session_state.conversation_history = []
            st.session_state.tool_history = []

            st.session_state.pop(
                "pending_memory_candidate",
                None,
            )

            st.session_state.pop(
                "prepared_memory_export",
                None,
            )

            st.session_state.engine = (
                DoxaEnginePhase2(
                    user_id=(
                        st.session_state.owner_id
                    ),
                )
            )

        # ----------------------------------------------
        # Simple backup
        # ----------------------------------------------

        st.markdown(
            "#### Simple backup"
        )

        simple_memory_export = (
            st.session_state
            .memory_portability
            .export_simple(
                memory_data=(
                    current_memory_data
                ),
                user_id=(
                    st.session_state.owner_id
                ),
            )
        )

        st.download_button(
            label="Download Memory",
            data=simple_memory_export,
            file_name=(
                f"{st.session_state.owner_id}"
                ".dede-memory.json"
            ),
            mime="application/json",
            key="download_simple_memory",
            use_container_width=True,
        )

        # ----------------------------------------------
        # Complete memory backup
        # ----------------------------------------------

        complete_image_items = (
            st.session_state.engine
            .image_memory
            .list_images()
        )

        complete_image_files = []

        for image_item in (
            complete_image_items
        ):
            if not isinstance(
                image_item,
                dict,
            ):
                continue

            image_id = str(
                image_item.get(
                    "image_id",
                    "",
                )
            ).strip()

            if not image_id:
                continue

            image_result = (
                st.session_state.engine
                .image_memory
                .get_image(
                    image_id
                )
            )

            if image_result.get(
                "status"
            ) != "success":
                continue

            image_bytes = (
                image_result.get(
                    "image_bytes",
                    b"",
                )
            )

            file_name = str(
                image_item.get(
                    "file_name",
                    "",
                )
            ).strip()

            if (
                not image_bytes
                or not file_name
            ):
                continue

            complete_image_files.append(
                {
                    "file_name": (
                        file_name
                    ),
                    "image_bytes": (
                        image_bytes
                    ),
                }
            )

        try:
            complete_memory_export = (
                st.session_state
                .memory_portability
                .export_complete(
                    memory_data=(
                        current_memory_data
                    ),
                    image_items=(
                        complete_image_items
                    ),
                    image_files=(
                        complete_image_files
                    ),
                    user_id=(
                        st.session_state
                        .owner_id
                    ),
                )
            )

            st.download_button(
                label=(
                    "Download Complete Memory"
                ),
                data=(
                    complete_memory_export
                ),
                file_name=(
                    f"{st.session_state.owner_id}"
                    ".dede-archive.zip"
                ),
                mime="application/zip",
                key=(
                    "download_complete_memory"
                ),
                use_container_width=True,
            )

            st.caption(
                "Includes saved responses, "
                "folders, image metadata and "
                "the original image files."
            )

        except ValueError as error:
            st.error(
                str(error)
            )

        except Exception:
            st.error(
                "Complete memory export "
                "could not be prepared."
            )

        st.caption(
            "No password required. Anyone with access "
            "to this file can read its contents."
        )

        simple_memory_file = st.file_uploader(
            "Select a simple memory backup",
            type=[
                "json",
            ],
            key="restore_simple_memory_file",
        )

        if st.button(
            "Restore Memory",
            key="restore_simple_memory",
            use_container_width=True,
        ):
            if simple_memory_file is None:
                st.error(
                    "Select a DeDe memory backup."
                )

            else:
                try:
                    simple_result = (
                        st.session_state
                        .memory_portability
                        .import_simple(
                            memory_file=(
                                simple_memory_file
                                .getvalue()
                            ),
                        )
                    )

                    activate_restored_memory(
                        simple_result.get(
                            "memory",
                            {},
                        )
                    )

                    st.success(
                        "Memory restored successfully."
                    )

                except ValueError as error:
                    st.error(
                        str(error)
                    )

                except Exception:
                    st.error(
                        "Memory restoration failed."
                    )

        st.caption(
            "Restoring replaces the current durable "
            "memory and clears the temporary conversation."
        )

        st.divider()

        # ----------------------------------------------
        # Private encrypted backup
        # ----------------------------------------------

        st.markdown(
            "#### 🔐 Private encrypted backup"
        )

        st.caption(
            "Optional protection for personal or "
            "sensitive memory."
        )

        export_password = st.text_input(
            "Export password",
            type="password",
            key="memory_export_password",
            help=(
                "Use at least 8 characters. "
                "DeDe does not store this password."
            ),
        )

        confirm_export_password = st.text_input(
            "Confirm export password",
            type="password",
            key="memory_export_password_confirm",
        )

        if st.button(
            "Prepare encrypted memory",
            key="prepare_encrypted_memory",
            use_container_width=True,
        ):
            if (
                export_password
                != confirm_export_password
            ):
                st.error(
                    "The two passwords do not match."
                )

            elif len(
                export_password
            ) < 8:
                st.error(
                    "Use a password containing "
                    "at least 8 characters."
                )

            else:
                try:
                    encrypted_memory = (
                        st.session_state
                        .memory_portability
                        .export_encrypted(
                            memory_data=(
                                current_memory_data
                            ),
                            user_id=(
                                st.session_state
                                .owner_id
                            ),
                            password=export_password,
                        )
                    )

                    st.session_state[
                        "prepared_memory_export"
                    ] = encrypted_memory

                    st.success(
                        "Encrypted memory prepared."
                    )

                except ValueError as error:
                    st.error(
                        str(error)
                    )

        prepared_memory_export = (
            st.session_state.get(
                "prepared_memory_export"
            )
        )

        if isinstance(
            prepared_memory_export,
            bytes,
        ):
            st.download_button(
                label="Download Private Memory",
                data=prepared_memory_export,
                file_name=(
                    f"{st.session_state.owner_id}"
                    ".dede-memory"
                ),
                mime="application/octet-stream",
                key="download_private_memory",
                use_container_width=True,
            )

            st.caption(
                "Keep the file and password separately. "
                "A forgotten password cannot be recovered."
            )

        st.markdown(
            "##### Restore private memory"
        )

        imported_private_file = st.file_uploader(
            "Select a .dede-memory file",
            type=[
                "dede-memory",
            ],
            key="import_private_memory_file",
        )

        import_password = st.text_input(
            "Import password",
            type="password",
            key="memory_import_password",
        )

        confirm_private_replacement = st.checkbox(
            "Replace current memory with this private backup",
            value=False,
            key="confirm_private_memory_replacement",
        )

        if st.button(
            "Restore Private Memory",
            key="restore_encrypted_memory",
            use_container_width=True,
        ):
            if imported_private_file is None:
                st.error(
                    "Select a .dede-memory file."
                )

            elif not import_password:
                st.error(
                    "Enter the memory password."
                )

            elif not confirm_private_replacement:
                st.error(
                    "Confirm replacement of the "
                    "current durable memory."
                )

            else:
                try:
                    private_result = (
                        st.session_state
                        .memory_portability
                        .import_encrypted(
                            encrypted_file=(
                                imported_private_file
                                .getvalue()
                            ),
                            password=import_password,
                        )
                    )

                    activate_restored_memory(
                        private_result.get(
                            "memory",
                            {},
                        )
                    )

                    st.success(
                        "Private memory restored "
                        "successfully."
                    )

                except ValueError as error:
                    st.error(
                        str(error)
                    )

                except Exception:
                    st.error(
                        "Private memory restoration failed."
                    )


    # --------------------------------------------------
    # Conversation Session
    # --------------------------------------------------

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "engine" not in st.session_state and st.session_state.get("owner_id"):
        st.session_state.engine = DoxaEnginePhase2(
            user_id=st.session_state.owner_id,
        )

    if st.button(
        "Reset Conversation",
        key="reset_current_conversation",
        use_container_width=True,
    ):
        st.session_state.conversation_history = []
        st.session_state.tool_history = []
    
        st.session_state.pop(
            "pending_memory_candidate",
            None,
        )
    
        st.session_state.pop(
            "voice_text",
            None,
        )
    
        st.session_state.engine = DoxaEnginePhase2(
            user_id=st.session_state.owner_id,
        )
    
        st.success(
            "Current conversation reset. "
            "Durable memory was preserved."
        )
    
        st.rerun()

    # --------------------------------------------------
    # Reasoning Models
    # --------------------------------------------------

    st.markdown("### Reasoning Models")

    enable_llm = True

    st.caption(
        "Choose which reasoning models DeDe may use."
    )

    llm_model_options = {
        "NVIDIA — Nemotron 3 Nano": "nvidia",
        "KIMI — Kimi K2.6": "kimi",
        "OpenAI": "openai",
        "Gemini": "gemini",
        "Mistral": "mistral",
        "DeepSeek — planned": "deepseek",
        "Qwen — planned": "qwen",
        "GLM — planned": "glm",
        "Claude — planned": "claude",
    }

    selected_llm_labels = st.multiselect(
        "Reasoning Models",
        list(llm_model_options.keys()),
        default=[
            "NVIDIA — Nemotron 3 Nano",
        ],
    )

    llm_providers = [
        llm_model_options[label]
        for label in selected_llm_labels
    ]

    llm_profile = "custom"

    connected_llms = [
        "openai",
        "gemini",
        "mistral",
        "kimi",
        "nvidia",
    ]

    active_llms = [
        provider
        for provider in llm_providers
        if provider in connected_llms
    ]

    planned_llms = [
        provider
        for provider in llm_providers
        if provider not in connected_llms
    ]

    st.caption(
        "Active: "
        + (
            ", ".join(active_llms)
            if active_llms
            else "none"
        )
        + " | Planned: "
        + (
            ", ".join(planned_llms)
            if planned_llms
            else "none"
        )
    )

    # --------------------------------------------------
    # Knowledge Sources
    # --------------------------------------------------

    st.markdown("### Knowledge Sources")

    st.caption(
        "Choose the knowledge profile and search strategy."
    )

    search_profile_labels = {
        "General — DuckDuckGo": "general",
        "Scientific — DuckDuckGo + ArXiv + CrossRef": "scientific",
        "Shopping — DuckDuckGo": "shopping",
        "News — DuckDuckGo": "news",
        "Programming — DuckDuckGo": "programming",
        "Legal — DuckDuckGo": "legal",
        "Custom": "custom",
    }

    selected_search_label = st.selectbox(
        "Knowledge Profile",
        list(search_profile_labels.keys()),
        index=0,
    )

    search_profile = search_profile_labels[selected_search_label]

    search_strategy = st.selectbox(
        "Search Strategy",
        [
            "Off",
            "Manual",
            "On Request",
            "Governor (Beta)",
        ],
        index=2,
    )

    st.caption(
        "Off: never search externally. "
        "Manual: search only when you explicitly activate it. "
        "On Request: search when semantic analysis detects that external information is needed. "
        "Governor: DeDe decides automatically when verification is beneficial."
    )

    search_mode_map = {
        "Off": "off",
        "Manual": "manual",
        "On Request": "on_request",
        "Governor (Beta)": "governor",
    }

    search_mode = search_mode_map[search_strategy]

    search_provider = []

    if search_profile == "custom":

        search_provider = st.multiselect(
            "Custom Search Providers",
            [
                "duckduckgo",
                "arxiv",
                "crossref",
                "brave — planned",
                "serpapi — planned",
                "pubmed — planned",
                "github — planned",
                "newsapi — planned",
                "semantic_scholar — planned",
                "eur_lex — planned",
            ],
            default=[
                "duckduckgo",
            ],
        )

        search_provider = [
            item.replace(" — planned", "")
            for item in search_provider
        ]

    # --------------------------------------------------
    # Semantic Dictionaries
    # --------------------------------------------------

    st.markdown("### Semantic Dictionaries")

    st.caption(
        "Choose one or several knowledge dictionaries."
    )

    knowledge_provider_labels = {
        "Local Knowledge": "local",
        "DeDe Foundational Knowledge": "foundational",
    }

    selected_knowledge_labels = st.multiselect(
        "Knowledge Dictionaries",
        list(knowledge_provider_labels.keys()),
        default=[
            "Local Knowledge",
            "DeDe Foundational Knowledge",
        ],
        key="knowledge_dictionary_selection",
    )

    knowledge_providers = [
        knowledge_provider_labels[label]
        for label in selected_knowledge_labels
    ]

    if not knowledge_providers:
        knowledge_providers = [
            "foundational",
        ]

        st.caption(
            "DeDe Foundational Knowledge remains active "
            "when no dictionary is selected."
        )

    knowledge_mode_labels = {
        "Best Source": "best",
        "Combine Selected Sources": "combine",
    }

    selected_knowledge_mode = st.selectbox(
        "Knowledge Mode",
        list(knowledge_mode_labels.keys()),
        index=0,
        key="knowledge_dictionary_mode",
    )

    knowledge_mode = knowledge_mode_labels[
        selected_knowledge_mode
    ]

    st.caption(
        "Planned: Wiktionary, WordNet, ConceptNet."
    )

# --------------------------------------------------
# DeDe Tools Panels
# --------------------------------------------------

render_image_generators_panel(
    tool_manager=st.session_state.tool_manager,
    save_control=render_image_save_control,
)

render_video_studio_panel(
    tool_manager=st.session_state.tool_manager,
)

render_free_video_maker_panel(
    tool_manager=st.session_state.tool_manager,
)

render_document_studio_panel(
    tool_manager=st.session_state.tool_manager,
)

render_text_creator_launcher()

text_creator_request = (
    render_text_creator_workspace()
)

if text_creator_request:
    requested_language = (
        text_creator_request.get(
            "language",
            "Automatic",
        )
    )

    if requested_language == "Automatic":
        language_instruction = (
            "Infer the appropriate output language "
            "from the title and instruction."
        )

    else:
        language_instruction = (
            "Write the complete text in "
            f"{requested_language}."
        )

    text_creator_prompt = (
        "You are DeDe's Text Creator.\n\n"
        "Create a finished text using these "
        "requirements:\n"
        f"- Title: "
        f"{text_creator_request.get('title', '')}\n"
        f"- Text type: "
        f"{text_creator_request.get('text_type', '')}\n"
        f"- Tone: "
        f"{text_creator_request.get('tone', '')}\n"
        f"- Length: "
        f"{text_creator_request.get('length', '')}\n"
        f"- Language: {requested_language}\n"
        f"- Instruction: "
        f"{text_creator_request.get('instruction', '')}\n\n"
        f"{language_instruction}\n"
        "Return only the finished text. "
        "Do not add introductory commentary."
    )

    try:
        with st.spinner(
            "DeDe is creating the draft..."
        ):
            text_creator_result = (
                st.session_state.engine
                .llm_engine
                .ask(
                    prompt=text_creator_prompt,
                    profile="fast",
                    providers=llm_providers,
                    enabled=enable_llm,
                )
            )

        generated_text = str(
            text_creator_result.get(
                "response",
                "",
            )
            or ""
        ).strip()

        if generated_text:
            st.session_state[
                "text_creator_content"
            ] = generated_text

            st.rerun()

        else:
            st.error(
                "DeDe did not generate a draft."
            )

    except Exception as error:
        st.error(
            "Text creation failed: "
            f"{error}"
        )

text_creator_content = str(
    st.session_state.get(
        "text_creator_content",
        "",
    )
    or ""
).strip()

if (
    st.session_state.get(
        "text_creator_open",
        False,
    )
    and text_creator_content
):
    render_message_save_control(
        message_text=text_creator_content,
        control_key="text_creator_content",
    )
    
    if st.button(
        "🎨 Create Image Prompt",
        key=(
            "text_creator_"
            "create_image_prompt"
        ),
        use_container_width=True,
    ):
        image_prompt_instruction = (
            "Transform the following text into one "
            "concise, detailed image-generation "
            "prompt in English.\n\n"
            "Select the most visually representative "
            "scene, subject or atmosphere.\n"
            "Describe the subject, environment, "
            "composition, lighting, colors, mood "
            "and visual style.\n"
            "Do not retell or reproduce the story.\n"
            "Create a single visual scene of no more "
            "than 120 words.\n"
            "Return only the image prompt, without "
            "commentary or quotation marks.\n\n"
            "Title: "
            f"{st.session_state.get(
                'text_creator_title',
                ''
            )}\n\n"
            "Text:\n"
            f"{text_creator_content[:12000]}"
        )

        try:
            with st.spinner(
                "DeDe is creating the "
                "image prompt..."
            ):
                image_prompt_result = (
                    st.session_state.engine
                    .llm_engine
                    .ask(
                        prompt=(
                            image_prompt_instruction
                        ),
                        profile="fast",
                        providers=llm_providers,
                        enabled=enable_llm,
                    )
                )

            generated_image_prompt = str(
                image_prompt_result.get(
                    "response",
                    "",
                )
                or ""
            ).strip()

            if len(generated_image_prompt) > 1600:
                generated_image_prompt = (
                    generated_image_prompt[
                        :1600
                    ]
                    .rsplit(
                        " ",
                        1,
                    )[0]
                    .strip()
                )

            if generated_image_prompt:
                st.session_state[
                    "pending_image_generator_prompt"
                ] = generated_image_prompt

                st.session_state[
                    "open_image_generators_panel"
                ] = True

                st.rerun()

            else:
                st.error(
                    "DeDe did not create "
                    "an image prompt."
                )

        except Exception as error:
            st.error(
                "Image prompt creation failed: "
                f"{error}"
            )

render_coding_studio_launcher()

coding_studio_request = (
    render_coding_studio_workspace(
        save_control=(
            render_message_save_control
        ),
    )
)

coding_studio_action = str(
    (
        coding_studio_request
        or {}
    ).get(
        "action",
        "",
    )
)

if (
    coding_studio_action
    == "connect_github_repository"
):
    github_reader = GitHubReadOnly()

    github_result = (
        github_reader.list_files(
            owner=(
                coding_studio_request.get(
                    "owner",
                    "",
                )
            ),
            repository=(
                coding_studio_request.get(
                    "repository",
                    "",
                )
            ),
            branch=(
                coding_studio_request.get(
                    "branch",
                    "main",
                )
            ),
        )
    )

    if github_result.get(
        "status"
    ) == "success":
        github_file_paths = sorted(
            [
                str(
                    item.get(
                        "path",
                        "",
                    )
                )
                for item in (
                    github_result.get(
                        "files",
                        [],
                    )
                )
                if item.get(
                    "path"
                )
            ]
        )

        st.session_state[
            "coding_github_files"
        ] = github_file_paths

        st.session_state[
            "coding_studio_result"
        ] = ""

        st.session_state[
            "coding_github_status"
        ] = (
            "Connected in read-only mode: "
            f"{len(github_file_paths)} "
            "file(s) available."
        )

    else:
        st.session_state[
            "coding_github_files"
        ] = []

        st.session_state[
            "coding_github_status"
        ] = str(
            github_result.get(
                "error",
                "GitHub connection failed.",
            )
        )

    st.rerun()

if (
    coding_studio_action
    == "load_github_file"
):
    github_reader = GitHubReadOnly()

    github_file_result = (
        github_reader.read_file(
            owner=(
                coding_studio_request.get(
                    "owner",
                    "",
                )
            ),
            repository=(
                coding_studio_request.get(
                    "repository",
                    "",
                )
            ),
            file_path=(
                coding_studio_request.get(
                    "file_path",
                    "",
                )
            ),
            branch=(
                coding_studio_request.get(
                    "branch",
                    "main",
                )
            ),
        )
    )

    if github_file_result.get(
        "status"
    ) == "success":
        loaded_file_path = str(
            github_file_result.get(
                "path",
                "",
            )
        )

        st.session_state[
            "coding_studio_pending_source"
        ] = str(
            github_file_result.get(
                "content",
                "",
            )
        )

        st.session_state[
            "coding_studio_filename"
        ] = loaded_file_path

        st.session_state[
            "coding_studio_result"
        ] = ""

        st.session_state[
            "coding_github_status"
        ] = (
            "Loaded read-only file: "
            f"{loaded_file_path}"
        )

    else:
        st.session_state[
            "coding_github_status"
        ] = str(
            github_file_result.get(
                "error",
                "The file could not be read.",
            )
        )

    st.rerun()

if (
    coding_studio_request
    and coding_studio_action
    == "run_coding_task"
):
    coding_task = str(
        coding_studio_request.get(
            "task",
            "Generate code",
        )
    )

    coding_language = str(
        coding_studio_request.get(
            "language",
            "Automatic",
        )
    )

    code_producing_tasks = {
        "Generate code",
        "Modify code",
        "Debug an error",
        "Refactor code",
        "Create tests",
        "Convert code",
    }

    if coding_task in code_producing_tasks:
        output_instruction = (
            "Return only the complete resulting code. "
            "Do not use Markdown code fences. "
            "Do not omit unchanged sections. "
            "Do not add introductory commentary."
        )

    elif coding_task == "Review code":
        output_instruction = (
            "Return a structured code review with "
            "exactly these sections:\n"
            "1. Confirmed defects\n"
            "2. Potential risks\n"
            "3. Optional improvements\n"
            "4. Correct patterns to preserve\n\n"
            "Do not present a stylistic preference "
            "or negligible micro-optimization as "
            "a defect.\n"
            "Distinguish confirmed facts from "
            "inferences.\n"
            "Respect the lifecycle and state model "
            "of the framework being used.\n"
            "For Streamlit, do not recommend moving "
            "per-session state initialization to "
            "module import time.\n"
            "Treat repeated idempotent initialization "
            "at independent entry points as defensive "
            "unless it causes a demonstrated problem.\n"
            "Quote only the code fragments necessary "
            "to support each finding."
        )

    elif coding_task == "Explain code":
        output_instruction = (
            "Explain what the code actually does, "
            "its execution order, state changes and "
            "dependencies.\n"
            "Distinguish observed behavior from "
            "interpretation.\n"
            "Do not invent missing project context.\n"
            "Quote only the code fragments necessary "
            "to support the explanation."
        )

    else:
        output_instruction = (
            "Return a clear, structured analysis.\n"
            "Separate confirmed defects, potential "
            "risks and optional improvements.\n"
            "Do not describe harmless or defensive "
            "code as an error without demonstrating "
            "a concrete consequence."
        )

    coding_prompt = (
        "You are DeDe's Coding Studio.\n\n"
        "Complete the requested coding task "
        "accurately and conservatively.\n"
        "Preserve existing behavior unless the "
        "instruction explicitly requests a change.\n"
        "Do not invent missing APIs, functions or "
        "project files.\n\n"
        f"Task: {coding_task}\n"
        f"Programming language: {coding_language}\n"
        "File name: "
        f"{coding_studio_request.get(
            'filename',
            ''
        )}\n"
        "User instruction:\n"
        f"{coding_studio_request.get(
            'instruction',
            ''
        )}\n\n"
        "Error or traceback:\n"
        f"{coding_studio_request.get(
            'error',
            ''
        )}\n\n"
        "Source code:\n"
        "<<<SOURCE_CODE\n"
        f"{coding_studio_request.get(
            'source_code',
            ''
        )[:30000]}\n"
        "SOURCE_CODE\n\n"
        f"{output_instruction}"
    )

    try:
        with st.spinner(
            "DeDe is working on the code..."
        ):
            coding_result = (
                st.session_state.engine
                .llm_engine
                .ask(
                    prompt=coding_prompt,
                    profile="fast",
                    providers=llm_providers,
                    enabled=enable_llm,
                )
            )

        generated_code_result = str(
            coding_result.get(
                "response",
                "",
            )
            or ""
        ).strip()

        if (
            coding_task == "Review code"
            and generated_code_result
        ):
            review_verification_prompt = (
                "You are the verification stage of "
                "DeDe's Coding Studio.\n\n"
                "Audit the draft code review below "
                "against the actual source code.\n"
                "Remove every unsupported, impossible "
                "or merely stylistic finding.\n\n"
                "Mandatory technical facts:\n"
                "- dict.get(key, default) does not "
                "raise KeyError when the key is absent.\n"
                "- Repeated calls to one centralized, "
                "idempotent initializer do not duplicate "
                "the initialization logic.\n"
                "- Independent UI entry points may each "
                "defensively call that initializer.\n"
                "- Streamlit session-state initialization "
                "must not be moved to module import time.\n"
                "- A potential risk requires a concrete "
                "failure mechanism, not speculation.\n\n"
                "Return only the corrected final review "
                "with these sections:\n"
                "1. Confirmed defects\n"
                "2. Potential risks\n"
                "3. Optional improvements\n"
                "4. Correct patterns to preserve\n\n"
                "SOURCE CODE:\n"
                "<<<SOURCE\n"
                f"{coding_studio_request.get(
                    'source_code',
                    ''
                )[:30000]}\n"
                "SOURCE\n\n"
                "DRAFT REVIEW:\n"
                "<<<REVIEW\n"
                f"{generated_code_result}\n"
                "REVIEW"
            )

            verified_review_result = (
                st.session_state.engine
                .llm_engine
                .ask(
                    prompt=(
                        review_verification_prompt
                    ),
                    profile="fast",
                    providers=llm_providers,
                    enabled=enable_llm,
                )
            )

            verified_review = str(
                verified_review_result.get(
                    "response",
                    "",
                )
                or ""
            ).strip()

            if verified_review:
                generated_code_result = (
                    verified_review
                )

        if generated_code_result:
            st.session_state[
                "coding_studio_result"
            ] = generated_code_result

            st.rerun()

        else:
            st.error(
                "DeDe did not produce "
                "a coding result."
            )

    except Exception as error:
        st.error(
            "Coding task failed: "
            f"{error}"
        )

# --------------------------------------------------
# Chat Display
# --------------------------------------------------

for index, turn in enumerate(st.session_state.conversation_history):
    with st.chat_message("user"):
        st.write(turn.get("user_input", ""))

    with st.chat_message("assistant"):
    
        answer = turn.get("answer", "")
    
        st.write(answer)

        if answer:
            render_message_save_control(
                message_text=answer,
                control_key=(
                    f"history_{index}"
                ),
            )

            if st.button(
                "🔊 Listen",
                key=f"tts_history_{index}",
            ):
                audio = generate_speech(answer)
                st.audio(audio, format="audio/mp3")

# --------------------------------------------------
# Tool Conversation History
# --------------------------------------------------

history_image_tools = {
    "image_generator",
    "cloudflare_image_generator",
    "cloudflare_reference_image",
}

for index, item in enumerate(
    st.session_state.tool_history
):
    with st.chat_message("user"):
        st.write(
            item.get(
                "user_input",
                "",
            )
        )

    with st.chat_message("assistant"):
        tool_name = item.get(
            "tool_name",
            "",
        )

        tool_result = item.get(
            "tool_result",
            {},
        )

        tool_status = tool_result.get(
            "status",
            "error",
        )

        if tool_status != "success":
            st.error(
                tool_result.get(
                    "error",
                    "Tool execution failed.",
                )
                or "Tool execution failed."
            )

        elif tool_name in history_image_tools:
            image_data = tool_result.get(
                "data",
                {},
            )

            image_bytes = image_data.get(
                "image_bytes"
            )

            mime_type = image_data.get(
                "mime_type",
                "image/png",
            )

            extension = (
                "jpg"
                if mime_type == "image/jpeg"
                else "png"
            )

            provider = image_data.get(
                "provider",
                "AI",
            )

            if image_bytes:
                st.image(
                    image_bytes,
                    caption=(
                        "Generated by DeDe with "
                        f"{provider}"
                    ),
                    width="stretch",
                )

                image_file_name = (
                    "dede_generated_image_"
                    f"{index + 1}.{extension}"
                )

                st.download_button(
                    label=(
                        f"Download {extension.upper()}"
                    ),
                    data=image_bytes,
                    file_name=image_file_name,
                    mime=mime_type,
                    key=f"download_tool_image_{index}",
                )

                if st.button(
                    "🎞️ Add to Movie Maker",
                    key=(
                        "add_chat_image_to_"
                        f"movie_maker_{index}"
                    ),
                ):
                    image_added = (
                        _store_movie_maker_image(
                            image_bytes=bytes(
                                image_bytes
                            ),
                            name=image_file_name,
                            mime_type=mime_type,
                            source="DeDe chat",
                        )
                    )

                    if image_added:
                        st.success(
                            "Image added to "
                            "Movie Maker."
                        )
                    else:
                        st.info(
                            "This image is already "
                            "in Movie Maker."
                        )

                st.caption(
                    f"Provider: {provider} | Model: "
                    f"{image_data.get('model', 'unknown')}"
                )

            else:
                st.error(
                    "The saved tool result contains "
                    "no image data."
                )

        else:
            st.write(
                tool_result.get(
                    "summary",
                    "Tool executed successfully.",
                )
                or "Tool executed successfully."
            )
# --------------------------------------------------
# Voice Input / Speech to Text
# --------------------------------------------------

st.subheader("Voice input")

audio_value = st.audio_input(
    "Record a voice message",
    sample_rate=16000,
    key="voice_audio_input",
)

voice_text = ""

if audio_value:
    st.audio(audio_value)

    if st.button("Transcribe voice", key="transcribe_voice_button"):
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
        ) as tmp:
            tmp.write(audio_value.getvalue())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )

        voice_text = transcript.strip()

        st.session_state["voice_text"] = voice_text
        st.success("Voice transcribed.")
        st.write(voice_text)

# --------------------------------------------------
# Pending Memory Confirmation
# --------------------------------------------------

pending_memory = st.session_state.get(
    "pending_memory_candidate"
)

if isinstance(
    pending_memory,
    dict,
):
    pending_candidate = pending_memory.get(
        "candidate",
        {},
    )

    pending_content = str(
        pending_candidate.get(
            "content",
            "",
        )
    ).strip()

    if pending_content:
        with st.container(
            border=True,
        ):
            st.markdown(
                "#### 🧠 Memory permission"
            )

            st.write(
                "DeDe proposes remembering:"
            )

            st.info(
                pending_content
            )

            memory_type = pending_candidate.get(
                "memory_type",
                "unknown",
            )

            sensitivity = pending_candidate.get(
                "sensitivity",
                "medium",
            )

            proposed_scope = pending_candidate.get(
                "proposed_scope",
                "persistent",
            )

            st.caption(
                f"Type: {memory_type} | "
                f"Scope: {proposed_scope} | "
                f"Sensitivity: {sensitivity}"
            )

            save_memory_column, reject_memory_column = (
                st.columns(2)
            )

            with save_memory_column:
                save_memory = st.button(
                    "Save memory",
                    type="primary",
                    use_container_width=True,
                    key="approve_pending_memory",
                )

            with reject_memory_column:
                reject_memory = st.button(
                    "Do not save",
                    use_container_width=True,
                    key="reject_pending_memory",
                )

            if save_memory:
                current_storage_mode = (
                    st.session_state.get(
                        "memory_storage_mode",
                        "selective",
                    )
                )

                approved_governance = (
                    st.session_state.engine
                    .memory_governor
                    .evaluate(
                        text=pending_memory.get(
                            "text",
                            "",
                        ),
                        storage_mode=(
                            current_storage_mode
                        ),
                        candidate=(
                            pending_candidate
                        ),
                        user_approved=True,
                    )
                )

                if approved_governance.get(
                    "allow_persistent_storage",
                    False,
                ):
                    st.session_state.engine.persistent_memory.store_candidate(
                        candidate=(
                            approved_governance.get(
                                "candidate",
                                {},
                            )
                        ),
                        storage_scope=(
                            approved_governance.get(
                                "storage_scope",
                                "persistent",
                            )
                        ),
                    )

                    del st.session_state[
                        "pending_memory_candidate"
                    ]

                    st.success(
                        "Memory saved."
                    )

                    st.rerun()

                else:
                    del st.session_state[
                        "pending_memory_candidate"
                    ]

                    st.warning(
                        approved_governance.get(
                            "reason",
                            "Memory was not saved.",
                        )
                    )

            if reject_memory:
                del st.session_state[
                    "pending_memory_candidate"
                ]

                st.info(
                    "Memory was not saved."
                )

                st.rerun()
# --------------------------------------------------
# Image Upload for DeDe Vision
# --------------------------------------------------

uploaded_chat_image = st.file_uploader(
    "📷 Upload an image for DeDe to analyze",
    type=["png", "jpg", "jpeg", "webp"],
    key="dede_chat_image_upload",
)

if uploaded_chat_image is not None:

    uploaded_image_bytes = (
        uploaded_chat_image.getvalue()
    )

    st.session_state[
        "active_chat_image"
    ] = {
        "name": uploaded_chat_image.name,
        "mime_type": uploaded_chat_image.type,
        "image_bytes": uploaded_image_bytes,
    }


active_image_preview = (
    st.session_state.get(
        "active_chat_image",
        {},
    )
)

if active_image_preview:

    preview_bytes = (
        active_image_preview.get(
            "image_bytes",
            b"",
        )
    )

    if preview_bytes:

        st.image(
            preview_bytes,
            caption=(
                active_image_preview.get(
                    "name",
                    "DeDe image",
                )
            ),
            width="stretch",
        )

        st.success(
            "Image ready for DeDe."
        )
   
# --------------------------------------------------
# Cloudflare Vision Engine
# --------------------------------------------------

if "cloudflare_vision" not in st.session_state:
    st.session_state.cloudflare_vision = (
        CloudflareVision()
    )

# --------------------------------------------------
# Cloudflare Reference Image Engine
# --------------------------------------------------

if "cloudflare_reference_image" not in st.session_state:
    st.session_state.cloudflare_reference_image = (
        CloudflareReferenceImage()
    )

if "visual_prompt_compiler" not in st.session_state:
    st.session_state.visual_prompt_compiler = (
        VisualPromptCompiler()
    )
    
# --------------------------------------------------
# Permanent Image Save Control
# --------------------------------------------------

image_save_notice = (
    st.session_state.pop(
        "image_save_notice",
        None,
    )
)

if image_save_notice:
    st.success(
        image_save_notice
    )

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

typed_text = st.chat_input(
    "Message DeDe"
)

text = (
    typed_text
    or st.session_state.get(
        "voice_text",
        "",
    )
)

if text:
    st.session_state[
        "voice_text"
    ] = ""

original_user_text = text

# --------------------------------------------------
# Active Image Vision Analysis
# --------------------------------------------------

active_chat_image = st.session_state.get(
    "active_chat_image",
    {},
)

if text and active_chat_image:

    image_bytes = active_chat_image.get(
        "image_bytes",
        b"",
    )

    if image_bytes:

        vision_result = (
            st.session_state.cloudflare_vision.analyze(
                image_bytes=image_bytes,
                prompt=text,
                mime_type=active_chat_image.get(
                    "mime_type",
                    "image/jpeg",
                ),
            )
        )

        if vision_result.get("status") == "success":

            vision_analysis = vision_result.get(
                "analysis",
                "",
            )

            st.session_state[
                "active_image_analysis"
            ] = {
                "filename": active_chat_image.get(
                    "name",
                    "",
                ),
                "analysis": vision_analysis,
                "provider": vision_result.get(
                    "provider",
                    "cloudflare",
                ),
                "model": vision_result.get(
                    "model",
                    "",
                ),
            }

            text = (
                f"{text}\n\n"
                "Visual analysis supplied by "
                "DeDe Vision:\n"
                f"{vision_analysis}"
            )

        else:

            st.error(
                vision_result.get(
                    "error",
                    "Image analysis failed.",
                )
            )
            st.stop()

if text:
    response_timer_state = (
        start_response_timer()
    )

    available_tools = (
        st.session_state.tool_manager.available_tools()
    )

    active_tool_provider = (
        llm_providers[0]
        if llm_providers
        else ""
    )

    memory_context_started_at = (
        time.perf_counter()
    )

    working_memory_context = (
        st.session_state.engine
        .conversation_manager
        .build_context(
            st.session_state.conversation_history
        )
    )

    persistent_memory_context = (
        st.session_state.engine
        .persistent_memory
        .get_memory()
    )

    retrieved_durable_memory = (
        st.session_state.engine
        .memory_retriever
        .retrieve(
            text=text,
            persistent_memory=(
                persistent_memory_context
            ),
        )
    )

    working_memory_context[
        "durable_memory"
    ] = {
        "owner": retrieved_durable_memory.get(
            "owner",
            {},
        ),
        "core_memories": (
            retrieved_durable_memory.get(
                "core_memories",
                [],
            )
        ),
        "relevant_memories": (
            retrieved_durable_memory.get(
                "relevant_memories",
                [],
            )
        ),
    }

    memory_context_seconds = (
        time.perf_counter()
        - memory_context_started_at
    )

    routing_started_at = (
        time.perf_counter()
    )
    
    tool_governor = ToolGovernor(
        llm_engine=(
            st.session_state
            .engine
            .llm_engine
        ),
    )

    tool_decision = (
        tool_governor.decide(
            text=original_user_text,
            available_tools=available_tools,
            provider=active_tool_provider,
            conversation_context=(
                working_memory_context
            ),
            image_context={
                "image_active": bool(
                    active_chat_image
                ),
                "filename": (
                    active_chat_image.get(
                        "name",
                        "",
                    )
                ),
                "mime_type": (
                    active_chat_image.get(
                        "mime_type",
                        "",
                    )
                ),
                "visual_analysis": (
                    st.session_state.get(
                        "active_image_analysis",
                        {},
                    ).get(
                        "analysis",
                        "",
                    )
                ),
            },
        )
    )

    detected_language = str(
        tool_decision.get(
            "detected_language",
            "",
        )
        or ""
    ).strip().lower()

    # --------------------------------------------------
    # Reference Image Generation Route
    # --------------------------------------------------

    image_intent = str(
        tool_decision.get(
            "image_intent",
            "unrelated",
        )
        or "unrelated"
    ).strip().lower()

    if (
        image_intent
        == "reference_image_generation"
        and active_chat_image
        and image_bytes
    ):

        # ----------------------------------------------
        # Recover useful recent conversational context
        # ----------------------------------------------

        recent_reference_context = []

        for recent_turn in (
            working_memory_context.get(
                "recent_turns",
                [],
            )[-3:]
        ):

            if not isinstance(
                recent_turn,
                dict,
            ):
                continue

            recent_user = str(
                recent_turn.get(
                    "user_input",
                    "",
                )
                or ""
            ).strip()

            recent_answer = str(
                recent_turn.get(
                    "answer",
                    "",
                )
                or ""
            ).strip()

            if recent_user:
                recent_reference_context.append(
                    f"Previous user request: "
                    f"{recent_user}"
                )

            if recent_answer:
                recent_reference_context.append(
                    f"Previous DeDe response: "
                    f"{recent_answer}"
                )

        previous_context_text = "\n".join(
            recent_reference_context
        )

        visual_reference_analysis = (
            st.session_state.get(
                "active_image_analysis",
                {},
            ).get(
                "analysis",
                "",
            )
        )

        reference_prompt = (
            st.session_state.visual_prompt_compiler
            .compile_reference_generation(
                user_request=original_user_text,
                visual_analysis=(
                    visual_reference_analysis
                ),
                conversation_context=(
                    previous_context_text
                ),
            )
        )

        with st.chat_message("user"):
            st.write(
                original_user_text
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "DeDe is creating the image "
                "from the reference..."
            ):

                reference_result = (
                    st.session_state
                    .cloudflare_reference_image
                    .generate(
                        prompt=reference_prompt,
                        reference_image=image_bytes,
                    )
                )

            if (
                reference_result.get(
                    "status"
                )
                == "success"
            ):

                generated_image_bytes = (
                    reference_result.get(
                        "image_bytes",
                        b"",
                    )
                )

                generated_mime_type = (
                    reference_result.get(
                        "mime_type",
                        "image/png",
                    )
                )

                if generated_image_bytes:

                    st.image(
                        generated_image_bytes,
                        caption=(
                            "Generated by DeDe "
                            "from the reference image"
                        ),
                        width="stretch",
                    )

                    st.download_button(
                        label="Download image",
                        data=generated_image_bytes,
                        file_name=(
                            "dede_reference_image.png"
                        ),
                        mime=generated_mime_type,
                        key=(
                            "download_reference_image_"
                            f"{len(st.session_state.tool_history)}"
                        ),
                    )

                    st.session_state.tool_history.append(
                        {
                            "user_input": (
                                original_user_text
                            ),
                            "tool_name": (
                                "cloudflare_reference_image"
                            ),
                            "tool_result": {
                                "status": "success",
                                "data": {
                                    "image_bytes": (
                                        generated_image_bytes
                                    ),
                                    "mime_type": (
                                        generated_mime_type
                                    ),
                                    "provider": "cloudflare",
                                    "model": (
                                        reference_result.get(
                                            "model",
                                            "",
                                        )
                                    ),
                                },
                            },
                        }
                    )

                else:

                    st.error(
                        "Reference generation succeeded "
                        "but no image was returned."
                    )

            else:

                st.error(
                    reference_result.get(
                        "error",
                        (
                            "Reference image "
                            "generation failed."
                        ),
                    )
                )
                
            finish_response_timer(
                response_timer_state
            )
    
            st.stop()
    # --------------------------------------------------
    # Vision Routing Protection
    # --------------------------------------------------
    
    vision_request_active = bool(
        active_chat_image
        and st.session_state.get(
            "active_image_analysis"
        )
    )
    
    if vision_request_active:
    
        selected_vision_tool = str(
            tool_decision.get(
                "tool_name",
                "",
            )
            or ""
        ).lower()
    
        if selected_vision_tool in {
            "image_generator",
            "cloudflare_image_generator",
        }:
    
            tool_decision["action"] = (
                "respond_normally"
            )
    
            tool_decision["tool_name"] = ""
    
            tool_decision["arguments"] = {}
    
            tool_decision["reason"] = (
                "An uploaded user image is being "
                "analyzed. Image generation must "
                "not be triggered."
            )

    routing_seconds = (
        time.perf_counter()
        - routing_started_at
    )
    
    memory_candidate = tool_decision.get(
        "memory_candidate",
        {},
    )
    
    if not isinstance(
        memory_candidate,
        dict,
    ):
        memory_candidate = {}

    # --------------------------------------------------
    # Durable Memory Duplicate Protection
    # --------------------------------------------------

    candidate_content = str(
        memory_candidate.get(
            "content",
            "",
        )
        or ""
    ).strip().casefold()

    candidate_type = str(
        memory_candidate.get(
            "memory_type",
            "",
        )
        or ""
    ).strip().casefold()

    existing_memory_items = (
        persistent_memory_context.get(
            "memory_items",
            [],
        )
    )

    if not isinstance(
        existing_memory_items,
        list,
    ):
        existing_memory_items = []

    memory_already_exists = False

    if candidate_content:
        for existing_memory in existing_memory_items:

            if not isinstance(
                existing_memory,
                dict,
            ):
                continue

            existing_content = str(
                existing_memory.get(
                    "content",
                    "",
                )
                or ""
            ).strip().casefold()

            existing_type = str(
                existing_memory.get(
                    "memory_type",
                    "",
                )
                or ""
            ).strip().casefold()

            if (
                existing_content
                == candidate_content
                and existing_type
                == candidate_type
            ):
                memory_already_exists = True
                break

    if memory_already_exists:
        memory_candidate = {}

        tool_decision[
            "memory_candidate"
        ] = {}

    memory_storage_mode = st.session_state.get(
        "memory_storage_mode",
        "selective",
    )
    
    memory_governance = (
        st.session_state.engine
        .memory_governor
        .evaluate(
            text=text,
            storage_mode=memory_storage_mode,
            candidate=memory_candidate,
            user_approved=False,
        )
    )
    
    tool_decision[
        "memory_governance"
    ] = memory_governance

    if memory_governance.get(
        "requires_confirmation",
        False,
    ):
        st.session_state[
            "pending_memory_candidate"
        ] = {
            "text": text,
            "candidate": memory_governance.get(
                "candidate",
                {},
            ),
            "storage_mode": memory_storage_mode,
            "storage_scope": (
                memory_governance.get(
                    "candidate",
                    {},
                ).get(
                    "proposed_scope",
                    "persistent",
                )
            ),
        }

    memory_saved = False

    if memory_governance.get(
        "allow_persistent_storage",
        False,
    ):
        approved_candidate = memory_governance.get(
            "candidate",
            {},
        )
    
        storage_scope = memory_governance.get(
            "storage_scope",
            "persistent",
        )
    
        st.session_state.engine.persistent_memory.store_candidate(
            candidate=approved_candidate,
            storage_scope=storage_scope,
        )
    
        memory_saved = True
    
    tool_decision[
        "memory_saved"
    ] = memory_saved
    
    # --------------------------------------------------
    # Working Memory Fast Route
    # --------------------------------------------------

    if (
        tool_decision.get(
            "action"
        )
        in {
            "use_working_memory",
            "respond_directly",
        }
        and not tool_decision.get(
            "external_search_required",
            False,
        )
    ):
        direct_answer = str(
            tool_decision.get(
                "direct_answer",
                "",
            )
            or ""
        ).strip()

        if direct_answer:
            with st.chat_message(
                "user"
            ):
                st.write(
                    text
                )

            with st.chat_message(
                "assistant"
            ):
                st.write(
                    direct_answer
                )

            fast_user_response = {
                "final_answer": (
                    direct_answer
                ),
                "follow_up_question": None,
                "conversation_mode": (
                    "working_memory_fast_route"
                ),
            }

            st.session_state.conversation_history = (
                st.session_state.engine
                .conversation_manager
                .add_turn(
                    history=(
                        st.session_state
                        .conversation_history
                    ),
                    user_input=text,
                    user_response=(
                        fast_user_response
                    ),
                    report={},
                )
            )

            finish_response_timer(
                response_timer_state
            )

            if st.session_state.get(
                "pending_memory_candidate"
            ):
                st.rerun()

            st.stop()
            
            
    # --------------------------------------------------
    # Active Document Routing
    # --------------------------------------------------

    active_document = st.session_state.get(
        "active_document",
        {},
    )

    active_document_ready = bool(
        active_document.get(
            "text",
            "",
        )
    )

    selected_tool_name = str(
        tool_decision.get(
            "tool_name",
            "",
        )
        or ""
    ).strip().lower()

    document_tool_selected = (
        "pdf" in selected_tool_name
        or "document" in selected_tool_name
    )

    active_document_request = (
        active_document_ready
        and document_tool_selected
    )

    if active_document_request:
        tool_decision = {
            "governor": "tool_governor",
            "status": "ready",
            "action": "respond_normally",
            "tool_name": "",
            "confidence": 1.0,
            "arguments": {},
            "reason": (
                "The requested document is already active "
                "and its extracted text is available. "
                "Answer from the active document context."
            ),
        }

    if tool_decision.get("action") == "use_tool":
        selected_tool = tool_decision.get(
            "tool_name",
            "",
        )

        selected_arguments = tool_decision.get(
            "arguments",
            {},
        )
        
        image_tool_names = {
            "image_generator",
            "cloudflare_image_generator",
        }

        video_tool_names = {
            "huggingface_video_generator",
            "pollinations_video_generator",
        }

        if selected_tool in image_tool_names:
            selected_tool = st.session_state.get(
                "selected_image_tool",
                "cloudflare_image_generator",
            )

            if selected_tool not in image_tool_names:
                selected_tool = (
                    "cloudflare_image_generator"
                )

            routed_image_prompt = str(
                selected_arguments.get(
                    "prompt",
                    text,
                )
            ).strip()

            image_prompt = (
                st.session_state.visual_prompt_compiler
                .compile_generation(
                    user_request=original_user_text,
                    routed_prompt=routed_image_prompt,
                )
            )

            if selected_tool == "cloudflare_image_generator":
                selected_arguments = {
                    "prompt": image_prompt,
                    "steps": st.session_state.get(
                        "cloudflare_image_steps",
                        4,
                    ),
                }

            else:
                selected_arguments = {
                    "prompt": image_prompt,
                    "size": selected_arguments.get(
                        "size",
                        "1024x1024",
                    ),
                    "quality": selected_arguments.get(
                        "quality",
                        "medium",
                    ),
                    "transparent_background": (
                        selected_arguments.get(
                            "transparent_background",
                            False,
                        )
                    ),
                }

            tool_decision["tool_name"] = selected_tool
            tool_decision["arguments"] = selected_arguments

        with st.chat_message("user"):
            st.write(text)

        if selected_tool in video_tool_names:
            video_prompt = str(
                selected_arguments.get(
                    "prompt",
                    text,
                )
            ).strip()

            if "pollinations" in text.lower():
                selected_tool = (
                    "pollinations_video_generator"
                )

                selected_arguments = {
                    "prompt": video_prompt,
                    "model": "wan-fast",
                    "duration": 5,
                    "aspect_ratio": "9:16",
                    "audio": False,
                }

            else:
                selected_tool = (
                    "huggingface_video_generator"
                )

                selected_arguments = {
                    "prompt": video_prompt,
                }

            tool_decision[
                "tool_name"
            ] = selected_tool

            tool_decision[
                "arguments"
            ] = selected_arguments

        with st.chat_message("assistant"):
            with st.spinner(
                "DeDe is using the requested tool..."
            ):
                tool_result = (
                    st.session_state.tool_manager.run(
                        tool_name=selected_tool,
                        arguments=selected_arguments,
                    )
                )

            if tool_result.get("status") != "success":
                st.error(
                    tool_result.get(
                        "error",
                        "Tool execution failed.",
                    )
                )

            elif selected_tool in image_tool_names:
                image_data = tool_result.get(
                    "data",
                    {},
                )

                image_bytes = image_data.get(
                    "image_bytes"
                )

                mime_type = image_data.get(
                    "mime_type",
                    "image/png",
                )

                extension = (
                    "jpg"
                    if mime_type == "image/jpeg"
                    else "png"
                )

                if image_bytes:
                    st.image(
                        image_bytes,
                        caption=(
                            "Generated by DeDe with "
                            f"{image_data.get('provider', 'AI')}"
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
                        key=(
                            "download_current_tool_image_"
                            f"{len(st.session_state.tool_history)}"
                        ),
                    )

                else:
                    st.error(
                        "The provider returned no image data."
                    )

            elif selected_tool in video_tool_names:
                video_data = tool_result.get(
                    "data",
                    {},
                )

                video_bytes = video_data.get(
                    "video_bytes"
                )

                mime_type = video_data.get(
                    "mime_type",
                    "video/mp4",
                )

                if video_bytes:
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
                        key=(
                            "download_current_tool_video_"
                            f"{len(st.session_state.tool_history)}"
                        ),
                    )

                    st.caption(
                        "Generated by DeDe with "
                        f"{video_data.get('provider', 'AI')} | "
                        "Model: "
                        f"{video_data.get('model', 'unknown')}"
                    )

                else:
                    st.error(
                        "The provider returned no video data."
                    )

            else:
                st.write(
                    tool_result.get(
                        "summary",
                        "Tool executed successfully.",
                    )
                )

        tool_history_index = len(
            st.session_state.tool_history
        )

        st.session_state.tool_history.append(
            {
                "user_input": text,
                "tool_name": selected_tool,
                "tool_decision": tool_decision,
                "tool_result": tool_result,
            }
        )

        st.session_state.conversation_history = (
            st.session_state.engine
            .conversation_manager
            .add_tool_turn(
                history=(
                    st.session_state
                    .conversation_history
                ),
                user_input=text,
                tool_name=selected_tool,
                tool_arguments=(
                    selected_arguments
                ),
                tool_result=tool_result,
                tool_history_index=(
                    tool_history_index
                ),
            )
        )

        finish_response_timer(
            response_timer_state
        )

        st.rerun()

        st.stop()

    effective_search_mode = (
        search_mode.lower()
    )

    effective_explicit_search_request = (
        False
    )

    if active_document_request:
        effective_search_mode = "off"

    elif (
        effective_search_mode
        == "on_request"
    ):
        effective_explicit_search_request = bool(
            tool_decision.get(
                "external_search_required",
                False,
            )
        )

        print("=" * 80)
    print("SEARCH ROUTING DIAGNOSTIC")
    print("USER TEXT :", repr(text))
    print(
        "TOOL GOVERNOR ACTION :",
        repr(
            tool_decision.get(
                "action"
            )
        ),
    )
    print(
        "TOOL GOVERNOR EXTERNAL SEARCH :",
        repr(
            tool_decision.get(
                "external_search_required"
            )
        ),
    )
    print(
        "TOOL GOVERNOR REASON :",
        repr(
            tool_decision.get(
                "reason"
            )
        ),
    )
    print(
        "EFFECTIVE SEARCH MODE :",
        repr(
            effective_search_mode
        ),
    )
    print(
        "EXPLICIT SEARCH REQUEST :",
        repr(
            effective_explicit_search_request
        ),
    )
    print("=" * 80)

    engine = st.session_state.engine

    cognitive_pipeline_started_at = (
        time.perf_counter()
    )

    report = engine.analyze(
        text=text,
        detected_language=detected_language,
        document_context=st.session_state.get(
            "active_document",
            {},
        ),
        enable_llm=enable_llm,
        search_provider=search_provider,
        search_profile=(
            None if search_profile == "custom"
            else search_profile
        ),
        search_mode=(
            effective_search_mode
        ),
        explicit_search_request=(
            effective_explicit_search_request
        ),
        llm_profile="fast",
        llm_providers=llm_providers,
        knowledge_providers=knowledge_providers,
        knowledge_mode=knowledge_mode,
        conversation_history=st.session_state.conversation_history,
        memory_governance=memory_governance,
    )
    
    cognitive_pipeline_seconds = (
        time.perf_counter()
        - cognitive_pipeline_started_at
    )
    
    # --------------------------------------------------
    # Real World Anchor Analysis
    # --------------------------------------------------

    anchor_engine = RealWorldAnchor()

    source_analysis = report.get(
        "source_analysis",
        {},
    )

    search_validation = report.get(
        "search_validation",
        {},
    )

    cognitive_comparison = report.get(
        "cognitive_comparison",
        {},
    )

    anchor_result = anchor_engine.analyze(
        text=text,
        source_analysis=source_analysis,
        search_validation=search_validation,
        cognitive_comparison=cognitive_comparison,
    )

    report["real_world_anchor"] = anchor_result

    st.session_state.conversation_history = report.get(
        "conversation_history",
        st.session_state.conversation_history,
    )

    user_response = report.get("user_response", {})

    with st.chat_message("user"):
        st.write(text)

    with st.chat_message("assistant"):

        final_answer = user_response.get(
            "final_answer",
            "No answer generated.",
        )

        st.write(final_answer)

        render_message_save_control(
            message_text=final_answer,
            control_key=(
                "current_"
                f"{len(
                    st.session_state
                    .conversation_history
                )}"
            ),
        )

        if st.button(
            "🔊 Listen",
            key=f"tts_current_{len(st.session_state.conversation_history)}",
        ):
            audio = generate_speech(final_answer)
            st.audio(audio, format="audio/mp3")

    total_response_seconds = (
        finish_response_timer(
            response_timer_state
        )
    )

    measured_seconds = (
        memory_context_seconds
        + routing_seconds
        + cognitive_pipeline_seconds
    )

    other_seconds = max(
        0.0,
        total_response_seconds
        - measured_seconds,
    )

    with st.expander(
        "⏱️ Performance details",
        expanded=False,
    ):
        st.write(
            "Memory context:",
            f"{memory_context_seconds:.2f} s",
        )

        st.write(
            "Tool routing:",
            f"{routing_seconds:.2f} s",
        )

        st.write(
            "Cognitive pipeline:",
            f"{cognitive_pipeline_seconds:.2f} s",
        )

        st.write(
            "Other processing:",
            f"{other_seconds:.2f} s",
        )

        st.write(
            "Total:",
            f"{total_response_seconds:.2f} s",
        )

        internal_profile = report.get(
            "performance_profile",
            {},
        )

        if internal_profile:

            st.markdown(
                "#### 🔬 Cognitive pipeline details"
            )

            st.write(
                "Memory + identity + dialogue:",
                f"{internal_profile.get(
                    'memory_identity_dialogue',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "Knowledge + semantic:",
                f"{internal_profile.get(
                    'knowledge_semantic',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "Search + source analysis:",
                f"{internal_profile.get(
                    'search_source_analysis',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "Graph + agents + reasoning:",
                f"{internal_profile.get(
                    'graph_agents_reasoning',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "LLM prompt build:",
                f"{internal_profile.get(
                    'llm_prompt_build',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "LLM generation:",
                f"{internal_profile.get(
                    'llm_generation',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "Committee + formulas + dialogue:",
                f"{internal_profile.get(
                    'committee_formula_dialogue',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "Final processing:",
                f"{internal_profile.get(
                    'final_processing',
                    0.0,
                ):.2f} s",
            )

            st.write(
                "**Internal total:**",
                f"{internal_profile.get(
                    'total_internal',
                    0.0,
                ):.2f} s",
            )

    workspace = report["workspace"]
    variables = workspace["variables"]
    agent_results = report["agent_results"]
    summary = report["summary"]
    committee = report["committee"]

    formulas = report["formulas"]
    core = formulas["core"]
    derived = formulas["derived"]

    # --------------------------------------------------
    # DeDe Cognitive Dashboard
    # --------------------------------------------------

    with st.expander("DeDe Cognitive Dashboard"):

        # --------------------------------------------------
        # Real World Anchor
        # --------------------------------------------------

        st.subheader("Ancrage au réel")

        st.write(anchor_result["label"])

        st.progress(anchor_result["score"])

        st.info(anchor_result["interpretation"])

        st.caption("Confiance épistémique")

        st.progress(
            anchor_result["epistemic_confidence"]
        )

        st.caption("Risque d'hallucination / suraffirmation")

        st.progress(
            anchor_result["hallucination_risk"]
        )

        st.write(
            "Action Governor :",
            anchor_result["governor_action"],
        )

        with st.expander("Détails de l'ancrage"):
            st.json(anchor_result["components"])

        # --------------------------------------------------
        # Active Document
        # --------------------------------------------------

        st.subheader("Active Document")

        active_document_report = report.get(
            "document_context",
            {},
        )

        if (
            active_document_report.get(
                "status"
            )
            == "ready"
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Filename",
                    active_document_report.get(
                        "filename",
                        "N/A",
                    ),
                )

            with col2:
                st.metric(
                    "Pages",
                    active_document_report.get(
                        "page_count",
                        0,
                    ),
                )

            with col3:
                st.metric(
                    "Words",
                    active_document_report.get(
                        "word_count",
                        0,
                    ),
                )

            with st.expander(
                "Document metadata"
            ):
                st.json(
                    active_document_report.get(
                        "metadata",
                        {},
                    )
                )

        else:
            st.caption(
                "No active document."
            )

        # --------------------------------------------------
        # Search Engine
        # --------------------------------------------------
        
        search_result = report.get(
            "search_result",
            {},
        )
        
        st.subheader("Search Engine")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Provider",
                search_result.get(
                    "provider",
                    "none",
                ),
            )
        
        with col2:
            st.metric(
                "Status",
                search_result.get(
                    "status",
                    "disabled",
                ),
            )
        
        st.caption(
            search_result.get(
                "summary",
                "",
            )
        )
        
        with st.expander("Search Details"):
            st.json(search_result)

        # --------------------------------------------------
        # Universal Text Analysis
        # --------------------------------------------------

        st.subheader("Universal Text Analysis")

        user_text_analysis = report.get(
            "user_text_analysis",
            {},
        )

        web_text_analysis = report.get(
            "web_text_analysis",
            {},
        )

        final_response_analysis = report.get(
            "final_response_analysis",
            {},
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "User Analysis",
                user_text_analysis.get(
                    "status",
                    "N/A",
                ),
            )

        with col2:
            st.metric(
                "Web Items Analyzed",
                web_text_analysis.get(
                    "item_count",
                    0,
                ),
            )

        with col3:
            st.metric(
                "Final Response Analysis",
                final_response_analysis.get(
                    "status",
                    "N/A",
                ),
            )

        with st.expander("User Text Analysis"):
            st.json(user_text_analysis)

        with st.expander("Web Text Analysis"):
            st.json(web_text_analysis)

        with st.expander("Final Response Analysis"):
            st.json(final_response_analysis)

        # --------------------------------------------------
        # Cognitive Comparison
        # --------------------------------------------------

        st.subheader("Cognitive Comparison")

        cognitive_comparison = report.get(
            "cognitive_comparison",
            {},
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Comparison Status",
                cognitive_comparison.get(
                    "status",
                    "N/A",
                ),
            )

        with col2:
            st.metric(
                "Warnings",
                cognitive_comparison.get(
                    "warning_count",
                    0,
                ),
            )

        st.write(
            cognitive_comparison.get(
                "summary",
                "",
            )
        )

        warnings = cognitive_comparison.get(
            "warnings",
            [],
        )

        for warning in warnings:
            message = warning.get(
                "message",
                "",
            )

            severity = warning.get(
                "severity",
                "medium",
            )

            if severity == "high":
                st.error(message)
            else:
                st.warning(message)

        with st.expander(
            "Cognitive Comparison Details"
        ):
            st.json(cognitive_comparison)

        # --------------------------------------------------
        # Cognitive Source Analysis
        # --------------------------------------------------

        st.subheader("Cognitive Source Analysis")

        source_analysis = report.get(
            "source_analysis",
            {},
        )

        source_aggregate = source_analysis.get(
            "aggregate",
            {},
        )

        average_scores = source_aggregate.get(
            "average_scores",
            {},
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Sources",
                source_analysis.get(
                    "source_count",
                    0,
                ),
            )

        with col2:
            evidence_score = average_scores.get(
                "evidence_level"
            )

            st.metric(
                "Average Evidence",
                (
                    f"{evidence_score:.0%}"
                    if isinstance(
                        evidence_score,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with col3:
            relevance_score = average_scores.get(
                "relevance"
            )

            st.metric(
                "Average Relevance",
                (
                    f"{relevance_score:.0%}"
                    if isinstance(
                        relevance_score,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        st.write(
            source_analysis.get(
                "overall_summary",
                "",
            )
        )

        st.write("Source Types")

        st.json(
            source_aggregate.get(
                "source_type_counts",
                {},
            )
        )

        with st.expander(
            "Cognitive Source Analysis Details"
        ):
            st.json(source_analysis)

        # --------------------------------------------------
        # Autobiographical Memory
        # --------------------------------------------------

        st.subheader("Autobiographical Memory")
        st.json(report.get("autobiography", {}))

        st.subheader("Autobiographical Reasoning")
        st.json(report.get("autobiographical_reasoning", {}))
        
        # --------------------------------------------------
        # Phase 2 Cognitive Variables
        # --------------------------------------------------
        
        st.subheader("Phase 2 Cognitive Variables")
    
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            show_metric("Grounding", variables["grounding"])
    
        with col2:
            show_metric("Integration", variables["integration"])
    
        with col3:
            show_metric("Closure", variables["closure"])
    
        with col4:
            show_metric("Reduction", variables["reduction"])
    
            
        # --------------------------------------------------
        # Phase 2 Cognitive Summary
        # --------------------------------------------------
        
        st.subheader("Phase 2 Cognitive Summary")
    
        st.write(summary["diagnosis"])
    
        st.metric(
            "Cognitive Balance",
            pct(summary["cognitive_balance"]),
        )
    
        committee = report["committee"]
    
        formulas = report["formulas"]
        core = formulas["core"]
        derived = formulas["derived"]
        
        # --------------------------------------------------
        # DOXA Formula Metrics
        # --------------------------------------------------
        
        st.subheader("DOXA Formula Metrics")
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            show_metric(
                "Support",
                core["support"],
            )
        
            show_metric(
                "Pressure",
                core["pressure"],
            )
        
        with col2:
            show_metric(
                "Cognitive Pressure",
                core["cognitive_pressure"],
            )
        
            show_metric(
                "Closure Risk",
                core["closure_risk"],
            )
        
        with col3:
            show_metric(
                "Revisability",
                core["revisability"],
            )
        
            show_metric(
                "Surconfidence",
                derived["surconfidence"],
            )
            
        # --------------------------------------------------
        # Derived Cognitive Pressures
        # --------------------------------------------------
        
        st.subheader("Derived Cognitive Pressures")
    
        col1, col2 = st.columns(2)
    
        with col1:
            show_metric("Cognitive Closure", derived["cognitive_closure"])
    
        with col2:
            show_metric(
                "Forgotten Reduction",
                derived["forgotten_reduction_pressure"],
            )
    
        st.info(formulas["diagnosis"])
        
        # --------------------------------------------------
        # Semantic Graph
        # --------------------------------------------------
    
        semantic_graph = report.get("semantic_graph", {})

        # --------------------------------------------------
        # Universal Text Analysis
        # --------------------------------------------------
        
        st.subheader("Universal Text Analysis")
        
        st.write("USER")
        st.json(report.get("user_text_analysis", {}))
        
        st.write("WEB")
        st.json(report.get("web_text_analysis", {}))
        
        st.write("FINAL RESPONSE")
        st.json(report.get("final_response_analysis", {}))
        
        st.subheader("Semantic Graph")
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.metric("Nodes", semantic_graph.get("node_count", 0))
    
        with col2:
            st.metric("Edges", semantic_graph.get("edge_count", 0))
    
        with col3:
            st.metric(
                "Causal Paths",
                semantic_graph.get("causal_path_count", 0),
            )
    
        if semantic_graph.get("causal_paths"):
            st.caption("Detected cognitive paths")
    
            for path in semantic_graph["causal_paths"]:
                readable_path = " → ".join(
                    f'{step["source"]} / {step["relation"]} / {step["target"]}'
                    for step in path["path"]
                )
                st.write(f"- {readable_path}")
    
        with st.expander("Semantic Graph details"):
            st.json(semantic_graph)
        
        # --------------------------------------------------
        # Graph Queries
        # --------------------------------------------------
    
        graph_queries = report.get("graph_queries", {})
        
        st.subheader("Graph Queries")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Central Nodes",
                len(graph_queries.get("central_nodes", [])),
            )
    
        with col2:
            key_paths = graph_queries.get("key_paths", {})
            available_paths = sum(
                1 for path in key_paths.values() if path
            )
            st.metric(
                "Available Key Paths",
                available_paths,
            )
    
        if graph_queries.get("central_nodes"):
            st.caption("Most connected cognitive nodes")
    
            for item in graph_queries["central_nodes"]:
                st.write(
                    f'- {item["node"]} — degree {item["degree"]}'
                )
        
        with st.expander("LLM Context Preview"):
            st.json(
                graph_queries.get(
                    "llm_context",
                    {},
                )
            )
        
        with st.expander("Graph Query details"):
            st.json(graph_queries)
        
        # --------------------------------------------------
        # Inference Pattern 
        # --------------------------------------------------
    
        inference_patterns = report.get("inference_patterns", {})
        
        st.subheader("Inference Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Available Patterns",
                inference_patterns.get("available_pattern_count", 0),
            )
        
        with col2:
            st.metric(
                "Detected Patterns",
                inference_patterns.get("detected_pattern_count", 0),
            )
        
        st.write(
            inference_patterns.get(
                "summary",
                "",
            )
        )
        
        patterns = inference_patterns.get("patterns", [])
        
        if patterns:
            for pattern in patterns:
                confidence = pattern.get("confidence", 0)
        
                st.write(
                    f'- **{pattern.get("name", "unknown")}** '
                    f'[{pattern.get("type", "pattern")}] '
                    f'— confidence {round(confidence * 100)}%'
                )
        
                st.caption(
                    pattern.get(
                        "description",
                        "",
                    )
                )
        
        with st.expander("Inference Pattern details"):
            st.json(inference_patterns)
    
        # --------------------------------------------------
        # Cognitive State Compiler
        # --------------------------------------------------
    
        cognitive_state = report.get("cognitive_state", {})
        
        st.subheader("Cognitive State Compiler")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Compiled Orientation",
                cognitive_state.get("orientation", "N/A"),
            )
    
        with col2:
            show_metric(
                "Compiled Confidence",
                cognitive_state.get("confidence"),
            )
    
        st.write(
            cognitive_state.get(
                "summary",
                "",
            )
        )
    
        with st.expander("Cognitive Focus"):
            st.json(
                cognitive_state.get(
                    "cognitive_focus",
                    [],
                )
            )
    
        with st.expander("Support"):
            st.json(
                cognitive_state.get(
                    "support",
                    [],
                )
            )
    
        with st.expander("Pressure"):
            st.json(
                cognitive_state.get(
                    "pressure",
                    [],
                )
            )
    
        with st.expander("Protective Mechanisms"):
            st.json(
                cognitive_state.get(
                    "protective_mechanisms",
                    [],
                )
            )
    
        with st.expander("Detected Dynamics"):
            st.json(
                cognitive_state.get(
                    "detected_dynamics",
                    [],
                )
            )
    
        with st.expander("Missing Dimensions"):
            st.json(
                cognitive_state.get(
                    "missing_dimensions",
                    [],
                )
            )
    
        with st.expander("Full Cognitive State"):
            st.json(cognitive_state)
    
        # --------------------------------------------------
        # Cognitive Reasoner
        # --------------------------------------------------
    
        cognitive_reasoning = report.get("cognitive_reasoning", {})
    
        st.subheader("Cognitive Reasoner")
    
        st.metric(
            "Reasoner Status",
            cognitive_reasoning.get("status", "N/A"),
        )
    
        nodes = cognitive_reasoning.get("nodes_considered", [])
    
        if nodes:
            st.caption("Nodes considered")
            st.write(", ".join(nodes))
    
        with st.expander("Hypotheses"):
            st.json(cognitive_reasoning.get("hypotheses", []))
    
        with st.expander("Contradictions"):
            st.json(cognitive_reasoning.get("contradictions", []))
    
        with st.expander("Explanations"):
            st.json(cognitive_reasoning.get("explanations", []))
    
        with st.expander("Missing Links"):
            st.json(cognitive_reasoning.get("missing_links", []))
    
        with st.expander("Predictions"):
            st.json(cognitive_reasoning.get("predictions", []))
    
        with st.expander("Counterfactuals"):
            st.json(cognitive_reasoning.get("counterfactuals", []))
    
        with st.expander("Inference Chains"):
            st.json(cognitive_reasoning.get("inference_chains", []))

        # --------------------------------------------------
        # Committee Reasoner
        # --------------------------------------------------

        committee_reasoning = report.get(
            "committee_reasoning",
            {},
        )

        st.subheader("Committee Reasoner")

        st.caption(
            "Transforms multiple LLM outputs into structured reasoning material "
            "before DeDe builds its final answer."
        )

        st.metric(
            "Reasoner Status",
            committee_reasoning.get("status", "N/A"),
        )

        st.write(
            committee_reasoning.get("summary", "")
        )

        with st.expander("Committee Reasoning Details"):
            st.json(committee_reasoning)
        
        # --------------------------------------------------
        # LLM Connector
        # --------------------------------------------------
    
        llm_package = report.get("llm_package", {})
        
        st.subheader("LLM Connector")
    
        st.metric(
            "LLM Package Status",
            llm_package.get("status", "N/A"),
        )
    
        st.write(llm_package.get("summary", ""))
    
        with st.expander("LLM System Prompt"):
            st.write(llm_package.get("system_prompt", ""))
    
        with st.expander("LLM Cognitive Context"):
            st.text(llm_package.get("cognitive_context", ""))
    
        with st.expander("Full LLM Prompt Package"):
            st.json(llm_package)
    
        # --------------------------------------------------
        # LLM Bridge
        # --------------------------------------------------
    
        llm_bridge_response = report.get("llm_bridge_response", {})
    
        st.subheader("LLM Bridge")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Bridge Status",
                llm_bridge_response.get("status", "N/A"),
            )
    
        with col2:
            st.metric(
                "Provider",
                llm_bridge_response.get("provider", "N/A"),
            )
    
            st.metric(
                "JSON Valid",
                str(llm_bridge_response.get("json_valid", False)),
            )
    
        st.write(
            llm_bridge_response.get(
                "summary",
                "",
            )
        )
    
        if llm_bridge_response.get("error"):
            st.error(
                llm_bridge_response["error"]
            )
    
        if llm_bridge_response.get("response"):
            with st.expander("LLM Raw Response"):
                st.write(
                    llm_bridge_response["response"]
                )
    
        with st.expander("Full LLM Bridge Response"):
            st.json(llm_bridge_response)

        # --------------------------------------------------
        # LLM Engine
        # --------------------------------------------------
        
        llm_engine_response = report.get(
            "llm_engine_response",
            {},
        )
        
        st.subheader("Reasoning Models")
        
        st.caption(
            "Reasoning models are interchangeable LLM components used by DeDe "
            "after memory, search, semantic and cognitive preparation."
        )
        
        llm_committee = llm_engine_response.get(
            "committee",
            {},
        )
        
        if llm_committee:
        
            st.metric(
                "Committee Providers",
                llm_committee.get(
                    "provider_count",
                    0,
                ),
            )
        
            st.caption(
                llm_committee.get(
                    "summary",
                    "",
                )
            )
        
        st.metric(
            "Engine Status",
            llm_engine_response.get("status", "N/A"),
        )
        
        st.write(
            llm_engine_response.get("summary", "")
        )
        
        with st.expander("Reasoning Model Details"):
            st.json(llm_engine_response)
    
        # --------------------------------------------------
        # Cognitive Feedback
        # --------------------------------------------------
    
        cognitive_feedback = report.get("cognitive_feedback", {})
    
        st.subheader("Cognitive Feedback")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Feedback Status",
                cognitive_feedback.get("status", "N/A"),
            )
    
        with col2:
            show_metric(
                "Feedback Confidence",
                cognitive_feedback.get("confidence"),
            )
    
        st.write(
            cognitive_feedback.get(
                "summary",
                "",
            )
        )
    
        with st.expander("New Concepts"):
            st.json(
                cognitive_feedback.get(
                    "new_concepts",
                    [],
                )
            )
    
        with st.expander("New Relations"):
            st.json(
                cognitive_feedback.get(
                    "new_relations",
                    [],
                )
            )
    
        with st.expander("New Hypotheses"):
            st.json(
                cognitive_feedback.get(
                    "new_hypotheses",
                    [],
                )
            )
    
        with st.expander("New Questions"):
            st.json(
                cognitive_feedback.get(
                    "new_questions",
                    [],
                )
            )
    
        with st.expander("New Missing Dimensions"):
            st.json(
                cognitive_feedback.get(
                    "new_missing_dimensions",
                    [],
                )
            )
    
        with st.expander("New Counterfactuals"):
            st.json(
                cognitive_feedback.get(
                    "new_counterfactuals",
                    [],
                )
            )
    
        with st.expander("Full Cognitive Feedback"):
            st.json(cognitive_feedback)
    
        # --------------------------------------------------
        # Dialogue Decision
        # --------------------------------------------------
        
        dialogue_decision = report.get("dialogue_decision", {})
    
        st.subheader("Dialogue Strategy")
        
        st.metric(
            "Dialogue Mode",
            dialogue_decision.get("mode", "N/A"),
        )
        
        st.write(
            dialogue_decision.get("summary", "")
        )
        
        with st.expander("Dialogue Decision"):
            st.json(dialogue_decision)
    
        # --------------------------------------------------
        # Conversation Reasoning
        # --------------------------------------------------
    
        conversation_reasoning = report.get("conversation_reasoning", {})
    
        st.subheader("Conversation Reasoning")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.metric(
                "Next Move",
                conversation_reasoning.get("move", "N/A"),
            )
    
        with col2:
            st.metric(
                "Follow-up",
                str(conversation_reasoning.get("is_follow_up", False)),
            )
    
        st.write(
            conversation_reasoning.get("summary", "")
        )
    
        if conversation_reasoning.get("next_prompt"):
            st.info(
                conversation_reasoning["next_prompt"]
            )
    
        with st.expander("Conversation Reasoning details"):
            st.json(conversation_reasoning)

        # --------------------------------------------------
        # Dialogue Profile
        # --------------------------------------------------

        dialogue_profile = report.get("dialogue_profile", {})

        st.subheader("Dialogue Profile")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Language",
                dialogue_profile.get("language", "N/A"),
            )

        with col2:
            st.metric(
                "Tone",
                dialogue_profile.get("tone", "N/A"),
            )

        with col3:
            st.metric(
                "Verbosity",
                dialogue_profile.get("verbosity", "N/A"),
            )

        st.write(
            dialogue_profile.get("summary", "")
        )

        with st.expander("Dialogue Profile details"):
            st.json(dialogue_profile)
    
        # --------------------------------------------------
        # Agent Interpretations
        # --------------------------------------------------
        # --------------------------------------------------
        # Mécroyance Therapy Spectrum
        # --------------------------------------------------
        
        cognitive_therapy = agent_results.get(
            "cognitive_therapy",
            {},
        )
        
        mecroyance = cognitive_therapy.get(
            "mecroyance",
            {},
        )
        
        if mecroyance:
        
            st.subheader("🧠 Mécroyance Therapy")
        
            g_value = float(
                mecroyance.get("G", 0.0)
            )
        
            n_value = float(
                mecroyance.get("N", 0.0)
            )
        
            d_value = float(
                mecroyance.get("D", 0.0)
            )
        
            m_value = float(
                mecroyance.get("M", 0.0)
            )
        
            bar_position = float(
                mecroyance.get(
                    "bar_position",
                    0.0,
                )
            )
        
            zone_label = mecroyance.get(
                "zone_label",
                "Unknown",
            )
        
            interpretation = mecroyance.get(
                "interpretation",
                "",
            )
        
            # ----------------------------------------------
            # G / N / D / M
            # ----------------------------------------------
        
            col1, col2, col3, col4 = st.columns(4)
        
            with col1:
                st.metric(
                    "G — Gnosis",
                    f"{g_value:.1f}",
                )
        
            with col2:
                st.metric(
                    "N — Nous",
                    f"{n_value:.1f}",
                )
        
            with col3:
                st.metric(
                    "D — Doxa",
                    f"{d_value:.1f}",
                )
        
            with col4:
                st.metric(
                    "M — Mécroyance",
                    f"{m_value:.1f}",
                )
        
            # ----------------------------------------------
            # Mécroyance bar
            # ----------------------------------------------
        
            st.markdown(
                "#### Barre de mécroyance"
            )
        
            st.progress(
                max(
                    0.0,
                    min(
                        1.0,
                        bar_position,
                    ),
                )
            )
        
            # ----------------------------------------------
            # Spectrum reference
            # ----------------------------------------------
        
            st.caption(
                "-10  ·  0  ·  10  ·  17  ·  19  ·  20"
            )
        
            st.markdown(
                f"**Zone actuelle : {zone_label}**"
            )
        
            if interpretation:
                st.info(
                    interpretation
                )
        
            with st.expander(
                "Mécroyance details"
            ):
                st.json(
                    mecroyance
                )
        st.subheader("Agent Interpretations")
    
        for name, result in agent_results.items():
            st.markdown(f"### {name}")
    
            st.info(result.get("summary", ""))
    
            if result.get("committee_reply"):
                st.write(result["committee_reply"])
    
            with st.expander(f"{name} details"):
                st.json(result)
    
        # --------------------------------------------------
        # Cognitive Committee
        # --------------------------------------------------
        
        st.subheader("Cognitive Committee")
    
        col1, col2 = st.columns(2)
    
        with col1:
            show_metric(
                "Committee Confidence",
                committee["confidence"],
            )
    
        with col2:
            st.metric(
                "Dominant Orientation",
                committee["dominant_orientation"],
            )
    
        st.info(committee["diagnosis"])
    
        # --------------------------------------------------
        # Committee Concerns
        # --------------------------------------------------
    
        if committee["concerns"]:
            st.subheader("Committee Concerns")
    
            for concern in committee["concerns"]:
                st.warning(concern)
    
        # --------------------------------------------------
        # Committee Recommendations
        # --------------------------------------------------
        
        st.subheader("Committee Recommendations")
    
        for recommendation in committee["recommendations"]:
            st.write(f"- {recommendation}")
                
        # --------------------------------------------------
        # Full Report
        # --------------------------------------------------
        
        st.subheader("Complete Cognitive Report")
        
        st.json(report)

    if st.session_state.get(
        "pending_memory_candidate"
    ):
        st.rerun()
