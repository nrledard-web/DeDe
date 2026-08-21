from __future__ import annotations

import json
import shutil
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ImageMemory:

    name = "image_memory"

    def __init__(
        self,
        user_id: str,
        base_path: str = "data/users",
    ) -> None:

        safe_user_id = (
            str(user_id or "default")
            .strip()
            .lower()
        )

        self.user_dir = (
            Path(base_path)
            / safe_user_id
        )

        self.images_dir = (
            self.user_dir
            / "images"
        )

        self.index_path = (
            self.user_dir
            / "image_memory.json"
        )

        self.images_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._ensure_index()


    def _ensure_index(self) -> None:

        if self.index_path.exists():
            return

        data = {
            "version": 1,
            "images": [],
        }

        self._write_index(
            data
        )


    def _read_index(self) -> dict[str, Any]:

        try:

            with self.index_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(
                    file
                )

        except Exception:

            data = {
                "version": 1,
                "images": [],
            }

        if not isinstance(
            data,
            dict,
        ):
            data = {
                "version": 1,
                "images": [],
            }

        images = data.get(
            "images",
            [],
        )

        if not isinstance(
            images,
            list,
        ):
            images = []

        data["images"] = images

        return data


    def _write_index(
        self,
        data: dict[str, Any],
    ) -> None:

        self.user_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.index_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )


    def save_image(
        self,
        image_bytes: bytes,
        original_name: str = "",
        mime_type: str = "image/jpeg",
        description: str = "",
        label: str = "",
        usage: list[str] | None = None,
        folder_id: str | None = None,
    ) -> dict[str, Any]:

        if not image_bytes:

            return {
                "status": "error",
                "error": "No image data provided.",
            }

        extension = self._extension_from_mime(
            mime_type
        )

        image_id = (
            "img_"
            + uuid.uuid4().hex[:12]
        )

        file_name = (
            f"{image_id}.{extension}"
        )

        file_path = (
            self.images_dir
            / file_name
        )

        file_path.write_bytes(
            image_bytes
        )

        created_at = (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )

        item = {
            "image_id": image_id,
            "label": (
                str(label or "").strip()
            ),
            "original_name": (
                str(original_name or "").strip()
            ),
            "file_name": file_name,
            "relative_path": (
                str(
                    Path("images")
                    / file_name
                )
            ),
            "mime_type": mime_type,
            "description": (
                str(description or "").strip()
            ),
            "usage": (
                list(usage)
                if isinstance(
                    usage,
                    list,
                )
                else []
            ),
            "folder_id": "",
            "created_at": created_at,
            }

        data = self._read_index()

        data["images"].append(
            item
        )

        self._write_index(
            data
        )

        return {
            "status": "success",
            "image": item,
        }


    def list_images(
        self,
    ) -> list[dict[str, Any]]:

        data = self._read_index()

        return list(
            data.get(
                "images",
                [],
            )
        )


    def get_image(
        self,
        image_id: str,
    ) -> dict[str, Any]:

        cleaned_id = str(
            image_id or ""
        ).strip()

        if not cleaned_id:

            return {
                "status": "error",
                "error": "Missing image_id.",
            }

        data = self._read_index()

        for item in data.get(
            "images",
            [],
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            if (
                item.get("image_id")
                != cleaned_id
            ):
                continue

            relative_path = item.get(
                "relative_path",
                "",
            )

            file_path = (
                self.user_dir
                / relative_path
            )

            if not file_path.exists():

                return {
                    "status": "error",
                    "error": (
                        "Image file not found."
                    ),
                }

            return {
                "status": "success",
                "image": item,
                "image_bytes": (
                    file_path.read_bytes()
                ),
            }

        return {
            "status": "error",
            "error": "Image not found.",
        }
        
    def move_image(
        self,
        image_id: str,
        folder_id: str | None,
    ) -> dict[str, Any]:
    
        cleaned_id = str(
            image_id or ""
        ).strip()
    
        cleaned_folder_id = str(
            folder_id or ""
        ).strip()
    
        if not cleaned_id:
    
            return {
                "status": "error",
                "error": "Missing image_id.",
            }
    
        data = self._read_index()
    
        for item in data.get(
            "images",
            [],
        ):
    
            if not isinstance(
                item,
                dict,
            ):
                continue
    
            if (
                item.get("image_id")
                != cleaned_id
            ):
                continue
    
            item["folder_id"] = (
                cleaned_folder_id
            )
    
            self._write_index(
                data
            )
    
            return {
                "status": "success",
                "image": item,
            }
    
        return {
            "status": "error",
            "error": "Image not found.",
        }
    
    
    def rename_image(
        self,
        image_id: str,
        label: str,
    ) -> dict[str, Any]:
    
        cleaned_id = str(
            image_id or ""
        ).strip()
    
        cleaned_label = str(
            label or ""
        ).strip()
    
        if not cleaned_id:
    
            return {
                "status": "error",
                "error": "Missing image_id.",
            }
    
        if not cleaned_label:
    
            return {
                "status": "error",
                "error": "Image label is empty.",
            }
    
        data = self._read_index()
    
        for item in data.get(
            "images",
            [],
        ):
    
            if not isinstance(
                item,
                dict,
            ):
                continue
    
            if (
                item.get("image_id")
                != cleaned_id
            ):
                continue
    
            item["label"] = (
                cleaned_label
            )
    
            self._write_index(
                data
            )
    
            return {
                "status": "success",
                "image": item,
            }
    
        return {
            "status": "error",
            "error": "Image not found.",
        }    


    def delete_image(
        self,
        image_id: str,
    ) -> dict[str, Any]:

        cleaned_id = str(
            image_id or ""
        ).strip()

        data = self._read_index()

        remaining = []
        deleted_item = None

        for item in data.get(
            "images",
            [],
        ):

            if (
                isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "image_id"
                )
                == cleaned_id
            ):
                deleted_item = item
                continue

            remaining.append(
                item
            )

        if deleted_item is None:

            return {
                "status": "error",
                "error": "Image not found.",
            }

        relative_path = (
            deleted_item.get(
                "relative_path",
                "",
            )
        )

        file_path = (
            self.user_dir
            / relative_path
        )

        if file_path.exists():

            file_path.unlink()

        data["images"] = remaining

        self._write_index(
            data
        )

        return {
            "status": "success",
            "deleted_image": (
                deleted_item
            ),
        }


    def clear_all(
        self,
    ) -> dict[str, Any]:

        if self.images_dir.exists():

            shutil.rmtree(
                self.images_dir
            )

        self.images_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._write_index(
            {
                "version": 1,
                "images": [],
            }
        )

        return {
            "status": "success",
        }


    def _extension_from_mime(
        self,
        mime_type: str,
    ) -> str:

        cleaned = str(
            mime_type or ""
        ).lower()

        if cleaned == "image/png":
            return "png"

        if cleaned == "image/webp":
            return "webp"

        return "jpg"
