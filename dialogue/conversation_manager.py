"""
DeDe - Conversation Manager

Maintains a unified short-term context containing:
- dialogue turns;
- tool actions;
- generated artifacts;
- recent concepts;
- recent topics.

This is DeDe's working conversation memory.
"""

from __future__ import annotations

from typing import Any


class ConversationManager:

    name = "conversation_manager"

    MAX_HISTORY_TURNS = 20
    CONTEXT_TURNS = 5
    MAX_ARTIFACTS = 12

    def build_context(
        self,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Build a compact working context from recent turns.
        """

        history = list(
            history or []
        )

        if not history:
            return {
                "manager": self.name,
                "status": "empty",
                "turn_count": 0,
                "last_turn_type": None,
                "last_user_input": None,
                "last_answer": None,
                "last_focus_concept": None,
                "last_tool_name": None,
                "last_tool_status": None,
                "recent_focus_concepts": [],
                "recent_topics": [],
                "recent_turns": [],
                "recent_artifacts": [],
                "active_task": None,
                "summary": (
                    "No previous conversation "
                    "context available."
                ),
            }

        recent_history = history[
            -self.CONTEXT_TURNS:
        ]

        last_turn = history[-1]

        recent_focus_concepts = []

        for turn in recent_history:
            focus = turn.get(
                "focus_concept"
            )

            if focus:
                recent_focus_concepts.append(
                    str(focus)
                )

        recent_focus_concepts = self._unique(
            recent_focus_concepts
        )

        recent_topics = []

        for turn in recent_history:
            topics = turn.get(
                "topics",
                [],
            )

            if isinstance(
                topics,
                list,
            ):
                recent_topics.extend(
                    str(topic)
                    for topic in topics
                    if topic
                )

        recent_topics = self._unique(
            recent_topics
        )

        recent_turns = [
            self._build_turn_context(
                turn
            )
            for turn in recent_history
        ]

        recent_artifacts = []

        for turn in recent_history:
            artifacts = turn.get(
                "artifacts",
                [],
            )

            if not isinstance(
                artifacts,
                list,
            ):
                continue

            for artifact in artifacts:
                if isinstance(
                    artifact,
                    dict,
                ):
                    recent_artifacts.append(
                        dict(artifact)
                    )

        recent_artifacts = recent_artifacts[
            -self.MAX_ARTIFACTS:
        ]

        active_task = self._find_active_task(
            recent_history
        )

        return {
            "manager": self.name,
            "status": "ready",
            "turn_count": len(history),
            "last_turn_type": last_turn.get(
                "turn_type",
                "dialogue",
            ),
            "last_user_input": last_turn.get(
                "user_input"
            ),
            "last_answer": last_turn.get(
                "answer"
            ),
            "last_focus_concept": last_turn.get(
                "focus_concept"
            ),
            "last_tool_name": last_turn.get(
                "tool_name"
            ),
            "last_tool_status": last_turn.get(
                "tool_status"
            ),
            "recent_focus_concepts": (
                recent_focus_concepts
            ),
            "recent_topics": recent_topics,
            "recent_turns": recent_turns,
            "recent_artifacts": recent_artifacts,
            "active_task": active_task,
            "summary": (
                "Unified conversation context "
                f"available with {len(history)} "
                "previous turn(s)."
            ),
        }

    def add_turn(
        self,
        history: list[dict[str, Any]] | None,
        user_input: str,
        user_response: dict[str, Any],
        report: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Add one ordinary dialogue turn.
        """

        history = list(
            history or []
        )

        topics = self._extract_topics(
            report
        )

        focus_concept = (
            self._extract_focus_concept(
                report=report,
                topics=topics,
            )
        )

        turn = {
            "turn_type": "dialogue",
            "user_input": str(
                user_input or ""
            ),
            "answer": str(
                user_response.get(
                    "final_answer",
                    "",
                )
                or ""
            ),
            "follow_up_question": (
                user_response.get(
                    "follow_up_question"
                )
            ),
            "conversation_mode": (
                user_response.get(
                    "conversation_mode"
                )
            ),
            "focus_concept": focus_concept,
            "topics": topics,
            "tool_name": None,
            "tool_status": None,
            "tool_arguments": {},
            "artifacts": [],
            "active_task": (
                self._infer_dialogue_task(
                    user_input=user_input,
                    focus_concept=(
                        focus_concept
                    ),
                )
            ),
        }

        history.append(
            turn
        )

        return history[
            -self.MAX_HISTORY_TURNS:
        ]

    def add_tool_turn(
        self,
        history: list[dict[str, Any]] | None,
        user_input: str,
        tool_name: str,
        tool_arguments: dict[str, Any] | None,
        tool_result: dict[str, Any] | None,
        tool_history_index: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Add an executed tool action to conversation memory.

        Binary content is never copied into conversation history.
        Only safe references and metadata are retained.
        """

        history = list(
            history or []
        )

        tool_arguments = dict(
            tool_arguments or {}
        )

        tool_result = dict(
            tool_result or {}
        )

        result_data = tool_result.get(
            "data",
            {},
        )

        if not isinstance(
            result_data,
            dict,
        ):
            result_data = {}

        tool_status = str(
            tool_result.get(
                "status",
                "unknown",
            )
        )

        artifacts = self._extract_tool_artifacts(
            tool_name=tool_name,
            tool_status=tool_status,
            result_data=result_data,
            tool_history_index=(
                tool_history_index
            ),
        )

        answer = self._build_tool_answer(
            tool_name=tool_name,
            tool_status=tool_status,
            tool_result=tool_result,
            result_data=result_data,
            artifact_count=len(
                artifacts
            ),
        )

        safe_arguments = (
            self._sanitize_tool_arguments(
                tool_arguments
            )
        )

        topics = self._tool_topics(
            tool_name=tool_name,
            result_data=result_data,
        )

        focus_concept = self._tool_focus(
            tool_name=tool_name,
            tool_arguments=(
                safe_arguments
            ),
            result_data=result_data,
        )

        turn = {
            "turn_type": "tool",
            "user_input": str(
                user_input or ""
            ),
            "answer": answer,
            "follow_up_question": None,
            "conversation_mode": (
                "tool_execution"
            ),
            "focus_concept": (
                focus_concept
            ),
            "topics": topics,
            "tool_name": str(
                tool_name or ""
            ),
            "tool_status": tool_status,
            "tool_arguments": (
                safe_arguments
            ),
            "artifacts": artifacts,
            "active_task": (
                self._infer_tool_task(
                    tool_name=tool_name,
                    tool_arguments=(
                        safe_arguments
                    ),
                )
            ),
        }

        history.append(
            turn
        )

        return history[
            -self.MAX_HISTORY_TURNS:
        ]

    def _build_turn_context(
        self,
        turn: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build a prompt-safe representation of one turn.
        """

        answer = str(
            turn.get(
                "answer",
                "",
            )
            or ""
        )

        if len(answer) > 2000:
            answer = (
                answer[:2000].rstrip()
                + "..."
            )

        user_input = str(
            turn.get(
                "user_input",
                "",
            )
            or ""
        )

        if len(user_input) > 1500:
            user_input = (
                user_input[:1500].rstrip()
                + "..."
            )

        artifacts = turn.get(
            "artifacts",
            [],
        )

        if not isinstance(
            artifacts,
            list,
        ):
            artifacts = []

        return {
            "turn_type": turn.get(
                "turn_type",
                "dialogue",
            ),
            "user_input": user_input,
            "answer": answer,
            "focus_concept": turn.get(
                "focus_concept"
            ),
            "topics": list(
                turn.get(
                    "topics",
                    [],
                )
                or []
            )[:8],
            "tool_name": turn.get(
                "tool_name"
            ),
            "tool_status": turn.get(
                "tool_status"
            ),
            "tool_arguments": dict(
                turn.get(
                    "tool_arguments",
                    {},
                )
                or {}
            ),
            "artifacts": [
                dict(artifact)
                for artifact in artifacts
                if isinstance(
                    artifact,
                    dict,
                )
            ],
            "active_task": turn.get(
                "active_task"
            ),
        }

    def _extract_tool_artifacts(
        self,
        tool_name: str,
        tool_status: str,
        result_data: dict[str, Any],
        tool_history_index: int | None,
    ) -> list[dict[str, Any]]:
        """
        Describe generated files without storing binary data.
        """

        if tool_status != "success":
            return []

        artifact_type = None
        mime_type = str(
            result_data.get(
                "mime_type",
                "",
            )
            or ""
        )

        if (
            result_data.get(
                "image_bytes"
            )
            or mime_type.startswith(
                "image/"
            )
        ):
            artifact_type = "image"

        elif (
            result_data.get(
                "video_bytes"
            )
            or mime_type.startswith(
                "video/"
            )
        ):
            artifact_type = "video"

        elif (
            "pdf" in tool_name.lower()
            or mime_type
            == "application/pdf"
        ):
            artifact_type = "document"

        if not artifact_type:
            return []

        reference = None

        if tool_history_index is not None:
            reference = (
                "tool_history:"
                f"{tool_history_index}"
            )

        artifact = {
            "type": artifact_type,
            "reference": reference,
            "tool_name": tool_name,
            "provider": result_data.get(
                "provider"
            ),
            "model": result_data.get(
                "model"
            ),
            "mime_type": (
                mime_type or None
            ),
            "prompt": result_data.get(
                "prompt"
            ),
            "duration": result_data.get(
                "duration"
            ),
            "aspect_ratio": result_data.get(
                "aspect_ratio"
            ),
            "image_count": result_data.get(
                "image_count"
            ),
        }

        return [
            {
                key: value
                for key, value
                in artifact.items()
                if value is not None
            }
        ]

    def _build_tool_answer(
        self,
        tool_name: str,
        tool_status: str,
        tool_result: dict[str, Any],
        result_data: dict[str, Any],
        artifact_count: int,
    ) -> str:
        """
        Build a compact textual memory of a tool action.
        """

        if tool_status == "success":
            summary = str(
                tool_result.get(
                    "summary",
                    "",
                )
                or result_data.get(
                    "summary",
                    "",
                )
                or "Tool executed successfully."
            )

            if artifact_count:
                return (
                    f"{summary} "
                    f"{artifact_count} artifact(s) "
                    "were produced."
                )

            return summary

        error = str(
            tool_result.get(
                "error",
                "",
            )
            or "Tool execution failed."
        )

        return (
            f"{tool_name} failed: "
            f"{error}"
        )

    def _sanitize_tool_arguments(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Keep prompt-safe metadata and exclude binary content.
        """

        allowed_keys = {
            "prompt",
            "model",
            "size",
            "quality",
            "steps",
            "duration",
            "aspect_ratio",
            "audio",
            "filename",
            "seconds_per_image",
            "background_color",
        }

        safe_arguments = {}

        for key, value in arguments.items():
            if key not in allowed_keys:
                continue

            if isinstance(
                value,
                (
                    str,
                    int,
                    float,
                    bool,
                ),
            ):
                safe_value = value

                if (
                    isinstance(
                        safe_value,
                        str,
                    )
                    and len(
                        safe_value
                    ) > 1000
                ):
                    safe_value = (
                        safe_value[
                            :1000
                        ].rstrip()
                        + "..."
                    )

                safe_arguments[
                    key
                ] = safe_value

        return safe_arguments

    def _tool_topics(
        self,
        tool_name: str,
        result_data: dict[str, Any],
    ) -> list[str]:

        topics = [
            str(
                tool_name or ""
            )
            .replace("_", " ")
            .strip()
            .lower()
        ]

        provider = result_data.get(
            "provider"
        )

        model = result_data.get(
            "model"
        )

        if provider:
            topics.append(
                str(provider).lower()
            )

        if model:
            topics.append(
                str(model).lower()
            )

        return self._unique(
            [
                topic
                for topic in topics
                if self._is_valid_concept(
                    topic
                )
            ]
        )[:8]

    def _tool_focus(
        self,
        tool_name: str,
        tool_arguments: dict[str, Any],
        result_data: dict[str, Any],
    ) -> str | None:

        prompt = str(
            tool_arguments.get(
                "prompt",
                "",
            )
            or result_data.get(
                "prompt",
                "",
            )
            or ""
        ).strip()

        if prompt:
            return prompt[:300]

        cleaned_tool_name = (
            str(
                tool_name or ""
            )
            .replace("_", " ")
            .strip()
            .lower()
        )

        return (
            cleaned_tool_name
            if cleaned_tool_name
            else None
        )

    def _infer_tool_task(
        self,
        tool_name: str,
        tool_arguments: dict[str, Any],
    ) -> dict[str, Any]:

        lowered_tool_name = str(
            tool_name or ""
        ).lower()

        if "image" in lowered_tool_name:
            task_type = (
                "image_generation"
            )

        elif "video" in lowered_tool_name:
            task_type = (
                "video_creation"
            )

        elif (
            "pdf" in lowered_tool_name
            or "document"
            in lowered_tool_name
        ):
            task_type = (
                "document_work"
            )

        else:
            task_type = (
                "tool_action"
            )

        return {
            "type": task_type,
            "status": "active",
            "tool_name": tool_name,
            "prompt": tool_arguments.get(
                "prompt"
            ),
        }

    def _infer_dialogue_task(
        self,
        user_input: str,
        focus_concept: str | None,
    ) -> dict[str, Any]:

        return {
            "type": "dialogue",
            "status": "active",
            "focus": (
                focus_concept
                or str(
                    user_input or ""
                )[:300]
            ),
        }

    def _find_active_task(
        self,
        recent_history: list[dict[str, Any]],
    ) -> dict[str, Any] | None:

        for turn in reversed(
            recent_history
        ):
            active_task = turn.get(
                "active_task"
            )

            if isinstance(
                active_task,
                dict,
            ):
                return dict(
                    active_task
                )

        return None

    def _extract_focus_concept(
        self,
        report: dict[str, Any],
        topics: list[str],
    ) -> str | None:

        cognitive_feedback = report.get(
            "cognitive_feedback",
            {},
        )

        concepts = report.get(
            "concepts",
            {},
        )

        semantic = report.get(
            "semantic",
            {},
        )

        graph_queries = report.get(
            "graph_queries",
            {},
        )

        candidates = []

        candidates.extend(
            cognitive_feedback.get(
                "new_concepts",
                [],
            )
        )

        candidates.extend(
            concepts.get(
                "main_concepts",
                [],
            )
        )

        candidates.extend(
            semantic.get(
                "main_concepts",
                [],
            )
        )

        for item in graph_queries.get(
            "central_nodes",
            [],
        ):
            node = item.get(
                "node"
            )

            if node:
                candidates.append(
                    node
                )

        candidates.extend(
            topics
        )

        scored = []

        for candidate in candidates:
            clean = self._clean_concept(
                candidate
            )

            if not self._is_valid_concept(
                clean
            ):
                continue

            score = self._score_concept(
                concept=clean,
                report=report,
            )

            scored.append(
                {
                    "concept": clean,
                    "score": score,
                }
            )

        if not scored:
            return None

        scored = sorted(
            scored,
            key=lambda item: item[
                "score"
            ],
            reverse=True,
        )

        return scored[0][
            "concept"
        ]

    def _extract_topics(
        self,
        report: dict[str, Any],
    ) -> list[str]:

        cognitive_feedback = report.get(
            "cognitive_feedback",
            {},
        )

        concepts = report.get(
            "concepts",
            {},
        )

        semantic = report.get(
            "semantic",
            {},
        )

        topics = []

        topics.extend(
            cognitive_feedback.get(
                "new_concepts",
                [],
            )
        )

        topics.extend(
            concepts.get(
                "main_concepts",
                [],
            )
        )

        topics.extend(
            semantic.get(
                "main_concepts",
                [],
            )
        )

        cleaned_topics = []

        for topic in topics:
            clean = self._clean_concept(
                topic
            )

            if self._is_valid_concept(
                clean
            ):
                cleaned_topics.append(
                    clean
                )

        return self._unique(
            cleaned_topics
        )[:12]

    def _score_concept(
        self,
        concept: str,
        report: dict[str, Any],
    ) -> float:

        score = 0.0

        cognitive_feedback = report.get(
            "cognitive_feedback",
            {},
        )

        concepts = report.get(
            "concepts",
            {},
        )

        semantic = report.get(
            "semantic",
            {},
        )

        graph_queries = report.get(
            "graph_queries",
            {},
        )

        if concept in [
            self._clean_concept(
                item
            )
            for item in cognitive_feedback.get(
                "new_concepts",
                [],
            )
        ]:
            score += 4.0

        if concept in [
            self._clean_concept(
                item
            )
            for item in concepts.get(
                "main_concepts",
                [],
            )
        ]:
            score += 2.0

        if concept in [
            self._clean_concept(
                item
            )
            for item in semantic.get(
                "main_concepts",
                [],
            )
        ]:
            score += 2.0

        for item in graph_queries.get(
            "central_nodes",
            [],
        ):
            node = self._clean_concept(
                item.get(
                    "node"
                )
            )

            if node == concept:
                score += (
                    float(
                        item.get(
                            "degree",
                            0,
                        )
                    )
                    * 0.2
                )

        score += min(
            len(concept) / 20,
            1.0,
        )

        return round(
            score,
            3,
        )

    def _clean_concept(
        self,
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return (
            str(value)
            .lower()
            .strip()
            .replace(
                "_",
                " ",
            )
        )

    def _is_valid_concept(
        self,
        concept: str,
    ) -> bool:

        if not concept:
            return False

        if len(concept) < 4:
            return False

        forbidden_prefixes = [
            "claim:",
            "metric:",
            "agent:",
            "strategy:",
            "assumption:",
            "missing_dimension:",
            "alternative_hypothesis:",
        ]

        if any(
            concept.startswith(
                prefix
            )
            for prefix
            in forbidden_prefixes
        ):
            return False

        if concept in self._function_words():
            return False

        if (
            concept
            in self._internal_cognitive_terms()
        ):
            return False

        return True

    def _function_words(
        self,
    ) -> set[str]:

        return {
            # French
            "alors", "apres", "après",
            "avec", "dans", "donc",
            "elle", "elles", "encore",
            "entre", "mais", "meme",
            "même", "nous", "pour",
            "quand", "quoi", "sans",
            "sous", "tout", "tous",
            "très", "tres", "vous",

            # English
            "about", "after", "again",
            "also", "because", "before",
            "between", "could", "should",
            "there", "these", "those",
            "under", "where", "which",
            "while", "would",

            # Spanish
            "ahora", "aunque", "como",
            "cuando", "desde", "donde",
            "entonces", "entre", "hasta",
            "para", "pero", "porque",
            "sobre", "tambien", "también",

            # Filipino / Tagalog
            "ang", "ano", "bakit",
            "dahil", "dito", "gusto",
            "hindi", "ikaw", "isang",
            "kailan", "kung", "mga",
            "naman", "ngayon", "para",
            "paano", "saan", "sila",
            "tayo",
        }

    def _internal_cognitive_terms(
        self,
    ) -> set[str]:

        return {
            "mecroyance",
            "mécroyance",
            "certainty",
            "understanding",
            "revisability",
            "reduction",
            "closure",
            "grounding",
            "integration",
            "cognitive filter",
            "cognitive_filter",
            "nouscope",
            "doxa",
            "gnosis",
            "nous",
        }

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:

        seen = set()
        unique_values = []

        for value in values:
            if value not in seen:
                seen.add(
                    value
                )

                unique_values.append(
                    value
                )

        return unique_values
