"""
DeDe - Dialogue Profile

Detects the user's conversational profile for the current turn.

Initial scope:
- language detection
- tone placeholder
- verbosity placeholder
"""

from typing import Any


class DialogueProfile:

    name = "dialogue_profile"

    def analyze(
        self,
        text: str,
        conversation_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        conversation_context = conversation_context or {}

        language = self._detect_language(text)

        return {
            "profile": self.name,
            "status": "ready",
            "language": language,
            "tone": "neutral",
            "verbosity": "medium",
            "conversation_turns": conversation_context.get(
                "turn_count",
                0,
            ),
            "summary": (
                f"Dialogue profile detected language='{language}', "
                "tone='neutral', verbosity='medium'."
            ),
        }

    def _detect_language(
        self,
        text: str,
    ) -> str:

        lowered = text.lower()

        french_markers = [
            " le ",
            " la ",
            " les ",
            " des ",
            " une ",
            " un ",
            " est ",
            " dans ",
            " avec ",
            " pourquoi ",
            " comment ",
            " quoi ",
            " peux ",
            " tu ",
            "ça",
            "c'est",
            "mécroyance",
        ]

        english_markers = [
            " what ",
            " is ",
            " are ",
            " and ",
            " in ",
            " why ",
            " how ",
            " with ",
            " can ",
            " you ",
            "the ",
            "what is",
            "and in",
        ]

        spanish_markers = [
            " el ",
            " la ",
            " los ",
            " las ",
            " una ",
            " uno ",
            " qué ",
            " que ",
            " por qué ",
            " cómo ",
            " en ",
            " con ",
            "es ",
        ]

        fr_score = self._score_markers(lowered, french_markers)
        en_score = self._score_markers(lowered, english_markers)
        es_score = self._score_markers(lowered, spanish_markers)

        scores = {
            "fr": fr_score,
            "en": en_score,
            "es": es_score,
        }

        best_language = max(
            scores,
            key=scores.get,
        )

        if scores[best_language] == 0:
            return "unknown"

        return best_language

    def _score_markers(
        self,
        text: str,
        markers: list[str],
    ) -> int:

        padded = f" {text} "

        score = 0

        for marker in markers:
            if marker in padded:
                score += 1

        return score
