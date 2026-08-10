"""
DeDe - Cloudflare Routing Provider

Uses a small multilingual model only for fast semantic routing.

It does not replace DeDe's main reasoning models.
"""

from __future__ import annotations

from typing import Any
import json
import os

import requests


class CloudflareRoutingProvider:

    name = "cloudflare_routing_provider"

    model = "@cf/meta/llama-3.1-8b-instruct-fast"

    MAX_PROMPT_CHARACTERS = 24_000

    def __init__(
        self,
        account_id: str | None = None,
        api_token: str | None = None,
    ) -> None:

        self.account_id = (
            account_id
            or os.environ.get(
                "CLOUDFLARE_ACCOUNT_ID"
            )
        )

        self.api_token = (
            api_token
            or os.environ.get(
                "CLOUDFLARE_API_TOKEN"
            )
        )

    def is_available(
        self,
    ) -> bool:

        return bool(
            self.account_id
            and self.api_token
        )

    def route(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        if not self.is_available():
            raise ValueError(
                "Cloudflare routing credentials "
                "are unavailable."
            )

        prepared_prompt = self._limit_prompt(
            prompt
        )

        endpoint = (
            "https://api.cloudflare.com/client/v4/"
            "accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.api_token}"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prepared_prompt,
            "max_tokens": 900,
            "temperature": 0.0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "use_tool",
                                "use_working_memory",
                                "respond_normally",
                            ],
                        },
                        "tool_name": {
                            "type": "string",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                        "arguments": {
                            "type": "object",
                        },
                        "direct_answer": {
                            "type": "string",
                        },
                        "memory_reference": {
                            "type": "string",
                        },
                        "memory_candidate": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                },
                                "memory_type": {
                                    "type": "string",
                                },
                                "subject": {
                                    "type": "string",
                                },
                                "attribute": {
                                    "type": "string",
                                },
                                "value": {
                                    "type": "string",
                                },
                                "selection_origin": {
                                    "type": [
                                        "string",
                                        "null",
                                    ],
                                },
                                "proposed_scope": {
                                    "type": "string",
                                },
                                "sensitivity": {
                                    "type": "string",
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "source": {
                                    "type": "string",
                                },
                                "project": {
                                    "type": [
                                        "string",
                                        "null",
                                    ],
                                },
                            },
                        },
                        "reason": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "action",
                        "tool_name",
                        "confidence",
                        "arguments",
                        "direct_answer",
                        "memory_reference",
                        "memory_candidate",
                        "reason",
                    ],
                },
            },
        }

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=20,
            )

        except requests.Timeout as error:
            raise RuntimeError(
                "Cloudflare routing timed out."
            ) from error

        except requests.RequestException as error:
            raise RuntimeError(
                "Cloudflare routing request failed."
            ) from error

        if not response.ok:
            raise RuntimeError(
                "Cloudflare routing failed with "
                f"HTTP {response.status_code}."
            )

        try:
            response_data = response.json()

        except ValueError as error:
            raise RuntimeError(
                "Cloudflare returned invalid JSON."
            ) from error

        if not response_data.get(
            "success",
            False,
        ):
            raise RuntimeError(
                "Cloudflare rejected the routing request."
            )

        result = response_data.get(
            "result",
            {},
        )

        if not isinstance(
            result,
            dict,
        ):
            raise RuntimeError(
                "Cloudflare returned an invalid result."
            )

        raw_response = result.get(
            "response",
            "",
        )

        if isinstance(
            raw_response,
            dict,
        ):
            routed_response = json.dumps(
                raw_response,
                ensure_ascii=False,
            )

        else:
            routed_response = str(
                raw_response or ""
            ).strip()

        if not routed_response:
            raise RuntimeError(
                "Cloudflare returned no routing decision."
            )

        return {
            "provider": "cloudflare",
            "model": self.model,
            "status": "success",
            "response": routed_response,
        }

    def _limit_prompt(
        self,
        prompt: str,
    ) -> str:

        cleaned_prompt = str(
            prompt or ""
        ).strip()

        if (
            len(cleaned_prompt)
            <= self.MAX_PROMPT_CHARACTERS
        ):
            return cleaned_prompt

        beginning = cleaned_prompt[
            :16_000
        ]

        ending = cleaned_prompt[
            -8_000:
        ]

        return (
            beginning
            + "\n\n"
            "[COMPACTED ROUTING CONTEXT]"
            "\n\n"
            + ending
        )
