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
        retrieved_memory: dict[str, Any] | None = None,
        llm_result: dict[str, Any] | None = None,
        cognitive_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        dede_state = dede_state or {}
        retrieved_memory = retrieved_memory or {}
        llm_result = llm_result or {}
        cognitive_state = cognitive_state or {}

        user_name = (
            dede_state.get("user", {}).get("preferred_name")
            or retrieved_memory.get("owner", {}).get("preferred_name")
            or identity_state.get("user_name")
        )

        language = (
            dede_state.get("user", {}).get("language")
            or identity_state.get("language")
            or "fr"
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

        llm_json = (
            llm_result.get("parsed_json")
            or llm_result.get("llm_response", {})
            or llm_result
        )

        llm_response = (
            llm_json.get("user_facing_response")
            or llm_json.get("response")
        )
        
        if llm_response:
            return llm_response

        if self._looks_like_identity_statement(lowered):
            return self._identity_response(
                display_name=display_name,
                language=language,
            )

        if "input" in lowered:
            return self._input_reduction_response(
                display_name=display_name,
                language=language,
            )

        return self._fallback_response(
            display_name=display_name,
            language=language,
        )

    def _identity_response(
        self,
        display_name: str,
        language: str,
    ) -> str:

        if language == "en":
            return (
                f"Hello {display_name}. I recognize you as the person "
                "speaking to DeDe, not as a simple input."
            )

        if language == "es":
            return (
                f"Hola {display_name}. Te reconozco como la persona "
                "que habla con DeDe, no como una simple entrada."
            )

        if language == "fil":
            return (
                f"Kumusta {display_name}. Kinikilala kita bilang taong "
                "nakikipag-usap kay DeDe, hindi bilang simpleng input."
            )

        return (
            f"Bonjour {display_name}. Je te reconnais comme la personne "
            "qui parle à DeDe, pas comme un simple input."
        )

    def _input_reduction_response(
        self,
        display_name: str,
        language: str,
    ) -> str:

        if language == "en":
            return (
                f"You are right, {display_name}. Technically, the system "
                "receives a message, but you are not an input. You are the "
                "person speaking to DeDe."
            )

        if language == "es":
            return (
                f"Tienes razón, {display_name}. Técnicamente, el sistema "
                "recibe un mensaje, pero tú no eres una entrada. Eres la "
                "persona que habla con DeDe."
            )

        if language == "fil":
            return (
                f"Tama ka, {display_name}. Sa teknikal na antas, tumatanggap "
                "ang sistema ng mensahe, pero hindi ka isang input. Ikaw ang "
                "taong nakikipag-usap kay DeDe."
            )

        return (
            f"Tu as raison {display_name}. Techniquement, le système reçoit "
            "un message, mais toi, tu n'es pas un input. Tu es la personne "
            "qui parle à DeDe."
        )

    def _fallback_response(
        self,
        display_name: str,
        language: str,
    ) -> str:

        if language == "en":
            return (
                f"{display_name}, I am listening. I will use my cognitive "
                "analysis to clarify the question without reducing you to "
                "the message itself."
            )

        if language == "es":
            return (
                f"{display_name}, te escucho. Usaré mi análisis cognitivo "
                "para aclarar la cuestión sin reducirte al mensaje mismo."
            )

        if language == "fil":
            return (
                f"{display_name}, nakikinig ako. Gagamitin ko ang aking "
                "cognitive analysis para linawin ang tanong nang hindi ka "
                "binabawasan sa mensahe lamang."
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
            "soy ",
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
