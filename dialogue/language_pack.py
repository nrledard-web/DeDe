"""
DeDe - Language Pack

Loads user-facing dialogue phrases from language modules.
"""

from typing import Any
from importlib import import_module


class LanguagePack:

    name = "language_pack"

    FALLBACK_LANGUAGE = "en"

    LANGUAGE_ALIASES = {
        "tl": "fil",
        "tagalog": "fil",
        "filipino": "fil",
        "zh-cn": "zh",
        "zh-tw": "zh",
    }

    def get(
        self,
        language: str,
        key: str,
        **kwargs: Any,
    ) -> str:

        language = self._normalize_language(language)

        phrases = self._load_phrases(language)

        if key not in phrases:
            phrases = self._load_phrases(
                self.FALLBACK_LANGUAGE,
            )

        template = phrases.get(key, "")

        try:
            return template.format(**kwargs)
        except Exception:
            return template

    def _normalize_language(
        self,
        language: str | None,
    ) -> str:

        if not language:
            return self.FALLBACK_LANGUAGE

        language = language.lower().strip()

        return self.LANGUAGE_ALIASES.get(
            language,
            language,
        )

    def _load_phrases(
        self,
        language: str,
    ) -> dict[str, str]:

        try:
            module = import_module(
                f"dialogue.languages.{language}"
            )

            return getattr(module, "PHRASES", {})

        except Exception:
            module = import_module(
                f"dialogue.languages.{self.FALLBACK_LANGUAGE}"
            )

            return getattr(module, "PHRASES", {})
