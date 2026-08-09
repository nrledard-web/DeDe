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
        user_id: str = "default_user",
        base_path: str = "data/users",
    ) -> None:
    
        safe_user_id = "".join(
            char for char in user_id
            if char.isalnum() or char in ["_", "-"]
        ) or "default_user"
    
        self.user_id = safe_user_id
    
        self.path = Path(base_path) / safe_user_id / "user_memory.json"
    
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
            "memory_items": [],
            "conversation_count": 0,
            "last_seen": None,
            "created_at": self._now(),
            "autobiography": {},
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

    def store_candidate(
        self,
        candidate: dict[str, Any],
        storage_scope: str,
    ) -> dict[str, Any]:
        """
        Store one structured durable-memory candidate.
        """
    
        if not isinstance(candidate, dict):
            return self.data
    
        content = str(
            candidate.get(
                "content",
                "",
            )
        ).strip()
    
        if not content:
            return self.data
    
        memory_type = str(
            candidate.get(
                "memory_type",
                "unknown",
            )
        ).strip().lower()
    
        sensitivity = str(
            candidate.get(
                "sensitivity",
                "medium",
            )
        ).strip().lower()
    
        source = str(
            candidate.get(
                "source",
                "conversation",
            )
        ).strip().lower()
    
        project = candidate.get(
            "project"
        )
    
        try:
            confidence = float(
                candidate.get(
                    "confidence",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            confidence = 0.0
    
        confidence = max(
            0.0,
            min(confidence, 1.0),
        )
    
        normalized_content = (
            content.lower().strip()
        )
    
        memory_items = self.data.setdefault(
            "memory_items",
            [],
        )
    
        for memory_item in memory_items:
            existing_content = str(
                memory_item.get(
                    "content",
                    "",
                )
            ).lower().strip()
    
            existing_type = str(
                memory_item.get(
                    "memory_type",
                    "",
                )
            ).lower().strip()
    
            if (
                existing_content == normalized_content
                and existing_type == memory_type
            ):
                memory_item.update(
                    {
                        "content": content,
                        "storage_scope": storage_scope,
                        "sensitivity": sensitivity,
                        "confidence": confidence,
                        "source": source,
                        "project": project,
                        "updated_at": self._now(),
                    }
                )
    
                self.data["last_seen"] = self._now()
                self.save()
    
                return self.data
    
        created_at = self._now()
    
        memory_items.append(
            {
                "memory_id": (
                    f"memory_{len(memory_items) + 1}"
                ),
                "content": content,
                "memory_type": memory_type,
                "storage_scope": storage_scope,
                "sensitivity": sensitivity,
                "confidence": confidence,
                "source": source,
                "project": project,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
    
        self.data["last_seen"] = created_at
        self.save()
    
        return self.data

    def restore_memory(
        self,
        memory_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Restore validated portable memory for the current owner.
    
        The technical owner ID remains controlled by the
        current DeDe installation.
        """
    
        if not isinstance(
            memory_data,
            dict,
        ):
            raise ValueError(
                "Imported memory data is invalid."
            )
    
        restored_memory = (
            self._default_memory()
        )
    
        allowed_keys = set(
            restored_memory.keys()
        )
    
        allowed_keys.add(
            "owner"
        )
    
        for key, value in memory_data.items():
            if key in allowed_keys:
                restored_memory[key] = value
    
        for list_key in [
            "known_people",
            "known_facts",
            "interaction_notes",
            "memory_items",
        ]:
            if not isinstance(
                restored_memory.get(
                    list_key
                ),
                list,
            ):
                restored_memory[list_key] = []
    
        if not isinstance(
            restored_memory.get(
                "autobiography"
            ),
            dict,
        ):
            restored_memory[
                "autobiography"
            ] = {}
    
        owner = restored_memory.get(
            "owner",
            {},
        )
    
        if not isinstance(
            owner,
            dict,
        ):
            owner = {}
    
        owner["id"] = self.user_id
    
        if not owner.get(
            "preferred_name"
        ):
            owner["preferred_name"] = (
                restored_memory.get(
                    "preferred_name"
                )
            )
    
        restored_memory[
            "owner"
        ] = owner
    
        restored_memory[
            "last_seen"
        ] = self._now()
    
        self.data = restored_memory
        self.save()

        return self.data

    def clear_memory(
        self,
    ) -> dict[str, Any]:
        """
        Permanently clear durable memory for this owner.
        """

        self.data = self._default_memory()

        self.data["last_seen"] = self._now()

        self.save()

        return self.data

    def increment_conversation_count(
        self,
    ) -> dict[str, Any]:

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
