"""
DeDe - User Memory

Minimal session-level user memory.

This is not long-term storage yet.
It prepares persistent cognitive memory.
"""

from typing import Any
import re


class UserMemory:

    name = "user_memory"

    def __init__(self) -> None:
        self.data: dict[str, Any] = {
            "preferred_name": None,
            "known_facts": [],
            "interaction_notes": [],
        }

    def update_from_text(
        self,
        text: str | None,
    ) -> dict[str, Any]:

        if not text:
            return self.data

        lowered = text.lower()

        # --------------------------------------------------
        # User name extraction
        # --------------------------------------------------

        name = self._extract_preferred_name(text)

        if name:
            self.data["preferred_name"] = name

            self._add_note(
                f"The user identified themselves as {name}."
            )

        # --------------------------------------------------
        # User rejects being reduced to an input
        # --------------------------------------------------

        if "input" in lowered:
            self._add_note(
                "The user rejects being reduced to an input-like label."
            )

        return self.data

    def get_memory(self) -> dict[str, Any]:
        return self.data

    def _extract_preferred_name(
        self,
        text: str,
    ) -> str | None:

        patterns = [

            # French
            r"\bje suis\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bje m[' ]appelle\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bje m[' ]appel\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bje me nomme\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bje me pr[ée]nomme\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bmon nom est\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bmoi c[' ]est\s+([A-Za-zÀ-ÿ\-']+)",

            # English
            r"\bi am\s+([A-Za-z\-']+)",
            r"\bmy name is\s+([A-Za-z\-']+)",

            # Spanish
            r"\bme llamo\s+([A-Za-zÀ-ÿ\-']+)",
            r"\bmi nombre es\s+([A-Za-zÀ-ÿ\-']+)",

            # Filipino
            r"\bako si\s+([A-Za-z\-']+)",
            r"\bpangalan ko ay\s+([A-Za-z\-']+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:

                name = match.group(1).strip()

                return (
                    name[:1].upper()
                    + name[1:]
                )

        return None

    def _add_note(
        self,
        note: str,
    ) -> None:

        if note not in self.data["interaction_notes"]:
            self.data["interaction_notes"].append(note)
