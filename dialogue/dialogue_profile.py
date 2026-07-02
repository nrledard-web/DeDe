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

        # --------------------------------------------------
        # Strong shortcuts for very short messages
        # --------------------------------------------------

        lowered = cleaned.lower()
        padded = f" {lowered} "

        # --------------------------------------------------
        # Strong greeting shortcuts
        # --------------------------------------------------
        
        french_greetings = [
            "bonjour",
            "bonsoir",
            "salut",
            "coucou",
        ]
        
        english_greetings = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good evening",
        ]
        
        spanish_greetings = [
            "hola",
            "buenos días",
            "buenas tardes",
            "buenas noches",
        ]
        
        filipino_greetings = [
            "kumusta",
            "kamusta",
            "magandang araw",
            "magandang umaga",
            "magandang gabi",
        ]
        
        if any(greeting in lowered for greeting in french_greetings):
            return "fr"
        
        if any(greeting in lowered for greeting in english_greetings):
            return "en"
        
        if any(greeting in lowered for greeting in spanish_greetings):
            return "es"
        
        if any(greeting in lowered for greeting in filipino_greetings):
            return "fil"

        if "¿" in cleaned or "¡" in cleaned:
            return "es"

        if any(char in lowered for char in ["é", "è", "ê", "à", "ç", "ù"]):
            return "fr"

        if padded.startswith(" et ") or " et " in padded:
            return "fr"

        if padded.startswith(" and ") or " and " in padded:
            return "en"

        if padded.startswith(" y ") or " y " in padded:
            return "es"

        # --------------------------------------------------
        # Library-based language detection
        # --------------------------------------------------

        try:
            from langdetect import DetectorFactory
            from langdetect import detect

            DetectorFactory.seed = 0

            detected = detect(cleaned)

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

            if detected == "tl":
                return "fil"
            
            if detected in supported:
                return detected

            if detected.startswith("zh"):
                return "zh"

            return detected

        except Exception:
            return self._fallback_detect_language(cleaned)

    def _fallback_detect_language(
        self,
        text: str,
    ) -> str:

        lowered = text.lower()
        padded = f" {lowered} "

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
            " et ",
            " en ",
            " religion ",
            " science ",
            " politique ",
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
            " the ",
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
            " con ",
            " y ",
            " es ",
        ]

        scores = {
            "fr": self._score_markers(padded, french_markers),
            "en": self._score_markers(padded, english_markers),
            "es": self._score_markers(padded, spanish_markers),
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

        score = 0

        for marker in markers:
            if marker in text:
                score += 1

        return score
