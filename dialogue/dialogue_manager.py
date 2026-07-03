"""
DeDe - Dialogue Manager

Transforms cognitive analysis into natural dialogue.

The workspace analyzes the input.
DeDe speaks to the person.
"""

from typing import Any


class DialogueManager:

    name = "dialogue_manager"

    def generate_response(
        self,
        user_text: str,
        identity_state: dict[str, Any],
        dede_state: dict[str, Any] | None = None,
        llm_result: dict[str, Any] | None = None,
        cognitive_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        dede_state = dede_state or {}
        llm_result = llm_result or {}
        cognitive_state = cognitive_state or {}

        user_name = (
            dede_state.get("user", {}).get("preferred_name")
            or identity_state.get("user_name")
        )

        language = (
            dede_state.get("user", {}).get("language")
            or "unknown"
        )

        conversation_stage = (
            dede_state.get("conversation", {}).get("stage")
            or "unknown"
        )

        response = self._build_natural_response(
            user_text=user_text,
            user_name=user_name,
            language=language,
            conversation_stage=conversation_stage,
            llm_result=llm_result,
            cognitive_state=cognitive_state,
        )

        return {
            "engine": self.name,
            "status": "ready",
            "response": response,
            "used_user_name": user_name,
            "language": language,
            "conversation_stage": conversation_stage,
            "summary": (
                "Natural dialogue response generated from identity, "
                "memory and cognitive state."
            ),
        }

    def _build_natural_response(
        self,
        user_text: str,
        user_name: str | None,
        language: str,
        conversation_stage: str,
        llm_result: dict[str, Any],
        cognitive_state: dict[str, Any],
    ) -> str:

        lowered = user_text.lower()
        display_name = user_name or self._default_address(language)

        llm_json = llm_result.get("parsed_json", {})
        llm_response = llm_json.get("user_facing_response")

        # --------------------------------------------------
        # Identity / name recognition
        # --------------------------------------------------

        if self._looks_like_identity_statement(lowered):
            if language == "en":
                return (
                    f"Hello {display_name}. I recognize you as the person "
                    "speaking to DeDe, not as a simple input."
                )

            return (
                f"Bonjour {display_name}. Je te reconnais comme la personne "
                "qui parle à DeDe, pas comme un simple input."
            )

        # --------------------------------------------------
        # Rejection of input reduction
        # --------------------------------------------------

        if "input" in lowered:
            if language == "en":
                return (
                    f"You are right, {display_name}. Technically, the system "
                    "receives a message, but you are not an input. You are the "
                    "person speaking to DeDe."
                )

            return (
                f"Tu as raison {display_name}. Techniquement, le système reçoit "
                "un message, mais toi, tu n'es pas un input. Tu es la personne "
                "qui parle à DeDe."
            )

        # --------------------------------------------------
        # Prefer LLM user-facing response if available
        # --------------------------------------------------

        if llm_response:
            return llm_response

        # --------------------------------------------------
        # Minimal fallback
        # --------------------------------------------------

        if language == "en":
            return (
                f"{display_name}, I am listening. I will use my cognitive "
                "analysis to help clarify the question without reducing you "
                "to the message itself."
            )

        return (
            f"{display_name}, je t'écoute. J'utiliserai mon analyse cognitive "
            "pour clarifier la question sans te réduire au message lui-même."
        )

    def _looks_like_identity_statement(
        self,
        lowered: str,
    ) -> bool:

        identity_markers = [
            "je suis ",
            "je m'appelle ",
            "je m appel",
            "je m'appel",
            "je me nomme ",
            "mon nom est ",
            "i am ",
            "my name is ",
            "me llamo ",
            "mi nombre es ",
            "ako si ",
            "pangalan ko ay ",
        ]

        return any(
            marker in lowered
            for marker in identity_markers
        )

    def _default_address(
        self,
        language: str,
    ) -> str:

        if language == "en":
            return "there"

        if language == "es":
            return "tú"

        if language == "fil":
            return "ikaw"

        return "toi"
