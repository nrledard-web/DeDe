"""
DeDe - Semantic Language Resolver

Resolves the language of short or statistically ambiguous
user messages through a dedicated semantic LLM decision.

The resolver receives only the current user message.

It does not use:
- conversation history
- memory
- topic vocabulary lists
- language-specific lexical markers
- DeDe foundational concepts
"""

from __future__ import annotations

import json
import re
from typing import Any


class SemanticLanguageResolver:

    name = "semantic_language_resolver"

    def __init__(
        self,
        llm_engine: Any | None = None,
    ) -> None:
        self.llm_engine = llm_engine

    def set_llm_engine(
        self,
        llm_engine: Any,
    ) -> None:
        self.llm_engine = llm_engine

    def resolve(
        self,
        text: str,
    ) -> dict[str, Any]:

        cleaned_text = str(
            text or ""
        ).strip()

        if not cleaned_text:
            return self._empty_result(
                reason="empty_text",
            )

        if self.llm_engine is None:
            return self._empty_result(
                reason="llm_engine_unavailable",
            )

        prompt = (
            "Determine the natural language used in the "
            "CURRENT USER MESSAGE below.\n\n"
            "Analyze only the linguistic structure and meaning "
            "of that message.\n\n"
            "Do not use conversation history, assumed user "
            "preferences, subject matter, proper names, product "
            "names or topic vocabulary as evidence.\n\n"
            "Return the ISO 639-1 language code when one exists. "
            "If the language cannot be determined reliably, "
            "return \"unknown\".\n\n"
            "Return only valid JSON with exactly this structure:\n"
            "{\n"
            '  "language": "",\n'
            '  "confidence": 0.0\n'
            "}\n\n"
            "CURRENT USER MESSAGE:\n"
            + cleaned_text
        )

        try:
            response = self.llm_engine.ask(
                prompt=prompt,
                profile="fast",
                enabled=True,
            )

        except Exception as error:
            return self._empty_result(
                reason=str(error),
            )

        raw_response = ""

        if isinstance(
            response,
            dict,
        ):
            raw_response = str(
                response.get(
                    "response",
                    response.get(
                        "raw_response",
                        "",
                    ),
                )
                or ""
            ).strip()

        else:
            raw_response = str(
                response or ""
            ).strip()

        parsed = self._parse_json(
            raw_response
        )

        if not parsed:
            return self._empty_result(
                reason="invalid_semantic_response",
                raw_response=raw_response,
            )

        language = self._normalize_code(
            parsed.get(
                "language"
            )
        )

        try:
            confidence = float(
                parsed.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            )

        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        if (
            not language
            or language == "unknown"
        ):
            return self._empty_result(
                reason="semantic_language_unknown",
                raw_response=raw_response,
            )

        return {
            "resolver": self.name,
            "status": "ready",
            "language": language,
            "confidence": confidence,
            "source": "semantic_current_message_only",
            "raw_response": raw_response,
        }

    def _parse_json(
        self,
        text: str,
    ) -> dict[str, Any] | None:

        cleaned = str(
            text or ""
        ).strip()

        cleaned = (
            cleaned
            .replace(
                "```json",
                "",
            )
            .replace(
                "```JSON",
                "",
            )
            .replace(
                "```",
                "",
            )
            .strip()
        )

        try:
            parsed = json.loads(
                cleaned
            )

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except Exception:
            pass

        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL,
        )

        if not match:
            return None

        try:
            parsed = json.loads(
                match.group(0)
            )

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except Exception:
            return None

        return None

    @staticmethod
    def _normalize_code(
        language: Any,
    ) -> str:

        code = str(
            language or ""
        ).strip().lower()

        if not code:
            return ""

        if "-" in code:
            code = code.split(
                "-",
                1,
            )[0]

        if "_" in code:
            code = code.split(
                "_",
                1,
            )[0]

        return code

    def _empty_result(
        self,
        reason: str,
        raw_response: str = "",
    ) -> dict[str, Any]:

        return {
            "resolver": self.name,
            "status": "unresolved",
            "language": "unknown",
            "confidence": 0.0,
            "source": "semantic_current_message_only",
            "reason": reason,
            "raw_response": raw_response,
        }
