"""
DeDe - Universal Language Estimator

Estimates the user's language using:

- universal language detection
- conversation continuity
- user language preference
- limited lexical corrections for known ambiguous cases

Important principle:

Language-specific markers are NOT the primary detection system.

They are only local correction signals.

The estimator can therefore return any language supported by
the underlying detection library rather than being restricted
to a fixed list of languages.
"""

from __future__ import annotations

from typing import Any


class LanguageEstimator:

    name = "language_estimator"

    # ======================================================
    # Public API
    # ======================================================

    def estimate(
        self,
        text: str,
        conversation_context: dict[str, Any] | None = None,
        user_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        conversation_context = (
            conversation_context
            or {}
        )

        user_memory = (
            user_memory
            or {}
        )

        cleaned = str(
            text
            or ""
        ).strip()

        if not cleaned:

            return self._result(
                primary="unknown",
                confidence=0.0,
                scores={},
                source="empty_text",
            )

        # --------------------------------------------------
        # Universal detector
        # --------------------------------------------------

        detected = self._langdetect(
            cleaned
        )

        # --------------------------------------------------
        # Dynamic score map
        # --------------------------------------------------
        #
        # Unlike the previous estimator, languages are not
        # restricted to a fixed dictionary.
        # --------------------------------------------------

        scores: dict[str, float] = {}

        def ensure_language(
            language: str | None,
        ) -> None:

            if not language:
                return

            language = self._normalize_code(
                language
            )

            if (
                language
                and language != "unknown"
                and language not in scores
            ):
                scores[language] = 0.0

        ensure_language(
            detected
        )

        # --------------------------------------------------
        # User preference
        # --------------------------------------------------

        preferred_language = (
            user_memory.get(
                "preferred_language"
            )
        )

        preferred_language = (
            self._normalize_code(
                preferred_language
            )
        )

        ensure_language(
            preferred_language
        )

        # --------------------------------------------------
        # Conversation continuity
        # --------------------------------------------------

        last_language = (
            conversation_context.get(
                "last_language"
            )
        )

        last_language = (
            self._normalize_code(
                last_language
            )
        )

        ensure_language(
            last_language
        )

        # --------------------------------------------------
        # Known correction languages
        # --------------------------------------------------

        correction_languages = {
            "fr",
            "en",
            "es",
            "fil",
            "pt",
        }

        for language in correction_languages:
            ensure_language(
                language
            )

        # --------------------------------------------------
        # Universal detector score
        # --------------------------------------------------
        #
        # The language detected from the CURRENT message
        # must remain the dominant signal.
        #
        # Conversation history and memory may stabilize
        # ambiguous messages, but must not prevent the user
        # from switching languages between turns.
        # --------------------------------------------------
        
        if detected:
        
            detected = self._normalize_code(
                detected
            )
        
            ensure_language(
                detected
            )
        
            word_count = len(
                cleaned.split()
            )
        
            # Stronger current-message priority once enough
            # linguistic material is available.
            if word_count >= 4:
                detector_weight = 7.0
        
            elif word_count >= 2:
                detector_weight = 5.0
        
            else:
                detector_weight = 3.0
        
            scores[detected] += (
                detector_weight
            )

        # --------------------------------------------------
        # Limited lexical corrections
        # --------------------------------------------------

        marker_scores = (
            self._marker_scores(
                cleaned
            )
        )

        for language, marker_score in (
            marker_scores.items()
        ):

            ensure_language(
                language
            )

            scores[language] += (
                marker_score
            )

        # --------------------------------------------------
        # Script and punctuation corrections
        # --------------------------------------------------

        script_scores = (
            self._script_scores(
                cleaned
            )
        )

        for language, script_score in (
            script_scores.items()
        ):

            ensure_language(
                language
            )

            scores[language] += (
                script_score
            )

        # --------------------------------------------------
        # Memory preference
        # --------------------------------------------------
        #
        # Preference helps stabilize ambiguous short messages.
        # It must not dominate strong evidence from the
        # current message.
        # --------------------------------------------------

        if (
            preferred_language
            and preferred_language in scores
        ):
            scores[
                preferred_language
            ] += 0.75

        # --------------------------------------------------
        # Conversation continuity
        # --------------------------------------------------

        if (
            last_language
            and last_language in scores
        ):
            scores[
                last_language
            ] += 0.50

        # --------------------------------------------------
        # Known ambiguity correction
        # --------------------------------------------------
        #
        # langdetect sometimes identifies short French text
        # as Portuguese.
        # --------------------------------------------------

        if detected == "pt":

            french_signal = scores.get(
                "fr",
                0.0,
            )

            portuguese_signal = (
                marker_scores.get(
                    "pt",
                    0.0,
                )
            )

            if (
                french_signal >= 2.0
                and portuguese_signal <= 1.0
            ):

                scores["pt"] = max(
                    0.0,
                    scores.get(
                        "pt",
                        0.0,
                    )
                    - 2.0,
                )

                scores["fr"] = (
                    scores.get(
                        "fr",
                        0.0,
                    )
                    + 2.0
                )

        # --------------------------------------------------
        # Remove completely unsupported zero-score entries
        # --------------------------------------------------

        active_scores = {
            language: score
            for language, score
            in scores.items()
            if score > 0.0
        }

        if not active_scores:

            return self._result(
                primary="unknown",
                confidence=0.0,
                scores=scores,
                source=(
                    "no_reliable_language_signal"
                ),
                detected_by_library=(
                    detected
                ),
            )

        # --------------------------------------------------
        # Decision
        # --------------------------------------------------

        ranked = sorted(
            active_scores.items(),
            key=lambda item: (
                item[1]
            ),
            reverse=True,
        )

        primary = ranked[0][0]

        top_score = ranked[0][1]

        second_score = (
            ranked[1][1]
            if len(ranked) > 1
            else 0.0
        )

        total = sum(
            active_scores.values()
        )

        raw_confidence = (
            top_score / total
            if total > 0.0
            else 0.0
        )

        # --------------------------------------------------
        # Separation confidence
        # --------------------------------------------------
        #
        # A clear gap between first and second candidate
        # increases confidence.
        # --------------------------------------------------

        separation = (
            top_score
            - second_score
        )

        separation_bonus = min(
            0.20,
            separation * 0.04,
        )

        confidence = min(
            1.0,
            raw_confidence
            + separation_bonus,
        )

        return self._result(
            primary=primary,
            confidence=round(
                confidence,
                3,
            ),
            scores=scores,
            source=(
                "universal_detector_with_"
                "contextual_corrections"
            ),
            detected_by_library=(
                detected
            ),
        )

    # ======================================================
    # Universal detector
    # ======================================================

    def _langdetect(
        self,
        text: str,
    ) -> str | None:

        try:

            from langdetect import (
                DetectorFactory,
                detect,
            )

            DetectorFactory.seed = 0

            detected = detect(
                text
            )

            return self._normalize_code(
                detected
            )

        except Exception:

            return None

    # ======================================================
    # Language code normalization
    # ======================================================

    @staticmethod
    def _normalize_code(
        language: Any,
    ) -> str | None:

        if language is None:
            return None

        code = str(
            language
        ).strip().lower()

        if not code:
            return None

        # Tagalog returned by langdetect
        if code == "tl":
            return "fil"

        # Chinese variants
        if code.startswith(
            "zh"
        ):
            return "zh"

        # Common locale forms
        if "-" in code:
            code = code.split(
                "-",
                1,
            )[0]

        if "_" in code:
            code = code.split(
                "_",
                1,
            )[0]

        return code

    # ======================================================
    # Local lexical corrections
    # ======================================================
    #
    # These markers are deliberately limited.
    #
    # They do NOT define which languages DeDe supports.
    #
    # They only help resolve known ambiguity for a few
    # frequently used languages.
    # ======================================================

    def _marker_scores(
        self,
        text: str,
    ) -> dict[str, float]:

        lowered = (
            str(
                text
            )
            .lower()
            .strip()
        )

        padded = (
            f" {lowered} "
        )

        markers = {

            "fr": [
                " je ",
                " j'",
                " toi ",
                " tu ",
                " mon ",
                " ma ",
                " mes ",
                " m'appelle ",
                " bonjour ",
                " bonsoir ",
                " salut ",
                " pourquoi ",
                " comment ",
                " c'est ",
                " ça ",
                " mécroyance ",
            ],

            "en": [
                " what ",
                " why ",
                " how ",
                " hello ",
                " hi ",
                " can you ",
                " explain ",
                " understanding ",
                " certainty ",
            ],

            "es": [
                " hola ",
                " qué ",
                " por qué ",
                " cómo ",
                " buenos días ",
                " buenas tardes ",
                " buenas noches ",
                " gracias ",
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
            ],

            "pt": [
                " olá ",
                " obrigado ",
                " obrigada ",
                " você ",
                " vocês ",
            ],
        }

        scores: dict[
            str,
            float,
        ] = {}

        for (
            language,
            language_markers,
        ) in markers.items():

            score = 0.0

            for marker in (
                language_markers
            ):

                if marker in padded:
                    score += 1.0

            scores[
                language
            ] = score

        return scores

    # ======================================================
    # Script detection
    # ======================================================
    #
    # Script signals are structural and therefore useful for
    # languages that use distinct writing systems.
    #
    # They do not attempt complete linguistic recognition.
    # ======================================================

    def _script_scores(
        self,
        text: str,
    ) -> dict[str, float]:

        scores: dict[
            str,
            float,
        ] = {}

        # --------------------------------------------------
        # Cyrillic
        # --------------------------------------------------

        cyrillic_count = sum(
            1
            for char in text
            if (
                "\u0400"
                <= char
                <= "\u04FF"
            )
        )

        if cyrillic_count >= 2:

            # Do not force Russian if langdetect already
            # identifies another Cyrillic language.
            detected = self._langdetect(
                text
            )

            if detected:
                scores[
                    detected
                ] = 2.0
            else:
                scores[
                    "ru"
                ] = 1.5

        # --------------------------------------------------
        # Arabic script
        # --------------------------------------------------

        arabic_count = sum(
            1
            for char in text
            if (
                "\u0600"
                <= char
                <= "\u06FF"
            )
        )

        if arabic_count >= 2:

            detected = self._langdetect(
                text
            )

            if detected:
                scores[
                    detected
                ] = max(
                    scores.get(
                        detected,
                        0.0,
                    ),
                    2.0,
                )

        # --------------------------------------------------
        # Japanese Hiragana / Katakana
        # --------------------------------------------------

        japanese_count = sum(
            1
            for char in text
            if (
                "\u3040"
                <= char
                <= "\u30FF"
            )
        )

        if japanese_count >= 2:

            scores[
                "ja"
            ] = 3.0

        # --------------------------------------------------
        # Hangul
        # --------------------------------------------------

        korean_count = sum(
            1
            for char in text
            if (
                "\uAC00"
                <= char
                <= "\uD7AF"
            )
        )

        if korean_count >= 2:

            scores[
                "ko"
            ] = 3.0

        # --------------------------------------------------
        # Chinese Han characters
        # --------------------------------------------------

        han_count = sum(
            1
            for char in text
            if (
                "\u4E00"
                <= char
                <= "\u9FFF"
            )
        )

        if (
            han_count >= 2
            and japanese_count == 0
        ):

            detected = self._langdetect(
                text
            )

            if detected:

                detected = (
                    self._normalize_code(
                        detected
                    )
                )

                scores[
                    detected
                ] = max(
                    scores.get(
                        detected,
                        0.0,
                    ),
                    2.5,
                )

            else:

                scores[
                    "zh"
                ] = 2.0

        return scores

    # ======================================================
    # Result
    # ======================================================

    def _result(
        self,
        primary: str,
        confidence: float,
        scores: dict[str, float],
        source: str,
        detected_by_library: str | None = None,
    ) -> dict[str, Any]:

        ranked_scores = sorted(
            scores.items(),
            key=lambda item: (
                item[1]
            ),
            reverse=True,
        )

        alternatives = {
            language: round(
                score,
                3,
            )
            for (
                language,
                score,
            ) in ranked_scores
            if (
                language != primary
                and score > 0.0
            )
        }

        return {
            "estimator": self.name,
            "status": "ready",

            "primary_language": (
                primary
            ),

            "confidence": round(
                confidence,
                3,
            ),

            "scores": {
                language: round(
                    score,
                    3,
                )
                for (
                    language,
                    score,
                ) in scores.items()
                if score > 0.0
            },

            "alternatives": (
                alternatives
            ),

            "detected_by_library": (
                detected_by_library
            ),

            "source": source,

            "universal_detection": True,

            "summary": (
                f"Language estimated as "
                f"'{primary}' with confidence "
                f"{round(confidence * 100)}%."
            ),
        }
