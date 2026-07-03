"""
DeDe - Dialogue Profile

Detects the user's conversational profile for the current turn.

Current scope:
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

        cleaned = text.strip()

        if not cleaned:
            return "unknown"

        lowered = cleaned.lower()
        padded = f" {lowered} "

        # --------------------------------------------------
        # Strong French identity / dialogue shortcuts
        # --------------------------------------------------

        french_markers = [
            " je ",
            " j'",
            " mon ",
            " ma ",
            " mes ",
            " nom ",
            " nicolas ",
            " pas input ",
            " m'appelle ",
            " m'appel ",
            " appelle ",
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
            " et ",
            " en ",
            " religion ",
            " science ",
            " politique ",
            "ça",
            "c'est",
            "mécroyance",
        ]
        strong_english_markers = [
            "what ",
            "what is",
            "why ",
            "how ",
            "hello",
            "can you",
            "explain",
        ]

        strong_spanish_markers = [
            "hola",
            "qué",
            "que ",
            "por qué",
            "cómo",
            "buenos días",
            "buenas tardes",
        ]

        fr_score = self._score_markers(padded, strong_french_markers)
        en_score = self._score_markers(padded, strong_english_markers)
        es_score = self._score_markers(padded, strong_spanish_markers)

        scores = {
            "fr": fr_score,
            "en": en_score,
            "es": es_score,
        }

        best_language = max(scores, key=scores.get)

        if scores[best_language] > 0:
            return best_language

        # --------------------------------------------------
        # Strong punctuation / accents
        # --------------------------------------------------

        if "¿" in cleaned or "¡" in cleaned:
            return "es"

        if any(char in lowered for char in ["é", "è", "ê", "à", "ç", "ù"]):
            return "fr"

        # --------------------------------------------------
        # Library-based language detection
        # --------------------------------------------------

        try:
            from langdetect import DetectorFactory
            from langdetect import detect

            DetectorFactory.seed = 0

            detected = detect(cleaned)

            if detected == "tl":
                return "fil"

            # Important correction:
            # very short French messages are often misdetected as Portuguese.
            if detected == "pt":
                fallback = self._fallback_detect_language(cleaned)

                if fallback != "unknown":
                    return fallback

            supported = {
                "en",
                "fr",
                "es",
                "de",
                "it",
                "pt",
                "nl",
                "ru",
                "zh-cn",
                "zh-tw",
                "ja",
                "ko",
                "ar",
                "tl",
            }

            if detected in supported:
                return detected

            if detected.startswith("zh"):
                return "zh"

            return detected

        except Exception:
            return self._fallback_detect_language(cleaned)

    def _score_markers(
        self,
        text: str,
        markers: list[str],
    ) -> int:

        score = 0

        for marker in markers:
            if marker in text:
                score += 1

        return score
