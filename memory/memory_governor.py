"""
DeDe - Memory Governor

Decides what should or should not enter persistent memory.
"""

from typing import Any


class MemoryGovernor:

    name = "memory_governor"

    def evaluate(
        self,
        text: str,
    ) -> dict[str, Any]:

        lowered = text.lower()

        if any(
            marker in lowered
            for marker in [
                "don't save",
                "do not save",
                "ne sauvegarde pas",
                "ne mémorise pas",
                "pas en mémoire",
                "pas dans la mémoire",
            ]
        ):
            return {
                "governor": self.name,
                "status": "ready",
                "allow_persistent_storage": False,
                "reason": "User explicitly requested not to store this permanently.",
            }

        if any(
            marker in lowered
            for marker in [
                "je m'appelle",
                "je m'appel",
                "je me nomme",
                "mon nom est",
                "moi c'est",
                "my name is",
                "i am",
                "me llamo",
                "ako si",
            ]
        ):
            return {
                "governor": self.name,
                "status": "ready",
                "allow_persistent_storage": True,
                "reason": "Identity or continuity information.",
            }

        return {
            "governor": self.name,
            "status": "ready",
            "allow_persistent_storage": True,
            "reason": "No restriction detected.",
        }
