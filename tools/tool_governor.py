"""
DeDe - Tool Governor

Governs three possible routes:
- use a registered tool;
- answer directly from working memory;
- continue through the normal cognitive pipeline.

The decision is semantic and multilingual.
It does not depend on language-specific marker lists.
"""

from __future__ import annotations

import json
from typing import Any

from llm.llm_engine import LLMEngine


class ToolGovernor:
    """
    Select the lightest valid route for the request.
    """

    name = "tool_governor"

    MINIMUM_CONFIDENCE = 0.70

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
        conversation_context: (
            dict[str, Any] | None
        ) = None,
    ) -> dict[str, Any]:
        """
        Return a normalized semantic routing decision.
        """

        cleaned_text = str(
            text or ""
        ).strip()

        if not cleaned_text:
            return self._normal_decision(
                reason="Empty user message.",
            )

        cleaned_provider = str(
            provider or ""
        ).strip()

        if not cleaned_provider:
            return self._normal_decision(
                reason=(
                    "No active reasoning provider "
                    "is available for routing."
                ),
            )

        conversation_context = (
            conversation_context or {}
        )

        tool_descriptions = (
            self._prepare_tool_descriptions(
                available_tools
            )
        )

        working_memory = (
            self._prepare_working_memory(
                conversation_context
            )
        )

        system_instruction = """
You are DeDe's multilingual routing governor.

Your role is not to provide ordinary knowledge or reasoning.
Your role is to select the lightest valid route for the
current user request.

Understand intention semantically, independently of language,
spelling, grammar, accents, informal phrasing or writing quality.

You receive:
1. registered tools and their schemas;
2. recent structured working memory;
3. the current user message.

Choose exactly one action:

1. use_tool
Choose this only when the user clearly requests an action
performed by a registered tool.

2. use_working_memory
Choose this only when the request can be answered completely
and safely from the supplied structured working memory.
Typical cases include asking what DeDe just did, which tool
was used, what artifact was produced, or what the immediately
preceding action concerned.

When choosing use_working_memory:
- use only facts explicitly present in working memory;
- do not invent unavailable content;
- do not claim that an artifact exists unless it is listed;
- write a brief direct_answer in the language of the user;
- preserve exact technical tool names when relevant;
- do not expose internal reasoning.

3. respond_normally
Choose this when the request requires ordinary explanation,
knowledge, interpretation, verification or cognitive reasoning,
or when working memory is insufficient or ambiguous.

Do not choose a route merely because a word resembles a tool
name. Decide from the full semantic intention.

For use_tool, select only an exact registered tool name and
construct arguments that respect its supplied input schema.

Return only valid JSON with this exact structure:

{
  "action": "use_tool" or "use_working_memory" or "respond_normally",
  "tool_name": "exact registered tool name or empty string",
  "confidence": 0.0,
  "arguments": {},
  "direct_answer": "",
  "memory_reference": "",
  "reason": "short internal explanation"
}
""".strip()

        user_instruction = (
            "REGISTERED TOOLS:\n"
            + json.dumps(
                tool_descriptions,
                ensure_ascii=False,
                indent=2,
            )
            + "\n\nSTRUCTURED WORKING MEMORY:\n"
            + json.dumps(
                working_memory,
                ensure_ascii=False,
                indent=2,
            )
            + "\n\nCURRENT USER MESSAGE:\n"
            + cleaned_text
        )

        governor_prompt = (
            system_instruction
            + "\n\n"
            + user_instruction
        )

        try:
            engine_response = (
                self.llm_engine.ask(
                    prompt=governor_prompt,
                    profile="fast",
                    providers=[
                        cleaned_provider,
                    ],
                    enabled=True,
                )
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
                    "returned no routing decision."
                )

            parsed = self._parse_json(
                raw_output
            )

            return self._validate_decision(
                decision=parsed,
                available_tools=(
                    available_tools
                ),
                working_memory=(
                    working_memory
                ),
            )

        except Exception as error:
            return {
                "governor": self.name,
                "status": "fallback",
                "action": "respond_normally",
                "tool_name": "",
                "confidence": 0.0,
                "arguments": {},
                "direct_answer": "",
                "memory_reference": "",
                "reason": (
                    "Routing failed; normal DeDe "
                    "reasoning will continue."
                ),
                "error": str(error),
            }

    def _prepare_tool_descriptions(
        self,
        available_tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Keep only prompt-safe tool metadata.
        """

        prepared = []

        for tool in available_tools or []:
            if not isinstance(
                tool,
                dict,
            ):
                continue

            name = str(
                tool.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not name:
                continue

            prepared.append(
                {
                    "name": name,
                    "description": str(
                        tool.get(
                            "description",
                            "",
                        )
                        or ""
                    ),
                    "input_schema": (
                        tool.get(
                            "input_schema",
                            {},
                        )
                        if isinstance(
                            tool.get(
                                "input_schema",
                                {},
                            ),
                            dict,
                        )
                        else {}
                    ),
                }
            )

        return prepared

    def _prepare_working_memory(
        self,
        conversation_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare compact structured memory without binary data.
        """

        recent_turns = (
            conversation_context.get(
                "recent_turns",
                [],
            )
        )

        if not isinstance(
            recent_turns,
            list,
        ):
            recent_turns = []

        prepared_turns = []

        for turn in recent_turns[-5:]:
            if not isinstance(
                turn,
                dict,
            ):
                continue

            prepared_turns.append(
                {
                    "turn_type": turn.get(
                        "turn_type"
                    ),
                    "user_input": self._limit_text(
                        turn.get(
                            "user_input"
                        ),
                        1200,
                    ),
                    "answer": self._limit_text(
                        turn.get(
                            "answer"
                        ),
                        1600,
                    ),
                    "focus_concept": turn.get(
                        "focus_concept"
                    ),
                    "tool_name": turn.get(
                        "tool_name"
                    ),
                    "tool_status": turn.get(
                        "tool_status"
                    ),
                    "tool_arguments": (
                        turn.get(
                            "tool_arguments",
                            {},
                        )
                        if isinstance(
                            turn.get(
                                "tool_arguments",
                                {},
                            ),
                            dict,
                        )
                        else {}
                    ),
                    "artifacts": (
                        turn.get(
                            "artifacts",
                            [],
                        )
                        if isinstance(
                            turn.get(
                                "artifacts",
                                [],
                            ),
                            list,
                        )
                        else []
                    ),
                    "active_task": (
                        turn.get(
                            "active_task"
                        )
                    ),
                }
            )

        recent_artifacts = (
            conversation_context.get(
                "recent_artifacts",
                [],
            )
        )

        if not isinstance(
            recent_artifacts,
            list,
        ):
            recent_artifacts = []

        active_task = (
            conversation_context.get(
                "active_task"
            )
        )

        if not isinstance(
            active_task,
            dict,
        ):
            active_task = None

        return {
            "status": (
                conversation_context.get(
                    "status",
                    "empty",
                )
            ),
            "turn_count": (
                conversation_context.get(
                    "turn_count",
                    0,
                )
            ),
            "last_turn_type": (
                conversation_context.get(
                    "last_turn_type"
                )
            ),
            "last_tool_name": (
                conversation_context.get(
                    "last_tool_name"
                )
            ),
            "last_tool_status": (
                conversation_context.get(
                    "last_tool_status"
                )
            ),
            "recent_turns": prepared_turns,
            "recent_artifacts": (
                recent_artifacts[-12:]
            ),
            "active_task": active_task,
        }

    def _parse_json(
        self,
        raw_output: str,
    ) -> dict[str, Any]:
        """
        Parse JSON, including accidental Markdown fences.
        """

        cleaned = raw_output.strip()

        if cleaned.startswith(
            "```"
        ):
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
                "Routing response is not "
                "a JSON object."
            )

        return parsed

    def _validate_decision(
        self,
        decision: dict[str, Any],
        available_tools: list[dict[str, Any]],
        working_memory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate the route and prevent unsupported actions.
        """

        registered_names = {
            str(
                tool.get(
                    "name",
                    "",
                )
            ).strip()
            for tool in available_tools or []
            if isinstance(
                tool,
                dict,
            )
            and tool.get(
                "name"
            )
        }

        action = str(
            decision.get(
                "action",
                "respond_normally",
            )
            or "respond_normally"
        ).strip()

        tool_name = str(
            decision.get(
                "tool_name",
                "",
            )
            or ""
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

        direct_answer = str(
            decision.get(
                "direct_answer",
                "",
            )
            or ""
        ).strip()

        memory_reference = str(
            decision.get(
                "memory_reference",
                "",
            )
            or ""
        ).strip()

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

        reason = str(
            decision.get(
                "reason",
                "",
            )
            or ""
        )

        if (
            confidence
            < self.MINIMUM_CONFIDENCE
        ):
            return self._normal_decision(
                reason=(
                    reason
                    or "Routing confidence is insufficient."
                ),
                confidence=confidence,
            )

        if action == "use_working_memory":
            has_memory = bool(
                working_memory.get(
                    "recent_turns"
                )
                or working_memory.get(
                    "recent_artifacts"
                )
            )

            if (
                not has_memory
                or not direct_answer
            ):
                return self._normal_decision(
                    reason=(
                        "Working-memory routing was "
                        "selected without sufficient "
                        "memory or a usable answer."
                    ),
                    confidence=confidence,
                )

            return {
                "governor": self.name,
                "status": "ready",
                "action": (
                    "use_working_memory"
                ),
                "tool_name": "",
                "confidence": confidence,
                "arguments": {},
                "direct_answer": (
                    direct_answer
                ),
                "memory_reference": (
                    memory_reference
                ),
                "reason": (
                    reason
                    or "The answer is fully supported "
                    "by recent working memory."
                ),
            }

        if action == "use_tool":
            if (
                tool_name
                not in registered_names
            ):
                return self._normal_decision(
                    reason=(
                        "The selected tool is not "
                        "registered."
                    ),
                    confidence=confidence,
                )

            return {
                "governor": self.name,
                "status": "ready",
                "action": "use_tool",
                "tool_name": tool_name,
                "confidence": confidence,
                "arguments": arguments,
                "direct_answer": "",
                "memory_reference": "",
                "reason": (
                    reason
                    or "A registered tool matches "
                    "the requested action."
                ),
            }

        return self._normal_decision(
            reason=(
                reason
                or "The normal cognitive pipeline "
                "is required."
            ),
            confidence=confidence,
        )

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
            "direct_answer": "",
            "memory_reference": "",
            "reason": reason,
        }

    def _limit_text(
        self,
        value: Any,
        limit: int,
    ) -> str:

        text = str(
            value or ""
        ).strip()

        if len(text) <= limit:
            return text

        return (
            text[:limit].rstrip()
            + "..."
        )
