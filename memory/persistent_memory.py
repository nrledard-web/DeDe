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
            "assistant_identity": {
                "preferred_name": None,
                "selection_origin": None,
                "selection_reason": None,
                "confirmed_by_user": False,
                "updated_at": None,
            },
            "known_people": [],
            "known_facts": [],
            "interaction_notes": [],
            "memory_items": [],
            "memory_folders": [],
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
    
        existing_ids = {
            str(
                item.get(
                    "memory_id",
                    "",
                )
            ).strip()
            for item in memory_items
            if isinstance(
                item,
                dict,
            )
        }
        
        memory_number = 1
        
        while (
            f"memory_{memory_number}"
            in existing_ids
        ):
            memory_number += 1
        
        created_at = self._now()
        
        memory_items.append(
            {
                "memory_id": (
                    f"memory_{memory_number}"
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
            "memory_folders",
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

    def create_memory_folder(
        self,
        folder_name: str,
    ) -> dict[str, Any]:
        """
        Create one user-defined memory folder.
        """

        cleaned_name = str(
            folder_name or ""
        ).strip()

        if not cleaned_name:
            return {
                "status": "invalid_name",
                "created": False,
                "error": (
                    "The folder name is empty."
                ),
            }

        memory_folders = self.data.setdefault(
            "memory_folders",
            [],
        )

        if not isinstance(
            memory_folders,
            list,
        ):
            memory_folders = []

            self.data[
                "memory_folders"
            ] = memory_folders

        normalized_name = (
            cleaned_name.casefold()
        )

        for folder in memory_folders:
            if not isinstance(
                folder,
                dict,
            ):
                continue

            existing_name = str(
                folder.get(
                    "name",
                    "",
                )
            ).strip().casefold()

            if (
                existing_name
                == normalized_name
            ):
                return {
                    "status": "already_exists",
                    "created": False,
                    "error": (
                        "A memory folder with this "
                        "name already exists."
                    ),
                    "folder": folder,
                }

        existing_ids = {
            str(
                folder.get(
                    "folder_id",
                    "",
                )
            ).strip()
            for folder in memory_folders
            if isinstance(
                folder,
                dict,
            )
        }

        folder_number = 1

        while (
            f"folder_{folder_number}"
            in existing_ids
        ):
            folder_number += 1

        created_at = self._now()

        new_folder = {
            "folder_id": (
                f"folder_{folder_number}"
            ),
            "name": cleaned_name,
            "created_at": created_at,
            "updated_at": created_at,
        }

        memory_folders.append(
            new_folder
        )

        self.data["last_seen"] = (
            created_at
        )

        self.save()

        return {
            "status": "success",
            "created": True,
            "folder": new_folder,
        }

    def delete_memory_folder(
        self,
        folder_id: str,
    ) -> dict[str, Any]:
        """
        Delete a user-defined folder without deleting
        the memories that it contained.
        """

        cleaned_folder_id = str(
            folder_id or ""
        ).strip()

        memory_folders = self.data.get(
            "memory_folders",
            [],
        )

        if not isinstance(
            memory_folders,
            list,
        ):
            memory_folders = []

        remaining_folders = []
        deleted_folder = None

        for folder in memory_folders:
            if not isinstance(
                folder,
                dict,
            ):
                continue

            if (
                deleted_folder is None
                and str(
                    folder.get(
                        "folder_id",
                        "",
                    )
                ).strip()
                == cleaned_folder_id
            ):
                deleted_folder = folder
                continue

            remaining_folders.append(
                folder
            )

        if deleted_folder is None:
            return {
                "status": "not_found",
                "deleted": False,
                "folder_id": (
                    cleaned_folder_id
                ),
            }

        memory_items = self.data.get(
            "memory_items",
            [],
        )

        moved_item_count = 0

        if isinstance(
            memory_items,
            list,
        ):
            for memory_item in memory_items:
                if not isinstance(
                    memory_item,
                    dict,
                ):
                    continue

                if str(
                    memory_item.get(
                        "folder_id",
                        "",
                    )
                    or ""
                ).strip() == cleaned_folder_id:
                    memory_item[
                        "folder_id"
                    ] = None

                    memory_item[
                        "updated_at"
                    ] = self._now()

                    moved_item_count += 1

        self.data[
            "memory_folders"
        ] = remaining_folders

        self.data["last_seen"] = (
            self._now()
        )

        self.save()

        return {
            "status": "success",
            "deleted": True,
            "folder_id": cleaned_folder_id,
            "deleted_folder": deleted_folder,
            "moved_item_count": (
                moved_item_count
            ),
        }

    def move_memory_item(
        self,
        memory_id: str,
        folder_id: str | None,
    ) -> dict[str, Any]:
        """
        Move one durable memory into a user-defined
        folder or back to its automatic folder.
        """

        cleaned_memory_id = str(
            memory_id or ""
        ).strip()

        cleaned_folder_id = str(
            folder_id or ""
        ).strip() or None

        if cleaned_folder_id is not None:
            memory_folders = self.data.get(
                "memory_folders",
                [],
            )

            valid_folder_ids = {
                str(
                    folder.get(
                        "folder_id",
                        "",
                    )
                ).strip()
                for folder in memory_folders
                if isinstance(
                    folder,
                    dict,
                )
            }

            if (
                cleaned_folder_id
                not in valid_folder_ids
            ):
                return {
                    "status": "folder_not_found",
                    "moved": False,
                    "memory_id": (
                        cleaned_memory_id
                    ),
                    "folder_id": (
                        cleaned_folder_id
                    ),
                }

        memory_items = self.data.get(
            "memory_items",
            [],
        )

        if not isinstance(
            memory_items,
            list,
        ):
            memory_items = []

        for memory_item in memory_items:
            if not isinstance(
                memory_item,
                dict,
            ):
                continue

            current_memory_id = str(
                memory_item.get(
                    "memory_id",
                    "",
                )
            ).strip()

            if (
                current_memory_id
                != cleaned_memory_id
            ):
                continue

            memory_item[
                "folder_id"
            ] = cleaned_folder_id

            memory_item[
                "updated_at"
            ] = self._now()

            self.data["last_seen"] = (
                self._now()
            )

            self.save()

            return {
                "status": "success",
                "moved": True,
                "memory_id": (
                    cleaned_memory_id
                ),
                "folder_id": (
                    cleaned_folder_id
                ),
            }

        return {
            "status": "not_found",
            "moved": False,
            "memory_id": cleaned_memory_id,
            "folder_id": cleaned_folder_id,
        }

    def delete_memory_item(
        self,
        memory_id: str,
    ) -> dict[str, Any]:
        """
        Delete one durable memory item by its identifier.
        """

        cleaned_memory_id = str(
            memory_id or ""
        ).strip()

        memory_items = self.data.get(
            "memory_items",
            [],
        )

        if (
            not cleaned_memory_id
            or not isinstance(
                memory_items,
                list,
            )
        ):
            return {
                "status": "not_found",
                "deleted": False,
                "memory_id": cleaned_memory_id,
            }

        remaining_items = []
        deleted_item = None

        for item in memory_items:
            if not isinstance(
                item,
                dict,
            ):
                continue

            if (
                deleted_item is None
                and str(
                    item.get(
                        "memory_id",
                        "",
                    )
                ).strip()
                == cleaned_memory_id
            ):
                deleted_item = item
                continue

            remaining_items.append(
                item
            )

        if deleted_item is None:
            return {
                "status": "not_found",
                "deleted": False,
                "memory_id": cleaned_memory_id,
            }

        self.data[
            "memory_items"
        ] = remaining_items

        self.data[
            "last_seen"
        ] = self._now()

        self.save()

        return {
            "status": "success",
            "deleted": True,
            "memory_id": cleaned_memory_id,
            "deleted_item": deleted_item,
        }


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
