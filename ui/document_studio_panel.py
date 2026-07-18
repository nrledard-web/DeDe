"""
DeDe - Document Studio Panel

Streamlit sidebar interface for document tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


def render_document_studio_panel(
    tool_manager: Any,
) -> None:
    """
    Render document tools inside the sidebar.
    """

    with st.sidebar:
        with st.expander(
            "📄 Document Studio",
            expanded=False,
        ):
            document_tool_labels = {
                "PDF Reader — Active": "pdf_reader",
                "PDF Generator — Planned": "planned",
                "Word Generator — Planned": "planned",
                "PowerPoint Generator — Planned": "planned",
                "Spreadsheet Generator — Planned": "planned",
            }

            selected_document_label = st.selectbox(
                "Document Tool",
                list(document_tool_labels.keys()),
                key="document_studio_tool",
            )

            selected_document_tool = (
                document_tool_labels[
                    selected_document_label
                ]
            )

            if selected_document_tool == "pdf_reader":
                _render_pdf_reader(
                    tool_manager=tool_manager,
                )

            else:
                st.info(
                    "This document tool is visible in "
                    "the modular architecture but is "
                    "not implemented yet."
                )

            _render_active_document_status()


def _render_pdf_reader(
    tool_manager: Any,
) -> None:
    """
    Render PDF upload and text extraction controls.
    """

    st.caption(
        "Upload a PDF to extract and inspect its text."
    )

    uploaded_pdf = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        key="pdf_studio_uploader",
    )

    max_pages = st.number_input(
        "Maximum pages to read",
        min_value=1,
        max_value=500,
        value=100,
        step=1,
        key="pdf_studio_max_pages",
    )

    if st.button(
        "Read PDF",
        key="read_pdf_button",
        type="primary",
        use_container_width=True,
    ):
        if uploaded_pdf is None:
            st.warning(
                "Choose a PDF document first."
            )

        else:
            file_bytes = uploaded_pdf.getvalue()

            with st.spinner(
                "DeDe is reading the PDF..."
            ):
                pdf_result = tool_manager.run(
                    tool_name="pdf_reader",
                    arguments={
                        "file_bytes": file_bytes,
                        "filename": uploaded_pdf.name,
                        "max_pages": int(max_pages),
                    },
                )

            st.session_state[
                "last_pdf_result"
            ] = pdf_result

            st.session_state[
                "active_pdf_bytes"
            ] = file_bytes

    _render_pdf_result()


def _render_pdf_result() -> None:
    """
    Display the last PDF extraction result.
    """

    pdf_tool_result = st.session_state.get(
        "last_pdf_result",
        {},
    )

    if not pdf_tool_result:
        return

    pdf_status = pdf_tool_result.get(
        "status",
        "unknown",
    )

    pdf_data = pdf_tool_result.get(
        "data",
        {},
    )

    if pdf_status == "success":
        _store_active_document(
            pdf_tool_result=pdf_tool_result,
            pdf_data=pdf_data,
        )

        st.success(
            pdf_tool_result.get(
                "summary",
                "PDF read successfully.",
            )
        )

        st.metric(
            "Pages",
            pdf_data.get(
                "page_count",
                0,
            ),
        )

        st.metric(
            "Pages read",
            pdf_data.get(
                "pages_read",
                0,
            ),
        )

        st.metric(
            "Words",
            pdf_data.get(
                "word_count",
                0,
            ),
        )

        metadata = pdf_data.get(
            "metadata",
            {},
        )

        with st.expander(
            "PDF metadata",
            expanded=False,
        ):
            st.json(
                metadata
            )

        extracted_text = str(
            pdf_data.get(
                "text",
                "",
            )
        )

        st.text_area(
            "Extracted text preview",
            value=extracted_text[:20000],
            height=250,
            disabled=True,
            key="pdf_text_preview",
        )

        if len(extracted_text) > 20000:
            st.caption(
                "The preview is limited to "
                "20,000 characters."
            )

        _render_downloads(
            pdf_data=pdf_data,
            extracted_text=extracted_text,
            metadata=metadata,
        )

    elif pdf_status == "no_text":
        st.warning(
            pdf_tool_result.get(
                "summary",
                (
                    "No text was found. "
                    "The document may require OCR."
                ),
            )
        )

    else:
        st.error(
            pdf_tool_result.get(
                "error",
                "PDF reading failed.",
            )
        )


def _store_active_document(
    pdf_tool_result: dict[str, Any],
    pdf_data: dict[str, Any],
) -> None:
    """
    Make the extracted PDF available to DeDe chat.
    """

    st.session_state.active_document = {
        "status": "ready",
        "source_type": "pdf",
        "filename": pdf_data.get(
            "filename",
            "document.pdf",
        ),
        "text": pdf_data.get(
            "text",
            "",
        ),
        "pages": pdf_data.get(
            "pages",
            [],
        ),
        "page_count": pdf_data.get(
            "page_count",
            0,
        ),
        "pages_read": pdf_data.get(
            "pages_read",
            0,
        ),
        "metadata": pdf_data.get(
            "metadata",
            {},
        ),
        "word_count": pdf_data.get(
            "word_count",
            0,
        ),
        "character_count": pdf_data.get(
            "character_count",
            0,
        ),
        "summary": pdf_tool_result.get(
            "summary",
            "",
        ),
    }


def _render_downloads(
    pdf_data: dict[str, Any],
    extracted_text: str,
    metadata: dict[str, Any],
) -> None:
    """
    Render active and planned download options.
    """

    st.markdown("#### Downloads")

    filename = pdf_data.get(
        "filename",
        "document.pdf",
    )

    file_stem = Path(
        filename
    ).stem

    original_pdf = st.session_state.get(
        "active_pdf_bytes"
    )

    if original_pdf:
        st.download_button(
            label="Download original PDF",
            data=original_pdf,
            file_name=filename,
            mime="application/pdf",
            key="download_original_pdf",
            use_container_width=True,
        )

    st.download_button(
        label="Download extracted text",
        data=extracted_text.encode(
            "utf-8"
        ),
        file_name=f"{file_stem}.txt",
        mime="text/plain",
        key="download_pdf_text",
        use_container_width=True,
    )

    structured_result = {
        "filename": filename,
        "page_count": pdf_data.get(
            "page_count",
            0,
        ),
        "pages_read": pdf_data.get(
            "pages_read",
            0,
        ),
        "word_count": pdf_data.get(
            "word_count",
            0,
        ),
        "character_count": pdf_data.get(
            "character_count",
            0,
        ),
        "metadata": metadata,
        "text": extracted_text,
    }

    st.download_button(
        label="Download structured JSON",
        data=json.dumps(
            structured_result,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8"),
        file_name=f"{file_stem}.json",
        mime="application/json",
        key="download_pdf_json",
        use_container_width=True,
    )

    st.button(
        "Download DOCX — Planned",
        disabled=True,
        key="download_pdf_docx_planned",
        use_container_width=True,
    )

    st.button(
        "Download PDF report — Planned",
        disabled=True,
        key="download_pdf_report_planned",
        use_container_width=True,
    )


def _render_active_document_status() -> None:
    """
    Display and manage the active document.
    """

    active_document = st.session_state.get(
        "active_document",
        {},
    )

    if active_document.get("status") != "ready":
        return

    st.success(
        "Active document: "
        + active_document.get(
            "filename",
            "document.pdf",
        )
    )

    st.caption(
        f'{active_document.get("page_count", 0)} page(s) '
        f'| {active_document.get("word_count", 0)} words'
    )

    if st.button(
        "Remove active PDF",
        key="remove_active_pdf",
        use_container_width=True,
    ):
        st.session_state.pop(
            "active_document",
            None,
        )

        st.session_state.pop(
            "last_pdf_result",
            None,
        )

        st.session_state.pop(
            "active_pdf_bytes",
            None,
        )

        st.rerun()
