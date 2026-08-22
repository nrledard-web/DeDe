"""
DeDe - Coding Studio interface.

Provides the Coding Studio launcher,
workspace and session state.
"""

from __future__ import annotations
from typing import Any

import streamlit as st


CODING_TASKS = [
    "Generate code",
    "Modify code",
    "Debug an error",
    "Explain code",
    "Review code",
    "Refactor code",
    "Create tests",
    "Convert code",
]

PROGRAMMING_LANGUAGES = [
    "Automatic",
    "Python",
    "JavaScript",
    "TypeScript",
    "HTML / CSS",
    "SQL",
    "Bash",
    "JSON / YAML",
    "Other",
]


def ensure_coding_studio_state() -> None:
    """
    Initialize Coding Studio state.
    """

    defaults = {
        "coding_studio_open": False,
        "coding_studio_task": (
            CODING_TASKS[0]
        ),
        "coding_studio_language": (
            PROGRAMMING_LANGUAGES[0]
        ),
        "coding_studio_filename": "",
        "coding_studio_instruction": "",
        "coding_studio_error": "",
        "coding_studio_source_code": "",
        "coding_studio_result": "",
        "coding_github_owner": (
            "nrledard-web"
        ),
        "coding_github_repository": (
            "DeDe"
        ),
        "coding_github_branch": "main",
        "coding_github_files": [],
        "coding_github_selected_file": "",
        "coding_github_status": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    github_defaults = {
        "coding_github_owner": (
            "nrledard-web"
        ),
        "coding_github_repository": (
            "DeDe"
        ),
        "coding_github_branch": "main",
    }

    for key, value in (
        github_defaults.items()
    ):
        current_value = str(
            st.session_state.get(
                key,
                "",
            )
            or ""
        ).strip()

        if not current_value:
            st.session_state[key] = value


def render_coding_studio_launcher() -> None:
    """
    Render the Coding Studio button.
    """

    ensure_coding_studio_state()

    if st.button(
        "💻 Coding Studio",
        key="open_coding_studio",
        use_container_width=True,
    ):
        st.session_state[
            "coding_studio_open"
        ] = True


def render_coding_studio_workspace(
    save_control: Any = None,
) -> (
    dict[str, str] | None
):
    """
    Render the Coding Studio workspace.
    """

    ensure_coding_studio_state()

    pending_source_code = (
        st.session_state.pop(
            "coding_studio_pending_source",
            None,
        )
    )

    if pending_source_code is not None:
        st.session_state[
            "coding_studio_source_code"
        ] = str(
            pending_source_code
        )

    if not st.session_state.get(
        "coding_studio_open",
        False,
    ):
        return None

    st.markdown("---")

    title_column, close_column = (
        st.columns([0.85, 0.15])
    )

    with title_column:
        st.markdown(
            "## 💻 Coding Studio"
        )

        st.caption(
            "Generate, inspect, debug and "
            "improve code with DeDe."
        )

    with close_column:
        if st.button(
            "✕",
            key="close_coding_studio",
            help="Close Coding Studio",
            use_container_width=True,
        ):
            st.session_state[
                "coding_studio_open"
            ] = False

            st.rerun()

    with st.expander(
        "🐙 GitHub — Read Only",
        expanded=False,
    ):
        st.caption(
            "DeDe may read repository files. "
            "Writing, deletion and publishing "
            "are not available."
        )

        repository_column, branch_column = (
            st.columns([0.7, 0.3])
        )

        with repository_column:
            st.text_input(
                "Repository owner",
                key="coding_github_owner",
            )

            st.text_input(
                "Repository name",
                key=(
                    "coding_github_repository"
                ),
            )

        with branch_column:
            st.text_input(
                "Branch",
                key="coding_github_branch",
            )

        if st.button(
            "🔗 Connect Repository",
            key=(
                "coding_github_"
                "connect_repository"
            ),
            use_container_width=True,
        ):
            return {
                "action": (
                    "connect_github_repository"
                ),
                "owner": str(
                    st.session_state.get(
                        "coding_github_owner",
                        "",
                    )
                ).strip(),
                "repository": str(
                    st.session_state.get(
                        "coding_github_repository",
                        "",
                    )
                ).strip(),
                "branch": str(
                    st.session_state.get(
                        "coding_github_branch",
                        "main",
                    )
                ).strip(),
            }

        github_status = str(
            st.session_state.get(
                "coding_github_status",
                "",
            )
            or ""
        ).strip()

        if github_status:
            st.caption(
                github_status
            )

        github_files = (
            st.session_state.get(
                "coding_github_files",
                [],
            )
        )

        if github_files:
            selected_github_file = (
                st.selectbox(
                    "Repository file",
                    github_files,
                    key=(
                        "coding_github_"
                        "selected_file"
                    ),
                )
            )

            if st.button(
                "📖 Load Selected File",
                key=(
                    "coding_github_"
                    "load_selected_file"
                ),
                use_container_width=True,
            ):
                return {
                    "action": (
                        "load_github_file"
                    ),
                    "owner": str(
                        st.session_state.get(
                            "coding_github_owner",
                            "",
                        )
                    ).strip(),
                    "repository": str(
                        st.session_state.get(
                            "coding_github_repository",
                            "",
                        )
                    ).strip(),
                    "branch": str(
                        st.session_state.get(
                            "coding_github_branch",
                            "main",
                        )
                    ).strip(),
                    "file_path": str(
                        selected_github_file
                    ).strip(),
                }

    task_column, language_column = (
        st.columns(2)
    )

    with task_column:
        st.selectbox(
            "Coding task",
            CODING_TASKS,
            key="coding_studio_task",
        )

    with language_column:
        st.selectbox(
            "Programming language",
            PROGRAMMING_LANGUAGES,
            key="coding_studio_language",
        )

    st.text_input(
        "File name",
        key="coding_studio_filename",
        placeholder=(
            "Example: app.py"
        ),
    )

    st.text_area(
        "Instruction for DeDe",
        key="coding_studio_instruction",
        placeholder=(
            "Describe what you want DeDe "
            "to create, fix or explain..."
        ),
        height=120,
    )

    st.text_area(
        "Error or traceback",
        key="coding_studio_error",
        placeholder=(
            "Optional: paste the error "
            "message or traceback..."
        ),
        height=140,
    )

    st.text_area(
        "Source code",
        key="coding_studio_source_code",
        placeholder=(
            "Paste existing code here, "
            "or leave empty for new code..."
        ),
        height=260,
    )

    source_code = str(
        st.session_state.get(
            "coding_studio_source_code",
            "",
        )
        or ""
    )

    source_lines = (
        len(source_code.splitlines())
        if source_code
        else 0
    )

    source_characters = len(
        source_code
    )

    st.caption(
        f"{source_lines} source lines | "
        f"{source_characters} characters"
    )

    run_task = st.button(
        "✨ Run Coding Task",
        key="coding_studio_run_task",
        type="primary",
        use_container_width=True,
    )

    if run_task:
        instruction = str(
            st.session_state.get(
                "coding_studio_instruction",
                "",
            )
            or ""
        ).strip()

        error_text = str(
            st.session_state.get(
                "coding_studio_error",
                "",
            )
            or ""
        ).strip()

        if (
            not instruction
            and not source_code.strip()
            and not error_text
        ):
            st.warning(
                "Add an instruction, source code "
                "or an error before running the task."
            )

        else:
            return {
                "action": "run_coding_task",
                "task": str(
                    st.session_state.get(
                        "coding_studio_task",
                        "Generate code",
                    )
                ),
                "language": str(
                    st.session_state.get(
                        "coding_studio_language",
                        "Automatic",
                    )
                ),
                "filename": str(
                    st.session_state.get(
                        "coding_studio_filename",
                        "",
                    )
                    or ""
                ).strip(),
                "instruction": instruction,
                "error": error_text,
                "source_code": (
                    source_code.strip()
                ),
            }

    result = str(
        st.session_state.get(
            "coding_studio_result",
            "",
        )
        or ""
    )

    if result:
        st.text_area(
            "DeDe result",
            key="coding_studio_result",
            height=320,
        )

        result_lines = len(
            result.splitlines()
        )

        result_characters = len(
            result
        )

        st.caption(
            f"{result_lines} result lines | "
            f"{result_characters} characters"
        )
        
        result_filename = str(
            st.session_state.get(
                "coding_studio_filename",
                "",
            )
            or ""
        ).strip()

        if not result_filename:
            result_filename = (
                "dede_generated_code.txt"
            )

        if callable(save_control):
            save_control(
                message_text=result,
                control_key=(
                    "coding_studio_result"
                ),
                default_title=(
                    result_filename
                ),
            )

        control_column, download_column = (
            st.columns(2)
        )

        with control_column:
            if st.button(
                "↩️ Use as Source",
                key=(
                    "coding_studio_"
                    "use_result_as_source"
                ),
                use_container_width=True,
            ):
                st.session_state[
                    "coding_studio_pending_source"
                ] = result

                st.rerun()

        with download_column:
            st.download_button(
                "⬇️ Download and save File",
                data=result,
                file_name=result_filename,
                mime="text/plain",
                key=(
                    "coding_studio_"
                    "download_result"
                ),
                use_container_width=True,
            )

    return None
