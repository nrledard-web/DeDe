"""
DeDe - User Memory

Minimal session-level user memory.

This is not long-term storage yet.
It prepares persistent cognitive memory.
"""

from typing import Any


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

        if "mon nom est nicolas" in lowered:
            self.data["preferred_name"] = "Nicolas"
            self._add_note(
                "The user explicitly corrected DeDe: his name is Nicolas, not input."
            )

        if "je m'appelle nicolas" in lowered or "je me nomme nicolas" in lowered:
            self.data["preferred_name"] = "Nicolas"
            self._add_note(
                "The user identified himself as Nicolas."
            )

        if "pas input" in lowered:
            self._add_note(
                "The user rejects being reduced to the label 'input'."
            )

        return self.data

    def get_memory(self) -> dict[str, Any]:
        return self.data

    def _add_note(
        self,
        note: str,
    ) -> None:

        if note not in self.data["interaction_notes"]:
            self.data["interaction_notes"].append(note)
