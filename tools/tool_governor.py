"""
DeDe - Tool Governor

Selects whether a user request requires a registered tool.

The decision is semantic and multilingual.
It does not depend on fixed lists of language-specific keywords.
"""

from __future__ import annotations

import json
from typing import Any
from llm.llm_engine import LLMEngine


class ToolGovernor:
    """
    Decide whether DeDe should use a registered tool
    before sending the request to the normal reasoning pipeline.
    """

    name = "tool_governor"

    def __init__(
        self,
        llm_engine: LLMEngine,
    ) -> None:
        self.llm_engine = llm_engine

    def decide(
        self,
        text: str,
        available_tools: list[dict[str, Any]],
        provider: str,
    ) -> dict[str, Any]:
        """
        Return a normalized tool decision.

        The Governor must understand the user's intention
        independently of the language used.
        """

        cleaned_text = str(
            text or ""
        ).strip()

        if not cleaned_text:
            return self._normal_decision(
                reason="Empty user message.",
            )

        if not available_tools:
            return self._normal_decision(
                reason="No tool is currently registered.",
            )
            
        cleaned_provider = str(
            provider or ""
        ).strip()

        if not cleaned_provider:
            return self._normal_decision(
                reason=(
                    "No active reasoning provider "
                    "is available for tool selection."
                ),
            )

        tool_descriptions = []

        for tool in available_tools:
            tool_descriptions.append(
                {
                    "name": tool.get(
                        "name",
                        "",
                    ),
                    "description": tool.get(
                        "description",
                        "",
                    ),
                    "input_schema": tool.get(
                        "input_schema",
                        {},
                    ),
                }
            )

        system_instruction = """
You are DeDe's multilingual Tool Governor.

Your only role is to decide whether the user's request should
invoke one of the registered tools.

Understand the intention semantically, regardless of language,
spelling mistakes, grammar, accent marks or informal phrasing.

Do not answer the user's request.

Use a tool only when the user is clearly asking for an action
that the tool actually performs.

For image generation:
- Select image_generator when the user asks to create, generate,
  draw, design, visualize or produce a new image.
- The request may be written in any language.
- Preserve the user's requested subject and visual constraints.
- Build a clean image prompt in the same language as the user.
- Do not select image_generator when the user merely discusses,
  analyzes or asks a question about images.

When no registered tool clearly applies, choose respond_normally.

Return only valid JSON with this exact structure:

{
  "action": "use_tool" or "respond_normally",
  "tool_name": "registered tool name or empty string",
  "confidence": number from 0 to 1,
  "arguments": {},
  "reason": "short internal explanation"
}

For image_generator, arguments must have this form:

{
  "prompt": "clean visual description",
  "size": "1024x1024",
  "quality": "medium",
  "transparent_background": false
}
""".strip()

        user_instruction = (
            "REGISTERED TOOLS:\n"
            + json.dumps(
                tool_descriptions,
                ensure_ascii=False,
                indent=2,
            )
            + "\n\nUSER MESSAGE:\n"
            + cleaned_text
        )

        governor_prompt = (
            system_instruction
            + "\n\n"
            + user_instruction
        )

        try:
            engine_response = self.llm_engine.ask(
                prompt=governor_prompt,
                profile="fast",
                providers=[
                    cleaned_provider,
                ],
                enabled=True,
            )

            raw_output = str(
                engine_response.get(
                    "response",
                    "",
                )
                or ""
            ).strip()

            if not raw_output:
                raise ValueError(
                    "The active reasoning provider "
                    "returned no tool decision."
                )

            parsed = self._parse_json(
                raw_output
            )

            return self._validate_decision(
                decision=parsed,
                available_tools=available_tools,
            )

        except Exception as error:
            return {
                "governor": self.name,
                "status": "fallback",
                "action": "respond_normally",
                "tool_name": "",
                "confidence": 0.0,
                "arguments": {},
                "reason": (
                    "Tool selection failed; normal DeDe "
                    "reasoning will continue."
                ),
                "error": str(error),
            }

    def _parse_json(
        self,
        raw_output: str,
    ) -> dict[str, Any]:
        """
        Parse a JSON object, including responses accidentally
        wrapped in Markdown code fences.
        """

        cleaned = raw_output.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix(
                "```json"
            )

            cleaned = cleaned.removeprefix(
                "```"
            )

            cleaned = cleaned.removesuffix(
                "```"
            )

            cleaned = cleaned.strip()

        parsed = json.loads(
            cleaned
        )

        if not isinstance(
            parsed,
            dict,
        ):
            raise ValueError(
                "Tool Governor response is not a JSON object."
            )

        return parsed

    def _validate_decision(
        self,
        decision: dict[str, Any],
        available_tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Validate tool name, confidence and arguments.
        """

        registered_names = {
            str(
                tool.get(
                    "name",
                    "",
                )
            ).strip()
            for tool in available_tools
            if tool.get("name")
        }

        action = str(
            decision.get(
                "action",
                "respond_normally",
            )
        ).strip()

        tool_name = str(
            decision.get(
                "tool_name",
                "",
            )
        ).strip()

        arguments = decision.get(
            "arguments",
            {},
        )

        if not isinstance(
            arguments,
            dict,
        ):
            arguments = {}

        try:
            confidence = float(
                decision.get(
                    "confidence",
                    0.0,
                )
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
            action != "use_tool"
            or tool_name not in registered_names
            or confidence < 0.70
        ):
            return self._normal_decision(
                reason=str(
                    decision.get(
                        "reason",
                        "No registered tool clearly applies.",
                    )
                ),
                confidence=confidence,
            )

        if tool_name == "image_generator":
            prompt = str(
                arguments.get(
                    "prompt",
                    "",
                )
            ).strip()

            if not prompt:
                return self._normal_decision(
                    reason=(
                        "Image generation was selected, "
                        "but no usable image prompt was produced."
                    ),
                    confidence=confidence,
                )

            arguments = {
                "prompt": prompt,
                "size": str(
                    arguments.get(
                        "size",
                        "1024x1024",
                    )
                ),
                "quality": str(
                    arguments.get(
                        "quality",
                        "medium",
                    )
                ),
                "transparent_background": bool(
                    arguments.get(
                        "transparent_background",
                        False,
                    )
                ),
            }

        return {
            "governor": self.name,
            "status": "ready",
            "action": "use_tool",
            "tool_name": tool_name,
            "confidence": confidence,
            "arguments": arguments,
            "reason": str(
                decision.get(
                    "reason",
                    "A registered tool matches the request.",
                )
            ),
        }

    def _normal_decision(
        self,
        reason: str,
        confidence: float = 1.0,
    ) -> dict[str, Any]:
        return {
            "governor": self.name,
            "status": "ready",
            "action": "respond_normally",
            "tool_name": "",
            "confidence": confidence,
            "arguments": {},
            "reason": reason,
        }
