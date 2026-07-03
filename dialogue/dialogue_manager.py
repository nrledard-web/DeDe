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
        llm_result: dict[str, Any] | None = None,
        cognitive_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        llm_result = llm_result or {}
        cognitive_state = cognitive_state or {}

        user_name = identity_state.get("user_name") or "toi"

        response = self._build_natural_response(
            user_text=user_text,
            user_name=user_name,
            llm_result=llm_result,
            cognitive_state=cognitive_state,
        )

        return {
            "engine": self.name,
            "status": "ready",
            "response": response,
            "used_user_name": identity_state.get("user_name"),
            "summary": "Natural dialogue response generated from identity, memory and cognitive state.",
        }

    def _build_natural_response(
        self,
        user_text: str,
        user_name: str,
        llm_result: dict[str, Any],
        cognitive_state: dict[str, Any],
    ) -> str:

        lowered = user_text.lower()

        if "mon nom est nicolas" in lowered or "je m'appelle nicolas" in lowered or "je me nomme nicolas" in lowered:
            return (
                "D'accord Nicolas. Je te reconnais comme une personne, "
                "pas comme un simple input. À partir de maintenant, je dois "
                "m'adresser à toi par ton nom et utiliser mes analyses internes "
                "pour mieux dialoguer avec toi, pas pour te réduire à une donnée."
            )

        if "pas input" in lowered:
            return (
                f"Tu as raison {user_name}. Le message peut être techniquement "
                "un input pour le système, mais toi, tu n'es pas un input. "
                "Tu es la personne qui parle à DeDe."
            )

        summary = llm_result.get("summary")

        if summary:
            return (
                f"{user_name}, voici ce que je comprends : "
                f"{summary}"
            )

        return (
            f"{user_name}, je t'écoute. Je vais utiliser mon analyse cognitive "
            "pour t'aider à clarifier, comprendre et garder les idées révisables."
        )
