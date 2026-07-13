"""
DeDe - PDF Reader

Extracts text and metadata from text-based PDF documents.

This first version does not perform OCR.
Scanned image-only PDFs require a later OCR tool.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from pypdf import PdfReader


class PDFReader:
    """
    Read a PDF from bytes and return normalized page content.
    """

    name = "pdf_reader"

    description = (
        "Read a PDF document, extract its text page by page, "
        "and return document metadata."
    )

    input_schema = {
        "file_bytes": {
            "type": "bytes",
            "required": True,
        },
        "filename": {
            "type": "string",
            "required": False,
            "default": "document.pdf",
        },
        "max_pages": {
            "type": "integer",
            "required": False,
            "default": 100,
        },
    }

    def run(
        self,
        file_bytes: bytes,
        filename: str = "document.pdf",
        max_pages: int = 100,
    ) -> dict[str, Any]:
        """
        Standard ToolManager entry point.
        """

        return self.read(
            file_bytes=file_bytes,
            filename=filename,
            max_pages=max_pages,
        )

    def read(
        self,
        file_bytes: bytes,
        filename: str = "document.pdf",
        max_pages: int = 100,
    ) -> dict[str, Any]:
        """
        Extract PDF text and metadata.
        """

        if not file_bytes:
            return {
                "tool": self.name,
                "status": "invalid_request",
                "error": "The PDF file is empty.",
                "summary": "No PDF data was supplied.",
            }

        safe_filename = str(
            filename or "document.pdf"
        ).strip()

        try:
            page_limit = int(max_pages)
        except (
            TypeError,
            ValueError,
        ):
            page_limit = 100

        page_limit = max(
            1,
            min(
                page_limit,
                500,
            ),
        )

        try:
            pdf_stream = BytesIO(
                file_bytes
            )

            reader = PdfReader(
                pdf_stream
            )

            if reader.is_encrypted:
                try:
                    decrypt_result = reader.decrypt(
                        ""
                    )

                    if decrypt_result == 0:
                        return {
                            "tool": self.name,
                            "status": "encrypted",
                            "error": (
                                "The PDF is encrypted and "
                                "requires a password."
                            ),
                            "summary": (
                                "Encrypted PDF could not be read."
                            ),
                        }

                except Exception:
                    return {
                        "tool": self.name,
                        "status": "encrypted",
                        "error": (
                            "The PDF is encrypted and "
                            "could not be opened."
                        ),
                        "summary": (
                            "Encrypted PDF could not be read."
                        ),
                    }

            total_pages = len(
                reader.pages
            )

            pages_to_read = min(
                total_pages,
                page_limit,
            )

            extracted_pages: list[
                dict[str, Any]
            ] = []

            complete_text_parts: list[str] = []

            empty_page_count = 0

            for page_index in range(
                pages_to_read
            ):
                page = reader.pages[
                    page_index
                ]

                page_text = str(
                    page.extract_text() or ""
                ).strip()

                if not page_text:
                    empty_page_count += 1

                extracted_pages.append(
                    {
                        "page_number": (
                            page_index + 1
                        ),
                        "text": page_text,
                        "character_count": len(
                            page_text
                        ),
                        "word_count": len(
                            page_text.split()
                        ),
                        "has_text": bool(
                            page_text
                        ),
                    }
                )

                if page_text:
                    complete_text_parts.append(
                        (
                            f"--- PAGE "
                            f"{page_index + 1} ---\n"
                            f"{page_text}"
                        )
                    )

            complete_text = "\n\n".join(
                complete_text_parts
            ).strip()

            metadata = self._extract_metadata(
                reader
            )

            status = (
                "success"
                if complete_text
                else "no_text"
            )

            if total_pages > page_limit:
                summary = (
                    f"PDF text extracted from the first "
                    f"{pages_to_read} of {total_pages} pages."
                )

            elif complete_text:
                summary = (
                    f"PDF text extracted from "
                    f"{pages_to_read} page(s)."
                )

            else:
                summary = (
                    "No extractable text was found. "
                    "The PDF may contain scanned images."
                )

            return {
                "tool": self.name,
                "status": status,
                "provider": "pypdf",
                "filename": safe_filename,
                "page_count": total_pages,
                "pages_read": pages_to_read,
                "truncated": (
                    total_pages > page_limit
                ),
                "empty_page_count": (
                    empty_page_count
                ),
                "metadata": metadata,
                "pages": extracted_pages,
                "text": complete_text,
                "character_count": len(
                    complete_text
                ),
                "word_count": len(
                    complete_text.split()
                ),
                "requires_ocr": (
                    not complete_text
                    or empty_page_count
                    == pages_to_read
                ),
                "error": None,
                "summary": summary,
            }

        except Exception as error:
            return {
                "tool": self.name,
                "status": "error",
                "error": str(error),
                "filename": safe_filename,
                "summary": (
                    "PDF extraction failed."
                ),
            }

    def _extract_metadata(
        self,
        reader: PdfReader,
    ) -> dict[str, Any]:
        """
        Convert PDF metadata into JSON-safe values.
        """

        raw_metadata = (
            reader.metadata or {}
        )

        return {
            "title": self._metadata_value(
                raw_metadata.get(
                    "/Title"
                )
            ),
            "author": self._metadata_value(
                raw_metadata.get(
                    "/Author"
                )
            ),
            "subject": self._metadata_value(
                raw_metadata.get(
                    "/Subject"
                )
            ),
            "creator": self._metadata_value(
                raw_metadata.get(
                    "/Creator"
                )
            ),
            "producer": self._metadata_value(
                raw_metadata.get(
                    "/Producer"
                )
            ),
            "creation_date": (
                self._metadata_value(
                    raw_metadata.get(
                        "/CreationDate"
                    )
                )
            ),
            "modification_date": (
                self._metadata_value(
                    raw_metadata.get(
                        "/ModDate"
                    )
                )
            ),
        }

    def _metadata_value(
        self,
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        cleaned = str(
            value
        ).strip()

        return cleaned or None
