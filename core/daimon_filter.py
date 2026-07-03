"""
DeDe - Daimon Filter

Final identity and behavior filter.

The LLM may reason.
DeDe decides how to speak.
"""

from typing import Any


class DaimonFilter:

    name = "daimon_filter"

    def filter_response(
        self,
        response: dict[str, Any],
        dede_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        dede_state = dede_state or {}

        final_answer = response.get("final_answer", "")
        follow_up = response.get("follow_up_question")

        user = dede_state.get("user", {})
        behavior = dede_state.get("behavior", {})

        user_name = user.get("preferred_name")
        language = user.get("language", "unknown")

        final_answer = self._remove_repetitive_phrases(
            final_answer,
            language,
        )

        final_answer = self._avoid_input_language(
            final_answer,
            language,
        )

        final_answer = self._soften_address(
            final_answer,
            user_name,
            language,
        )

        follow_up = self._filter_follow_up(
            follow_up,
            final_answer,
            language,
            behavior,
        )

        return {
            **response,
            "final_answer": final_answer.strip(),
            "follow_up_question": follow_up,
            "daimon_filter": {
                "status": "applied",
                "user_name": user_name,
                "language": language,
                "summary": (
                    "Response filtered through DeDe identity rules."
                ),
            },
        }

    def _remove_repetitive_phrases(
        self,
        text: str,
        language: str,
    ) -> str:

        unwanted = [
            "Yes, we can continue in the same line of thought.",
            "Oui, on peut poursuivre dans le même fil de réflexion.",
            "Would you like to continue with another domain, or go deeper into this thread?",
            "Souhaites-tu continuer avec un autre domaine ou approfondir ce fil ?",
            "Souhaites-tu maintenant comparer ai avec un autre domaine, ou approfondir ce cas précis ?",
            "Oo, maaari nating ipagpatuloy ang parehong linya ng pag-iisip.",
            "Gusto mo bang magpatuloy sa ibang larangan o palalimin pa natin ang usaping ito?",
        ]

        cleaned = text

        for phrase in unwanted:
            cleaned = cleaned.replace(phrase, "")

        return cleaned

    def _avoid_input_language(
        self,
        text: str,
        language: str,
    ) -> str:

        replacements = {
            "The input": "The message",
            "the input": "the message",
            "L'entrée": "Le message",
            "l'entrée": "le message",
            "input": "message",
        }

        cleaned = text

        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        return cleaned

    def _soften_address(
        self,
        text: str,
        user_name: str | None,
        language: str,
    ) -> str:

        if user_name:
            text = text.replace("Bonjour toi.", f"Bonjour {user_name}.")
            text = text.replace("Hello there.", f"Hello {user_name}.")
            text = text.replace("there,", f"{user_name},")
            text = text.replace("toi,", f"{user_name},")

        return text

    def _filter_follow_up(
        self,
        follow_up: str | None,
        final_answer: str,
        language: str,
        behavior: dict[str, Any],
    ) -> str | None:

        if not follow_up:
            return None

        generic_followups = [
            "Would you like to continue with another domain, or go deeper into this thread?",
            "Souhaites-tu continuer avec un autre domaine ou approfondir ce fil ?",
            "Souhaites-tu approfondir le concept, l’appliquer à un exemple, ou le comparer avec un autre domaine ?",
        ]

        if follow_up in generic_followups:
            return None

        return follow_up
