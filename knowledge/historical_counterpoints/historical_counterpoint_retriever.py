"""
DeDe - Historical Counterpoint Retriever

Loads underreported but materially important historical
counterpoints selected by DeDe's semantic classification.

Historical counterpoints are specialized knowledge.
They are not part of DeDe's universal foundational knowledge.
"""

from __future__ import annotations

from typing import Any

from knowledge.historical_counterpoints.islamic_thought import (
    ISLAMIC_THOUGHT_COUNTERPOINT,
)


class HistoricalCounterpointRetriever:
    """
    Load historical counterpoints selected by the
    multilingual semantic classification layer.

    This Retriever does not detect languages and does not
    search for language-specific keywords.
    """

    name = "historical_counterpoint_retriever"

    def __init__(self) -> None:
        self.counterpoints = {
            "islamic_thought": ISLAMIC_THOUGHT_COUNTERPOINT,
        }

    def retrieve(
        self,
        selected_counterpoint_ids: list[str] | None = None,
        canonical_concepts: list[str] | None = None,
        text: str = "",
    ) -> dict[str, Any]:
        """
        Load only counterpoints selected by the Cognitive Governor.

        Parameters
        ----------
        selected_counterpoint_ids:
            Canonical identifiers returned by the multilingual
            semantic classification layer.

        canonical_concepts:
            English concept labels generated from the meaning
            of the user message.

        text:
            Original user message, preserved for provenance only.
            It is not searched for lexical markers here.
        """

        selected_counterpoint_ids = (
            selected_counterpoint_ids
            or []
        )

        canonical_concepts = (
            canonical_concepts
            or []
        )

        selected_counterpoints = []

        for counterpoint_id in selected_counterpoint_ids:
            normalized_id = str(
                counterpoint_id
            ).strip()

            counterpoint = self.counterpoints.get(
                normalized_id
            )

            if not counterpoint:
                continue

            selected_counterpoints.append(
                {
                    "id": normalized_id,
                    "knowledge": counterpoint,
                }
            )

        prompt_context = self._build_prompt_context(
            selected_counterpoints
        )

        return {
            "retriever": self.name,
            "status": (
                "ready"
                if selected_counterpoints
                else "not_relevant"
            ),
            "query": text,
            "canonical_concepts": canonical_concepts,
            "requested_counterpoint_ids": (
                selected_counterpoint_ids
            ),
            "counterpoint_count": len(
                selected_counterpoints
            ),
            "matched_counterpoints": [
                item["id"]
                for item in selected_counterpoints
            ],
            "counterpoints": selected_counterpoints,
            "prompt_context": prompt_context,
            "summary": (
                f"Loaded {len(selected_counterpoints)} "
                "semantically selected historical counterpoint(s)."
                if selected_counterpoints
                else (
                    "No historical counterpoint was selected "
                    "for the current message."
                )
            ),
        }

    def _build_prompt_context(
        self,
        selected_counterpoints: list[dict[str, Any]],
    ) -> str:
        """
        Convert selected counterpoints into compact
        context for the reasoning model.
        """

        if not selected_counterpoints:
            return ""

        lines = [
            "DEDE RELEVANT HISTORICAL COUNTERPOINTS",
            "",
            (
                "These counterpoints contain underreported but materially "
                "important historical or intellectual information."
            ),
            (
                "Use them only when they clarify the user's actual question. "
                "Do not force every available detail into the answer."
            ),
            (
                "Preserve distinctions, provenance, uncertainty and "
                "cognitive revisability."
            ),
            "",
        ]

        for item in selected_counterpoints:
            knowledge = item.get(
                "knowledge",
                {},
            )

            label = knowledge.get(
                "label",
                item.get(
                    "id",
                    "Counterpoint",
                ),
            )

            lines.append(f"{label}:")
            lines.append("")

            self._append_value(
                lines=lines,
                value=knowledge,
                indent="",
                ignored_keys={
                    "id",
                    "label",
                    "retrieval_concepts",
                },
            )

            lines.append("")

        return "\n".join(lines)

    def _append_value(
        self,
        lines: list[str],
        value: Any,
        indent: str,
        ignored_keys: set[str] | None = None,
    ) -> None:
        """
        Render dictionaries, lists and strings
        as readable prompt context.
        """

        ignored_keys = ignored_keys or set()

        if isinstance(value, str):
            lines.append(
                f"{indent}- {value}"
            )
            return

        if isinstance(value, dict):
            for key, item in value.items():
                if key in ignored_keys:
                    continue

                readable_key = str(key).replace(
                    "_",
                    " ",
                )

                if isinstance(
                    item,
                    (dict, list),
                ):
                    lines.append(
                        f"{indent}- {readable_key}:"
                    )

                    self._append_value(
                        lines=lines,
                        value=item,
                        indent=indent + "  ",
                        ignored_keys=ignored_keys,
                    )

                else:
                    lines.append(
                        f"{indent}- {readable_key}: {item}"
                    )

            return

        if isinstance(value, list):
            for item in value:
                if isinstance(
                    item,
                    (dict, list),
                ):
                    self._append_value(
                        lines=lines,
                        value=item,
                        indent=indent,
                        ignored_keys=ignored_keys,
                    )

                else:
                    lines.append(
                        f"{indent}- {item}"
                    )

            return

        lines.append(
            f"{indent}- {value}"
        )
