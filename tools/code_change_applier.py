"""
DeDe - Deterministic Code Change Applier.

Applies explicit, validated text replacements
without executing the source code.
"""

from __future__ import annotations

import json
import difflib

from typing import Any


class CodeChangeApplier:
    """
    Apply validated changes to source code.
    """

    MAX_CHANGES = 25

    def _extract_payload(
        self,
        raw_response: str,
    ) -> dict[str, Any]:
        """
        Extract one JSON object from a response.
        """

        cleaned_response = str(
            raw_response or ""
        ).strip()

        json_start = (
            cleaned_response.find("{")
        )

        json_end = (
            cleaned_response.rfind("}")
        )

        if (
            json_start < 0
            or json_end <= json_start
        ):
            raise ValueError(
                "DeDe returned no valid "
                "change description."
            )

        json_text = cleaned_response[
            json_start:json_end + 1
        ]

        payload = json.loads(
            json_text
        )

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "The change description "
                "must be a JSON object."
            )

        return payload

    def apply(
        self,
        source_code: str,
        raw_response: str,
    ) -> dict[str, Any]:
        """
        Apply every exact replacement atomically.
        """

        original_source = str(
            source_code or ""
        )

        if not original_source:
            return {
                "status": "invalid_source",
                "error": (
                    "No source code was provided."
                ),
            }

        try:
            payload = self._extract_payload(
                raw_response
            )

        except (
            ValueError,
            json.JSONDecodeError,
        ) as error:
            return {
                "status": "invalid_changes",
                "error": str(error),
            }

        changes = payload.get(
            "changes",
            [],
        )

        if not isinstance(
            changes,
            list,
        ):
            return {
                "status": "invalid_changes",
                "error": (
                    "The changes field "
                    "must be a list."
                ),
            }

        if not changes:
            return {
                "status": "no_changes",
                "error": (
                    "DeDe proposed no change."
                ),
            }

        if len(changes) > self.MAX_CHANGES:
            return {
                "status": "too_many_changes",
                "error": (
                    "DeDe proposed too many "
                    "changes at once."
                ),
            }

        updated_source = original_source
        applied_changes = []

        for index, change in enumerate(
            changes,
            start=1,
        ):
            if not isinstance(
                change,
                dict,
            ):
                return {
                    "status": "invalid_change",
                    "error": (
                        f"Change {index} "
                        "is not an object."
                    ),
                }

            old_text = str(
                change.get(
                    "old_text",
                    "",
                )
            )

            new_text = str(
                change.get(
                    "new_text",
                    "",
                )
            )

            if not old_text:
                return {
                    "status": "invalid_change",
                    "error": (
                        f"Change {index} has "
                        "no original text."
                    ),
                }

            occurrence_count = (
                updated_source.count(
                    old_text
                )
            )

            if occurrence_count != 1:
                return {
                    "status": (
                        "ambiguous_change"
                    ),
                    "error": (
                        f"Change {index} expected "
                        "one exact occurrence but "
                        f"found {occurrence_count}."
                    ),
                }

            updated_source = (
                updated_source.replace(
                    old_text,
                    new_text,
                    1,
                )
            )

            applied_changes.append(
                {
                    "index": index,
                    "description": str(
                        change.get(
                            "description",
                            "",
                        )
                    ).strip(),
                }
            )

        diff_lines = (
            difflib.unified_diff(
                original_source.splitlines(),
                updated_source.splitlines(),
                fromfile="original",
                tofile="proposed",
                lineterm="",
            )
        )

        diff_text = "\n".join(
            diff_lines
        )

        return {
            "status": "success",
            "source_code": updated_source,
            "summary": str(
                payload.get(
                    "summary",
                    "",
                )
            ).strip(),
            "applied_changes": (
                applied_changes
            ),
            "change_count": len(
                applied_changes
            ),
        }
