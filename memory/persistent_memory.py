"""
DeDe - Persistent Memory

Simple JSON-based persistent memory.

This first version stores user-level continuity across reboots.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


class PersistentMemory:

    name = "persistent_memory"

    def __init__(
        self,
        path: str = "data/user_memory.json",
    ) -> None:

        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.data = self._load()

    def _default_memory(self) -> dict[str, Any]:

        return {
            "preferred_name": None,
            "preferred_language": None,
            "known_people": [],
            "known_facts": [],
            "interaction_notes": [],
            "conversation_count": 0,
            "last_seen": None,
            "created_at": self._now(),
        }

    def _load(self) -> dict[str, Any]:

        if not self.path.exists():
            return self._default_memory()

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                loaded = json.load(file)

            default = self._default_memory()
            default.update(loaded)

            return default

        except Exception:
            return self._default_memory()

    def save(self) -> None:

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def merge_user_memory(
        self,
        user_memory: dict[str, Any],
    ) -> dict[str, Any]:

        name = user_memory.get("preferred_name")

        if name:
            self.data["preferred_name"] = name

        for key in [
            "known_facts",
            "interaction_notes",
        ]:
            for item in user_memory.get(key, []):
                if item not in self.data[key]:
                    self.data[key].append(item)

        self.data["last_seen"] = self._now()
        self.save()

        return self.data

    def increment_conversation_count(self) -> dict[str, Any]:

        self.data["conversation_count"] = (
            self.data.get("conversation_count", 0) + 1
        )

        self.data["last_seen"] = self._now()
        self.save()

        return self.data

    def get_memory(self) -> dict[str, Any]:

        return self.data

    def _now(self) -> str:

        return datetime.now(
            timezone.utc,
        ).isoformat()
