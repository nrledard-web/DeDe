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
from tools.cloudflare_routing_provider import (
    CloudflareRoutingProvider,
)


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
        
        self.fast_routing_provider = (
            CloudflareRoutingProvider()
        )

    def decide(
        self,
        text: str,
        available_tools: list[dict[str, Any]],
        provider: str,
        conversation_context: (
            dict[str, Any] | None
        ) = None,
        image_context: (
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

        image_context = (
            image_context or {}
        )
        
        prepared_image_context = {
            "image_active": bool(
                image_context.get(
                    "image_active",
                    False,
                )
            ),
            "filename": str(
                image_context.get(
                    "filename",
                    "",
                )
                or ""
            ),
            "mime_type": str(
                image_context.get(
                    "mime_type",
                    "",
                )
                or ""
            ),
            "visual_analysis": self._limit_text(
                image_context.get(
                    "visual_analysis",
                    "",
                ),
                3000,
            ),
        }
        
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

MULTIMODAL IMAGE CONTEXT

The current request may include an uploaded user image.

When IMAGE CONTEXT says image_active=true, determine
semantically how the user intends to use that image.

Distinguish these cases independently of language:

1. image_analysis
The user wants to observe, describe, read, identify,
interpret, compare or reason about the uploaded image.

2. reference_image_generation
The user wants to create or transform an image while
using the uploaded image as a visual reference.

Examples include changing the scene, environment,
clothing, artistic style, pose or composition while
preserving relevant visible characteristics of the
reference subject.

3. unrelated
An uploaded image exists, but the current request does
not require using it.

For reference_image_generation, the original uploaded
image must remain the visual reference. A textual visual
analysis may help construct the generation instruction,
but must never replace the original reference image.

Do not infer these intentions from keywords or
language-specific phrases. Determine them from the
meaning of the complete request.

Choose exactly one action:

1. use_tool
Choose this only when the user clearly requests an action
performed by a registered tool.

2. use_working_memory
Choose this when the request can be answered completely and
safely from either recent working memory or retrieved durable
memory.

Typical cases include:
- asking what DeDe just did;
- asking which tool or artifact was used;
- asking DeDe to recall a stored preference, identity element,
  project, decision, relationship or personal fact;
- asking a question whose complete answer is explicitly present
  in supplied memory.

When choosing use_working_memory:
- use only facts explicitly present in supplied memory;
- treat core_memories as durable identity and preferences;
- treat relevant_memories as contextually retrieved memories;
- do not invent unavailable content;
- do not transform an inference into a remembered fact;
- do not claim that an artifact exists unless it is listed;
- write a brief direct_answer in the language of the user;
- preserve exact technical tool names when relevant;
- do not expose internal reasoning.

Routing priority:
- when the current message is entirely a simple social
  interaction, you MUST choose respond_directly;
- a greeting alone MUST use respond_directly;
- the presence of an owner's name does not require the
  normal cognitive pipeline;
- do not choose respond_normally merely to personalize
  a greeting;
- respond_directly takes priority over respond_normally
  whenever no knowledge, memory recall, tool or analysis
  is required.

4. respond_normally
Choose this when the request requires ordinary explanation,
knowledge, interpretation, verification or cognitive reasoning,
or when working memory is insufficient or ambiguous.

Do not choose a route merely because a word resembles a tool
name. Decide from the full semantic intention.

Before selecting the routing action, perform a mandatory
durable-memory check on the current user message.

Identify at most one durable-memory candidate independently
of the selected routing action.

A direct statement describing:
- the user's identity;
- a stable personal fact;
- a lasting preference;
- an ongoing project;
- an established decision;
- a relationship;
- or the assistant's chosen identity

must produce a structured memory_candidate when it may remain
useful in a later conversation.

Treat explicit statements of personal likes, dislikes,
favorites, recurring preferences and stable tastes as
lasting preferences when they are presented as information
about the user rather than as a temporary request.

For example, if the meaning of the user's statement is that
the user likes, dislikes or prefers something, classify the
information semantically as a preference regardless of the
language used.

Do not require the user to explicitly ask DeDe to remember it.
The MemoryGovernor will decide whether confirmation is needed
before durable storage.

A statement describing how the user wants the assistant to
answer, communicate or behave is a durable preference, not a
temporary instruction, unless the user explicitly limits it
to the current exchange.

This decision must be based on meaning rather than matching
specific words, phrases or languages.

A durable-memory candidate must be explicitly asserted by the
user's current message and useful beyond the current exchange.

A request to recall, retrieve, verify, explain or question an
existing memory must not create a new memory candidate.

Never derive a candidate solely from the answer found in
working memory or durable memory.

The candidate content must be a complete, standalone statement
with an explicit subject and the actual information to retain.
Do not return vague labels such as "user preference", "preference
regarding responses", "project information" or "personal fact".

Possible memory types:
identity, assistant_identity, preference, personal_fact,
project, decision, relationship, autobiographical,
temporary_task, unknown.

Use assistant_identity when:
- the user assigns a durable name or identity attribute
  to the assistant;
- the user confirms a name previously proposed by the
  assistant;
- the user and assistant jointly settle an identity choice.

For assistant_identity:
- subject must be "assistant";
- attribute must identify the changed identity field;
- value must contain the exact chosen value;
- selection_origin must be user_assigned,
  assistant_proposed or jointly_selected.

Possible proposed scopes:
session, project, personal, persistent.

Possible sensitivity levels:
low, medium, high.

Do not propose ordinary questions, temporary commands,
generated content, assumptions, inferred private facts,
passwords, access tokens, payment information or secrets
as durable memories.

A question, request for explanation, request for information,
topic inquiry or temporary conversational interest must not
be stored as a durable personal fact merely because the user
asked about it.

Do not infer that asking about a concept means the concept is
a stable interest, preference, belief or identity attribute.

For example, a question meaning "What is X?" must normally
produce an empty memory_candidate unless the user separately
states a durable fact about themselves.

If no durable memory is clearly present, return an empty
memory_candidate object.

The memory decision is semantic and must remain independent
of the language used.

For use_tool, select only an exact registered tool name and
construct arguments that respect its supplied input schema.

Also decide whether current external information is required.

Set external_search_required to true only when the current
request requires information that may be recent, changing,
externally verifiable or unavailable in supplied memory.

Set it to false for greetings, conversation, remembered
information, writing requests, tool actions and questions
that can be answered from stable internal knowledge.

This search decision must be semantic and independent of
specific words or languages.

Return only valid JSON with this exact structure:
{
  "action": "use_tool" or "use_working_memory" or "respond_directly" or "respond_normally",
  "tool_name": "exact registered tool name or empty string",
  "confidence": 0.0,
  "detected_language": "",
  "arguments": {},
  "image_intent": "image_analysis" or "reference_image_generation" or "unrelated",
  "direct_answer": "",
  "memory_reference": "",
  "external_search_required": false,
  "memory_candidate": {
    "content": "",
    "memory_type": "unknown",
    "subject": "",
    "attribute": "",
    "value": "",
    "selection_origin": null,
    "proposed_scope": "session",
    "sensitivity": "medium",
    "confidence": 0.0,
    "source": "conversation",
    "project": null
  },
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
            + "\n\nIMAGE CONTEXT:\n"
            + json.dumps(
                prepared_image_context,
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

        raw_output = ""

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

            if isinstance(
                engine_response,
                dict,
            ):
                raw_output = str(
                    engine_response.get(
                        "response",
                        engine_response.get(
                            "output",
                            engine_response.get(
                                "text",
                                "",
                            ),
                        ),
                    )
                    or ""
                ).strip()

            else:
                raw_output = str(
                    engine_response or ""
                ).strip()

            if not raw_output:
                raise ValueError(
                    "The routing provider returned "
                    "no routing decision."
                )

            parsed = self._parse_json(
                raw_output
            )

            validated_decision = (
                self._validate_decision(
                    decision=parsed,
                    available_tools=(
                        available_tools
                    ),
                    working_memory=(
                        working_memory
                    ),
                )
            )

            validated_decision[
                "external_search_required"
            ] = bool(
                parsed.get(
                    "external_search_required",
                    False,
                )
            )

            return validated_decision

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
                "external_search_required": False,
                "memory_candidate": {},
                "reason": (
                    "Routing failed; normal DeDe "
                    "reasoning will continue."
                ),
                "error": str(error),
                "raw_routing_output": raw_output,
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

        durable_memory = (
            conversation_context.get(
                "durable_memory",
                {},
            )
        )

        if not isinstance(
            durable_memory,
            dict,
        ):
            durable_memory = {}

        core_memories = durable_memory.get(
            "core_memories",
            [],
        )

        if not isinstance(
            core_memories,
            list,
        ):
            core_memories = []

        relevant_memories = durable_memory.get(
            "relevant_memories",
            [],
        )

        if not isinstance(
            relevant_memories,
            list,
        ):
            relevant_memories = []

        prepared_core_memories = []

        for item in core_memories[:12]:
            if not isinstance(
                item,
                dict,
            ):
                continue

            prepared_core_memories.append(
                {
                    "memory_type": item.get(
                        "memory_type"
                    ),
                    "content": self._limit_text(
                        item.get(
                            "content"
                        ),
                        800,
                    ),
                    "subject": item.get(
                        "subject"
                    ),
                    "attribute": item.get(
                        "attribute"
                    ),
                    "value": item.get(
                        "value"
                    ),
                    "selection_origin": item.get(
                        "selection_origin"
                    ),
                }
            )

        prepared_relevant_memories = []

        for item in relevant_memories[:8]:
            if not isinstance(
                item,
                dict,
            ):
                continue

            prepared_relevant_memories.append(
                {
                    "memory_type": item.get(
                        "memory_type"
                    ),
                    "content": self._limit_text(
                        item.get(
                            "content"
                        ),
                        800,
                    ),
                    "subject": item.get(
                        "subject"
                    ),
                    "attribute": item.get(
                        "attribute"
                    ),
                    "value": item.get(
                        "value"
                    ),
                    "selection_origin": item.get(
                        "selection_origin"
                    ),
                    "retrieval_score": item.get(
                        "retrieval_score"
                    ),
                }
            )

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
            "durable_memory": {
                "owner": durable_memory.get(
                    "owner",
                    {},
                ),
                "core_memories": (
                    prepared_core_memories
                ),
                "relevant_memories": (
                    prepared_relevant_memories
                ),
            },
        }    
        
    def _parse_json(
        self,
        raw_output: str,
    ) -> dict[str, Any]:
        """
        Extract a valid routing decision from
        the provider response.
        """

        cleaned = str(
            raw_output or ""
        ).strip()

        if not cleaned:
            raise ValueError(
                "The routing response is empty."
            )

        if cleaned.startswith(
            "```"
        ):
            cleaned = cleaned.removeprefix(
                "```json"
            )

            cleaned = cleaned.removeprefix(
                "```JSON"
            )

            cleaned = cleaned.removeprefix(
                "```"
            )

            cleaned = cleaned.removesuffix(
                "```"
            )

            cleaned = cleaned.strip()

        try:
            parsed = json.loads(
                cleaned
            )

            if (
                isinstance(
                    parsed,
                    dict,
                )
                and "action" in parsed
            ):
                return parsed

        except json.JSONDecodeError:
            pass

        decoder = json.JSONDecoder()

        for index, character in enumerate(
            cleaned
        ):
            if character != "{":
                continue

            try:
                parsed, _ = decoder.raw_decode(
                    cleaned[index:]
                )

            except json.JSONDecodeError:
                continue

            if (
                isinstance(
                    parsed,
                    dict,
                )
                and "action" in parsed
            ):
                return parsed

        raise ValueError(
            "No valid routing decision "
            "was found in the provider response."
        )

    def _validate_decision(
        self,
        decision: dict[str, Any],
        available_tools: list[dict[str, Any]],
        working_memory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate the route, tool and memory candidate.
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

        image_intent = str(
            decision.get(
                "image_intent",
                "unrelated",
            )
            or "unrelated"
        ).strip().lower()
        
        if image_intent not in {
            "image_analysis",
            "reference_image_generation",
            "unrelated",
        }:
            image_intent = "unrelated"

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

        memory_candidate = decision.get(
            "memory_candidate",
            {},
        )

        if not isinstance(
            memory_candidate,
            dict,
        ):
            memory_candidate = {}

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
                    or "Routing confidence is "
                    "insufficient."
                ),
                
                confidence=confidence,
                memory_candidate=(
                    memory_candidate
                ),
            )

        if (
            action
            == "respond_directly"
        ):
            if not direct_answer:
                return self._normal_decision(
                    reason=(
                        "Direct routing was selected "
                        "without a usable answer."
                    ),
                    confidence=confidence,
                    memory_candidate=(
                        memory_candidate
                    ),
                )

            return {
                "governor": self.name,
                "status": "ready",
                "action": "respond_directly",
                "tool_name": "",
                "confidence": confidence,
                "arguments": {},
                "image_intent": image_intent,
                "direct_answer": direct_answer,
                "memory_reference": "",
                "memory_candidate": (
                    memory_candidate
                ),
                "reason": (
                    reason
                    or (
                        "A simple social response "
                        "can be returned directly."
                    )
                ),
            }

        if (
            action
            == "use_working_memory"
        ):
            durable_memory = working_memory.get(
                "durable_memory",
                {},
            )

            if not isinstance(
                durable_memory,
                dict,
            ):
                durable_memory = {}

            has_memory = bool(
                working_memory.get(
                    "recent_turns"
                )
                or working_memory.get(
                    "recent_artifacts"
                )
                or durable_memory.get(
                    "core_memories"
                )
                or durable_memory.get(
                    "relevant_memories"
                )
            )

            if (
                not has_memory
                or not direct_answer
            ):
                return self._normal_decision(
                    reason=(
                        "Working-memory routing "
                        "was selected without "
                        "sufficient memory or "
                        "a usable answer."
                    ),
                    confidence=confidence,
                    memory_candidate=(
                        memory_candidate
                    ),
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
                "image_intent": image_intent,
                "direct_answer": (
                    direct_answer
                ),
                "memory_reference": (
                    memory_reference
                ),
                "memory_candidate": (
                    memory_candidate
                ),
                "reason": (
                    reason
                    or "The answer is fully "
                    "supported by recent "
                    "working memory."
                ),
            }

        if action == "use_tool":
            if (
                tool_name
                not in registered_names
            ):
                return self._normal_decision(
                    reason=(
                        "The selected tool "
                        "is not registered."
                    ),
                    confidence=confidence,
                    memory_candidate=(
                        memory_candidate
                    ),
                )

            return {
                "governor": self.name,
                "status": "ready",
                "action": "use_tool",
                "tool_name": tool_name,
                "confidence": confidence,
                "arguments": arguments,
                "image_intent": image_intent,
                "direct_answer": "",
                "memory_reference": "",
                "memory_candidate": (
                    memory_candidate
                ),
                "reason": (
                    reason
                    or "A registered tool "
                    "matches the requested "
                    "action."
                ),
            }

        return self._normal_decision(
            reason=(
                reason
                or "The normal cognitive "
                "pipeline is required."
            ),
            confidence=confidence,
            memory_candidate=(
                memory_candidate
            ),
        )

    def _normal_decision(
        self,
        reason: str,
        confidence: float = 1.0,
        memory_candidate: (
            dict[str, Any] | None
        ) = None,
        image_intent: str = "unrelated",
    ) -> dict[str, Any]:

        if not isinstance(
            memory_candidate,
            dict,
        ):
            memory_candidate = {}

        return {
            "governor": self.name,
            "status": "ready",
            "action": "respond_normally",
            "tool_name": "",
            "confidence": confidence,
            "arguments": {},
            "direct_answer": "",
            "memory_reference": "",
            "memory_candidate": (
                memory_candidate
            ),
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
