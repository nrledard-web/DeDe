"""
DeDe - Deterministic Code Syntax Validator.

Validates supported source formats without
executing the submitted code.
"""

from __future__ import annotations

import ast
import json

from pathlib import PurePosixPath
from typing import Any


class CodeSyntaxValidator:
    """
    Validate supported code and data formats.
    """

    PYTHON_EXTENSIONS = {
        ".py",
        ".pyw",
    }

    JSON_EXTENSIONS = {
        ".json",
    }

    def _detect_format(
        self,
        language: str,
        filename: str,
    ) -> str:
        """
        Detect the validation format.
        """

        normalized_language = str(
            language or ""
        ).strip().lower()

        extension = (
            PurePosixPath(
                str(filename or "")
            )
            .suffix
            .lower()
        )

        if (
            normalized_language == "python"
            or extension
            in self.PYTHON_EXTENSIONS
        ):
            return "python"

        if (
            normalized_language
            in {
                "json",
                "json / yaml",
            }
            and extension != ".yaml"
            and extension != ".yml"
        ):
            return "json"

        if extension in self.JSON_EXTENSIONS:
            return "json"

        return "unsupported"

    def validate(
        self,
        source_code: str,
        language: str = "Automatic",
        filename: str = "",
    ) -> dict[str, Any]:
        """
        Validate source syntax without execution.
        """

        source_code = str(
            source_code or ""
        )

        if not source_code.strip():
            return {
                "status": "empty",
                "valid": False,
                "error": (
                    "The source code is empty."
                ),
            }

        detected_format = (
            self._detect_format(
                language=language,
                filename=filename,
            )
        )

        if detected_format == "python":
            try:
                ast.parse(
                    source_code,
                    filename=(
                        filename
                        or "<dede-code>"
                    ),
                )

            except SyntaxError as error:
                return {
                    "status": "syntax_error",
                    "valid": False,
                    "format": "python",
                    "line": error.lineno,
                    "column": error.offset,
                    "error": str(error),
                }

            return {
                "status": "success",
                "valid": True,
                "format": "python",
                "summary": (
                    "Python syntax is valid."
                ),
            }

        if detected_format == "json":
            try:
                json.loads(
                    source_code
                )

            except json.JSONDecodeError as error:
                return {
                    "status": "syntax_error",
                    "valid": False,
                    "format": "json",
                    "line": error.lineno,
                    "column": error.colno,
                    "error": str(error),
                }

            return {
                "status": "success",
                "valid": True,
                "format": "json",
                "summary": (
                    "JSON syntax is valid."
                ),
            }

        return {
            "status": "unsupported",
            "valid": None,
            "format": detected_format,
            "summary": (
                "Automatic syntax validation "
                "is not available for this format."
            ),
        }
