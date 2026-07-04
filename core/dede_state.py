"""
DeDe - Internal State

Shared internal state for DeDe.

This is the first layer that gives DeDe continuity:
- who DeDe is
- who is speaking
- preferred language
- conversation stage
- response behavior
"""

from typing import Any


class DeDeState:

    name = "dede_state"

    def build(
        self,
        text: str,
        user_memory: dict[str, Any] | None = None,
        dede_identity: dict[str, Any] | None = None,
        dialogue_profile: dict[str, Any] | None = None,
        conversation_context: dict[str, Any] | None = None,
        retrieved_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        user_memory = user_memory or {}
        dede_identity = dede_identity or {}
        dialogue_profile = dialogue_profile or {}
        conversation_context = conversation_context or {}
        retrieved_memory = retrieved_memory or {}

        owner = retrieved_memory.get("owner", {})

        user_name = (
            user_memory.get("preferred_name")
            or owner.get("preferred_name")
            or dede_identity.get("user_name")
        )

        language = (
            dialogue_profile.get("language")
            or owner.get("preferred_language")
            or dede_identity.get("preferred_language")
            or "unknown"
        )

        turn_count = conversation_context.get("turn_count", 0)

        conversation_stage = self._conversation_stage(turn_count)

        return {
            "engine": self.name,
            "status": "ready",
            "assistant": {
                "name": dede_identity.get(
                    "assistant_identity",
                    "DeDe",
                ),
                "role": dede_identity.get(
                    "assistant_role",
                    "cognitive_daimon",
                ),
            },
            "user": {
                "is_person": True,
                "preferred_name": user_name,
                "language": language,
            },
            "conversation": {
                "turn_count": turn_count,
                "stage": conversation_stage,
                "current_text": text,
            },
            "behavior": {
                "use_user_name": bool(user_name),
                "avoid_input_label": True,
                "avoid_repeating_onboarding": turn_count > 0,
                "avoid_exposing_internal_analysis": True,
                "answer_directly_when_possible": True,
                "follow_latest_user_language": True,
            },
            "summary": self._summary(
                user_name=user_name,
                language=language,
                conversation_stage=conversation_stage,
            ),
        }

    def _conversation_stage(
        self,
        turn_count: int,
    ) -> str:

        if turn_count == 0:
            return "first_contact"

        if turn_count < 3:
            return "early_conversation"

        return "ongoing_conversation"

    def _summary(
        self,
        user_name: str | None,
        language: str,
        conversation_stage: str,
    ) -> str:

        if user_name:
            return (
                f"DeDe is speaking with {user_name} in language '{language}' "
                f"during stage '{conversation_stage}'."
            )

        return (
            f"DeDe is speaking with an unnamed person in language '{language}' "
            f"during stage '{conversation_stage}'."
        )
