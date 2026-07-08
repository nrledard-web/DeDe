"""
DeDe - LLM Response Interpreter

Normalizes external LLM responses before DeDe uses them.

Goal:
LLM raw response
    ↓
parsed JSON when possible
    ↓
user-facing answer separated from cognitive material
    ↓
debug remains available
"""

import json
import re
from typing import Any


class LLMResponseInterpreter:

    name = "llm_response_interpreter"

    def interpret(
        self,
        llm_package: dict[str, Any],
        llm_response: str | dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        raw_response = self._extract_raw_response(llm_response)

        if not raw_response:
            return self._empty_response(llm_package)

        parsed_json = self._parse_json(raw_response)

        if parsed_json:
            user_facing_response = self._safe_text(
                parsed_json.get("user_facing_response")
            )

            if not user_facing_response:
                user_facing_response = self._fallback_text(raw_response)

            return {
                "interpreter": self.name,
                "status": "parsed_json",
                "json_valid": True,
                "user_facing_response": user_facing_response,
                "summary": self._safe_text(
                    parsed_json.get("summary")
                ),
                "confidence": self._safe_float(
                    parsed_json.get("confidence"),
                    default=0.0,
                ),
                "language": self._safe_text(
                    parsed_json.get("language")
                ),
                "parsed_json": parsed_json,
                "raw_response": raw_response,
                "source_prompt_status": llm_package.get(
                    "status",
                    "unknown",
                ),
            }

        return {
            "interpreter": self.name,
            "status": "text_fallback",
            "json_valid": False,
            "user_facing_response": self._fallback_text(raw_response),
            "summary": "LLM response was not valid JSON. Text fallback used.",
            "confidence": 0.3,
            "language": "unknown",
            "parsed_json": None,
            "raw_response": raw_response,
            "source_prompt_status": llm_package.get(
                "status",
                "unknown",
            ),
        }

    def _extract_raw_response(
        self,
        llm_response: str | dict[str, Any] | None,
    ) -> str:

        if llm_response is None:
            return ""

        if isinstance(llm_response, str):
            return llm_response.strip()

        if isinstance(llm_response, dict):
            for key in [
                "response",
                "raw_response",
                "content",
                "text",
                "final_answer",
            ]:
                value = llm_response.get(key)

                if isinstance(value, str) and value.strip():
                    return value.strip()

            return json.dumps(
                llm_response,
                ensure_ascii=False,
            )

        return str(llm_response).strip()

    def _parse_json(
        self,
        text: str,
    ) -> dict[str, Any] | None:

        cleaned = text.strip()

        cleaned = self._remove_code_fence(cleaned)

        try:
            data = json.loads(cleaned)

            if isinstance(data, dict):
                return data

        except Exception:
            pass

        extracted = self._extract_json_object(cleaned)

        if not extracted:
            return None

        try:
            data = json.loads(extracted)

            if isinstance(data, dict):
                return data

        except Exception:
            return None

        return None

    def _remove_code_fence(
        self,
        text: str,
    ) -> str:

        return (
            text
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

    def _extract_json_object(
        self,
        text: str,
    ) -> str | None:

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return None

        return text[start:end + 1].strip()

    def _fallback_text(
        self,
        text: str,
    ) -> str:

        parsed = self._parse_json(text)

        if parsed and parsed.get("user_facing_response"):
            return self._safe_text(
                parsed.get("user_facing_response")
            )

        return text.strip()

    def _empty_response(
        self,
        llm_package: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "interpreter": self.name,
            "status": "no_response",
            "json_valid": False,
            "user_facing_response": "",
            "summary": "No external LLM response received.",
            "confidence": 0.0,
            "language": "unknown",
            "parsed_json": None,
            "raw_response": "",
            "source_prompt_status": llm_package.get(
                "status",
                "unknown",
            ),
        }

    def _safe_text(
        self,
        value: Any,
    ) -> str:

        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        return str(value).strip()

    def _safe_float(
        self,
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:
            return float(value)
        except Exception:
            return default
