"""
DeDe - Language Estimator

Estimates the user's language using:
- strong markers
- conversation history
- user memory
- langdetect fallback

It returns a revisable language profile, not only a raw language code.
"""

from typing import Any


class LanguageEstimator:

    name = "language_estimator"

    def estimate(
        self,
        text: str,
        conversation_context: dict[str, Any] | None = None,
        user_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        conversation_context = conversation_context or {}
        user_memory = user_memory or {}

        cleaned = text.strip()

        if not cleaned:
            return self._result(
                primary="unknown",
                confidence=0.0,
                scores={},
                source="empty_text",
            )

        lowered = cleaned.lower()
        padded = f" {lowered} "

        scores = {
            "fr": 0.0,
            "en": 0.0,
            "es": 0.0,
            "fil": 0.0,
            "pt": 0.0,
        }

        # --------------------------------------------------
        # Strong markers
        # --------------------------------------------------

        marker_scores = self._marker_scores(padded)

        for language, score in marker_scores.items():
            scores[language] += score

        # --------------------------------------------------
        # Accents and punctuation
        # --------------------------------------------------

        if any(char in lowered for char in ["é", "è", "ê", "à", "ç", "ù"]):
            scores["fr"] += 3.0

        if "¿" in cleaned or "¡" in cleaned:
            scores["es"] += 3.0

        # --------------------------------------------------
        # Memory preference
        # --------------------------------------------------

        preferred_language = user_memory.get("preferred_language")

        if preferred_language in scores:
            scores[preferred_language] += 1.5

        # --------------------------------------------------
        # Conversation continuity
        # --------------------------------------------------

        last_language = conversation_context.get("last_language")

        if last_language in scores:
            scores[last_language] += 1.0

        # --------------------------------------------------
        # Langdetect as weak signal
        # --------------------------------------------------

        detected = self._langdetect(cleaned)

        if detected in scores:
            scores[detected] += 1.0

        if detected == "tl":
            scores["fil"] += 1.0

        # Portuguese correction:
        # short French sentences are often misread as Portuguese.
        if detected == "pt":
            if scores["fr"] >= 2.0:
                scores["pt"] -= 1.0
                scores["fr"] += 1.0

        # --------------------------------------------------
        # Decision
        # --------------------------------------------------

        primary = max(
            scores,
            key=scores.get,
        )

        total = sum(
            max(score, 0.0)
            for score in scores.values()
        )

        if total <= 0:
            return self._result(
                primary="unknown",
                confidence=0.0,
                scores=scores,
                source="no_signal",
            )

        confidence = round(
            max(scores[primary], 0.0) / total,
            3,
        )

        return self._result(
            primary=primary,
            confidence=confidence,
            scores=scores,
            source="markers_memory_context_langdetect",
            detected_by_library=detected,
        )

    def _marker_scores(
        self,
        padded: str,
    ) -> dict[str, float]:

        markers = {
            "fr": [
                " je ",
                " j'",
                " toi ",
                " tu ",
                " mon ",
                " ma ",
                " mes ",
                " nom ",
                " m'appelle ",
                " m appel ",
                " m'appel ",
                " nicolas ",
                " pas input ",
                " explique ",
                " bonjour ",
                " bonsoir ",
                " salut ",
                " pourquoi ",
                " comment ",
                " quoi ",
                " c'est ",
                " ça ",
                " mécroyance ",
            ],
            "en": [
                " what ",
                " what is ",
                " why ",
                " how ",
                " hello ",
                " hi ",
                " can you ",
                " explain ",
                " belief ",
                " understanding ",
                " certainty ",
            ],
            "es": [
                " hola ",
                " qué ",
                " que ",
                " por qué ",
                " cómo ",
                " buenos días ",
                " buenas tardes ",
                " buenas noches ",
                " gracias ",
                " explicame ",
                " explícame ",
            ],
            "fil": [
                " kumusta ",
                " kamusta ",
                " magandang ",
                " salamat ",
                " bakit ",
                " paano ",
                " ako ",
                " ikaw ",
                " tayo ",
                " paliwanag ",
            ],
            "pt": [
                " olá ",
                " obrigado ",
                " obrigada ",
                " porque ",
                " como ",
                " você ",
            ],
        }

        scores = {}

        for language, language_markers in markers.items():
            scores[language] = 0.0

            for marker in language_markers:
                if marker in padded:
                    scores[language] += 1.0

        return scores

    def _langdetect(
        self,
        text: str,
    ) -> str | None:

        try:
            from langdetect import DetectorFactory
            from langdetect import detect

            DetectorFactory.seed = 0

            detected = detect(text)

            if detected == "tl":
                return "fil"

            if detected.startswith("zh"):
                return "zh"

            return detected

        except Exception:
            return None

    def _result(
        self,
        primary: str,
        confidence: float,
        scores: dict[str, float],
        source: str,
        detected_by_library: str | None = None,
    ) -> dict[str, Any]:

        alternatives = {
            language: round(score, 3)
            for language, score in sorted(
                scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            if language != primary
        }

        return {
            "estimator": self.name,
            "status": "ready",
            "primary_language": primary,
            "confidence": confidence,
            "scores": {
                language: round(score, 3)
                for language, score in scores.items()
            },
            "alternatives": alternatives,
            "detected_by_library": detected_by_library,
            "source": source,
            "summary": (
                f"Language estimated as '{primary}' "
                f"with confidence {round(confidence * 100)}%."
            ),
        }
