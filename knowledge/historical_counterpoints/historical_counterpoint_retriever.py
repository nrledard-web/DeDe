"""
DeDe - Historical Counterpoint Retriever

Retrieves underreported but materially important historical
counterpoints relevant to the current user message.

Historical counterpoints are specialized knowledge.
They are not part of DeDe's universal foundational knowledge.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from knowledge.historical_counterpoints.islamic_thought import (
    ISLAMIC_THOUGHT_COUNTERPOINT,
)


class HistoricalCounterpointRetriever:
    """
    Retrieve only historical counterpoints relevant
    to the current subject.
    """

    name = "historical_counterpoint_retriever"

    def __init__(self) -> None:
        self.counterpoints = {
            "islamic_thought": ISLAMIC_THOUGHT_COUNTERPOINT,
        }

    def retrieve(
        self,
        text: str,
        concept_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve relevant historical counterpoints.

        The retrieval is local and fast.
        No additional LLM call is required.
        """

        concept_data = concept_data or {}

        normalized_text = self._normalize(text)

        main_concepts = concept_data.get(
            "main_concepts",
            [],
        )

        normalized_concepts = {
            self._normalize(str(concept))
            for concept in main_concepts
            if concept
        }

        selected_counterpoints = []

        for counterpoint_id, counterpoint in (
            self.counterpoints.items()
        ):
            score = self._score_counterpoint(
                counterpoint=counterpoint,
                normalized_text=normalized_text,
                normalized_concepts=normalized_concepts,
            )

            if score <= 0:
                continue

            selected_counterpoints.append(
                {
                    "id": counterpoint_id,
                    "score": round(score, 3),
                    "knowledge": counterpoint,
                }
            )

        selected_counterpoints.sort(
            key=lambda item: item["score"],
            reverse=True,
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
                f"Retrieved {len(selected_counterpoints)} "
                "relevant historical counterpoint(s)."
                if selected_counterpoints
                else (
                    "No historical counterpoint was relevant "
                    "to the current message."
                )
            ),
        }

    def _score_counterpoint(
        self,
        counterpoint: dict[str, Any],
        normalized_text: str,
        normalized_concepts: set[str],
    ) -> float:
        """
        Score relevance from the user text and semantic concepts.
        """

        score = 0.0

        retrieval_concepts = counterpoint.get(
            "retrieval_concepts",
            [],
        )

        for concept in retrieval_concepts:
            normalized_term = self._normalize(
                str(concept)
            )

            if not normalized_term:
                continue

            if self._contains_term(
                normalized_text,
                normalized_term,
            ):
                word_count = len(
                    normalized_term.split()
                )

                score += (
                    2.5
                    if word_count > 1
                    else 1.5
                )

            if normalized_term in normalized_concepts:
                score += 1.5

        return score

    def _build_prompt_context(
        self,
        selected_counterpoints: list[dict[str, Any]],
    ) -> str:
        """
        Convert selected counterpoints into a compact
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
                item.get("id", "Counterpoint"),
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
        Render dictionaries, lists and strings as
        readable prompt context.
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

                if isinstance(item, (dict, list)):
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
                if isinstance(item, (dict, list)):
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

    def _contains_term(
        self,
        text: str,
        term: str,
    ) -> bool:
        if not text or not term:
            return False

        pattern = (
            r"(?<!\w)"
            + re.escape(term)
            + r"(?!\w)"
        )

        return bool(
            re.search(
                pattern,
                text,
            )
        )

    def _normalize(
        self,
        value: str,
    ) -> str:
        """
        Normalize accents, punctuation and letter case
        without altering semantic content.
        """

        normalized = unicodedata.normalize(
            "NFKD",
            str(value or ""),
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(
                character
            )
        )

        normalized = normalized.lower()

        normalized = re.sub(
            r"[^\w\s'-]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()
