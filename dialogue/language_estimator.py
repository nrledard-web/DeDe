"""
DeDe - Universal Language Estimator

Estimates the user's current language without relying on
language-specific lexical marker lists.

Principles:
- the current message is the primary signal;
- conversation continuity may stabilize ambiguous short messages;
- an explicit user language preference may stabilize ambiguity;
- Unicode script structure may strengthen detection;
- the estimator is not restricted to a predefined language list.

No vocabulary list is used to identify languages.
"""

from __future__ import annotations

from typing import Any
import unicodedata
from dialogue.semantic_language_resolver import (
    SemanticLanguageResolver,
)


class LanguageEstimator:

    name = "language_estimator"

    def __init__(
        self,
        llm_engine: Any | None = None,
    ) -> None:

        self.semantic_resolver = (
            SemanticLanguageResolver(
                llm_engine=llm_engine,
            )
        )

    def set_llm_engine(
        self,
        llm_engine: Any,
    ) -> None:

        self.semantic_resolver.set_llm_engine(
            llm_engine
        )
    

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
                detected_by_library=None,
            )

        # --------------------------------------------------
        # Universal statistical detection
        # --------------------------------------------------

        detections = self._langdetect_scores(
            cleaned
        )

        scores: dict[str, float] = {}

        for (
            language,
            probability,
        ) in detections.items():

            normalized_language = (
                self._normalize_code(
                    language
                )
            )

            if not normalized_language:
                continue

            scores[
                normalized_language
            ] = max(
                scores.get(
                    normalized_language,
                    0.0,
                ),
                probability,
            )

        detected_language = (
            max(
                scores,
                key=scores.get,
            )
            if scores
            else None
        )

        # --------------------------------------------------
        # Current-message strength
        # --------------------------------------------------

        word_count = len(
            cleaned.split()
        )

        character_count = len(
            cleaned
        )

        # --------------------------------------------------
        # Semantic resolution for short messages
        # --------------------------------------------------

        semantic_resolution = {}

        if word_count <= 5:

            semantic_resolution = (
                self.semantic_resolver.resolve(
                    cleaned
                )
            )

            semantic_language = str(
                semantic_resolution.get(
                    "language",
                    "",
                )
                or ""
            ).strip().lower()

            semantic_confidence = float(
                semantic_resolution.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            )

            if (
                semantic_language
                and semantic_language != "unknown"
                and semantic_confidence >= 0.60
            ):
                return self._result(
                    primary=semantic_language,
                    confidence=semantic_confidence,
                    scores={
                        semantic_language: (
                            semantic_confidence
                        )
                    },
                    source=(
                        "semantic_short_message_resolution"
                    ),
                    detected_by_library=(
                        detected_language
                    ),
                    script_profile=(
                        self._script_profile(
                            cleaned
                        )
                    ),
                )

        script_profile = (
            self._script_profile(
                cleaned
            )
        )

        strong_script_signal = bool(
            script_profile.get(
                "strong_non_latin_script",
                False,
            )
        )

        if detected_language:

            detector_probability = (
                scores.get(
                    detected_language,
                    0.0,
                )
            )

            # Current message remains dominant when it contains
            # enough linguistic material.
            if word_count >= 8:
                current_weight = 5.0

            elif word_count >= 5:
                current_weight = 3.0

            elif word_count >= 3:
                current_weight = 1.0

            else:
                current_weight = 0.5

            if character_count >= 20:
                current_weight += 1.0

            if strong_script_signal:
                current_weight += 1.5

            scores[
                detected_language
            ] = (
                detector_probability
                * current_weight
            )

        # --------------------------------------------------
        # Explicit user preference
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

        if preferred_language:

            preference_weight = (
                0.30
                if word_count >= 3
                else 0.70
            )

            scores[
                preferred_language
            ] = (
                scores.get(
                    preferred_language,
                    0.0,
                )
                + preference_weight
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

        if last_language:

            continuity_weight = (
                0.20
                if word_count >= 3
                else 0.60
            )

            scores[
                last_language
            ] = (
                scores.get(
                    last_language,
                    0.0,
                )
                + continuity_weight
            )

        # --------------------------------------------------
        # Script-supported detector reinforcement
        # --------------------------------------------------

        if (
            detected_language
            and strong_script_signal
        ):

            scores[
                detected_language
            ] = (
                scores.get(
                    detected_language,
                    0.0,
                )
                + 1.0
            )

        # --------------------------------------------------
        # No reliable signal
        # --------------------------------------------------

        active_scores = {
            language: score
            for language, score
            in scores.items()
            if score > 0.0
        }

        if not active_scores:

            fallback_language = (
                last_language
                or preferred_language
                or "unknown"
            )

            return self._result(
                primary=fallback_language,
                confidence=(
                    0.35
                    if fallback_language != "unknown"
                    else 0.0
                ),
                scores={},
                source="context_fallback",
                detected_by_library=None,
                script_profile=script_profile,
            )

        # --------------------------------------------------
        # Final ranking
        # --------------------------------------------------

        ranked = sorted(
            active_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        primary = ranked[0][0]

        top_score = ranked[0][1]

        second_score = (
            ranked[1][1]
            if len(ranked) > 1
            else 0.0
        )

        total_score = sum(
            active_scores.values()
        )

        proportional_confidence = (
            top_score / total_score
            if total_score > 0.0
            else 0.0
        )

        separation = max(
            0.0,
            top_score - second_score,
        )

        separation_bonus = min(
            0.20,
            separation * 0.05,
        )

        confidence = min(
            1.0,
            proportional_confidence
            + separation_bonus,
        )

        return self._result(
            primary=primary,
            confidence=round(
                confidence,
                3,
            ),
            scores=active_scores,
            source=(
                "universal_detector_with_"
                "contextual_stabilization"
            ),
            detected_by_library=(
                detected_language
            ),
            script_profile=script_profile,
        )

    # ======================================================
    # Statistical detector
    # ======================================================

    def _langdetect_scores(
        self,
        text: str,
    ) -> dict[str, float]:
        """
        Return probabilistic language candidates from langdetect.

        No language list is imposed by DeDe.
        """

        try:

            from langdetect import (
                DetectorFactory,
                detect_langs,
            )

            DetectorFactory.seed = 0

            detected_languages = (
                detect_langs(
                    text
                )
            )

            results: dict[
                str,
                float,
            ] = {}

            for candidate in (
                detected_languages[:5]
            ):

                language = (
                    self._normalize_code(
                        getattr(
                            candidate,
                            "lang",
                            None,
                        )
                    )
                )

                if not language:
                    continue

                try:
                    probability = float(
                        getattr(
                            candidate,
                            "prob",
                            0.0,
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    probability = 0.0

                results[
                    language
                ] = max(
                    results.get(
                        language,
                        0.0,
                    ),
                    probability,
                )

            return results

        except Exception:
            return {}

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

        # langdetect uses ISO 639 forms.
        # Normalize locale suffixes without restricting
        # which languages may be returned.

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

        # Tagalog and Filipino are treated as the same
        # dialogue language inside DeDe.

        if code == "tl":
            return "fil"

        # Chinese regional detector variants are normalized
        # to one dialogue code.

        if code.startswith(
            "zh"
        ):
            return "zh"

        return code

    # ======================================================
    # Unicode script profile
    # ======================================================

    def _script_profile(
        self,
        text: str,
    ) -> dict[str, Any]:
        """
        Observe writing-system structure without attempting
        to identify a language from vocabulary.

        Script information only strengthens statistical
        detection; it does not replace it.
        """

        profile = {
            "latin": 0,
            "cyrillic": 0,
            "arabic": 0,
            "hebrew": 0,
            "greek": 0,
            "devanagari": 0,
            "hiragana_katakana": 0,
            "hangul": 0,
            "han": 0,
            "other_letters": 0,
        }

        for character in text:

            if not character.isalpha():
                continue

            codepoint = ord(
                character
            )

            if (
                0x0041
                <= codepoint
                <= 0x024F
            ):
                profile[
                    "latin"
                ] += 1

            elif (
                0x0400
                <= codepoint
                <= 0x052F
            ):
                profile[
                    "cyrillic"
                ] += 1

            elif (
                0x0600
                <= codepoint
                <= 0x06FF
            ):
                profile[
                    "arabic"
                ] += 1

            elif (
                0x0590
                <= codepoint
                <= 0x05FF
            ):
                profile[
                    "hebrew"
                ] += 1

            elif (
                0x0370
                <= codepoint
                <= 0x03FF
            ):
                profile[
                    "greek"
                ] += 1

            elif (
                0x0900
                <= codepoint
                <= 0x097F
            ):
                profile[
                    "devanagari"
                ] += 1

            elif (
                0x3040
                <= codepoint
                <= 0x30FF
            ):
                profile[
                    "hiragana_katakana"
                ] += 1

            elif (
                0xAC00
                <= codepoint
                <= 0xD7AF
            ):
                profile[
                    "hangul"
                ] += 1

            elif (
                0x4E00
                <= codepoint
                <= 0x9FFF
            ):
                profile[
                    "han"
                ] += 1

            else:

                unicode_name = (
                    unicodedata.name(
                        character,
                        "",
                    )
                )

                if unicode_name:
                    profile[
                        "other_letters"
                    ] += 1

        non_latin_count = sum(
            value
            for key, value
            in profile.items()
            if key not in {
                "latin",
                "other_letters",
            }
        )

        profile[
            "strong_non_latin_script"
        ] = (
            non_latin_count >= 2
        )

        return profile

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
        script_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        ranked_scores = sorted(
            scores.items(),
            key=lambda item: item[1],
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

            "script_profile": (
                script_profile
                or {}
            ),

            "source": source,

            "universal_detection": True,

            "lexical_markers_used": False,

            "summary": (
                f"Language estimated as "
                f"'{primary}' with confidence "
                f"{round(confidence * 100)}%."
            ),
        }
