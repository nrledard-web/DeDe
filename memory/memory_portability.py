"""
DeDe portable memory.

Supports:
- simple readable JSON backups;
- private password-encrypted AES-GCM backups.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import base64
import io
import json
import os
import zipfile

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)
from cryptography.hazmat.primitives.kdf.pbkdf2 import (
    PBKDF2HMAC,
)


class MemoryPortability:

    name = "memory_portability"

    FILE_FORMAT = "dede-memory"
    SIMPLE_FILE_FORMAT = "dede-memory-simple"
    FILE_VERSION = 1
    KDF_ITERATIONS = 600_000
    MAX_FILE_SIZE = 25 * 1024 * 1024

    def export_simple(
        self,
        memory_data: dict[str, Any],
        user_id: str,
    ) -> bytes:

        self._validate_memory(
            memory_data
        )

        payload = {
            "format": self.SIMPLE_FILE_FORMAT,
            "version": self.FILE_VERSION,
            "owner_id": str(
                user_id or "default_user"
            ),
            "exported_at": self._now(),
            "privacy": "unencrypted",
            "memory": memory_data,
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ).encode(
            "utf-8"
        )

    def export_complete(
        self,
        memory_data: dict[str, Any],
        image_items: list[dict[str, Any]],
        image_files: list[dict[str, Any]],
        user_id: str,
    ) -> bytes:
        """
        Export text memory, folders, image metadata
        and image files in one portable ZIP archive.
        """

        self._validate_memory(
            memory_data
        )

        if not isinstance(
            image_items,
            list,
        ):
            image_items = []

        if not isinstance(
            image_files,
            list,
        ):
            image_files = []

        owner_id = str(
            user_id or "default_user"
        ).strip()

        manifest = {
            "format": (
                "dede-complete-memory"
            ),
            "version": (
                self.FILE_VERSION
            ),
            "owner_id": owner_id,
            "exported_at": self._now(),
            "privacy": "unencrypted",
            "contents": {
                "text_memory": True,
                "image_index": True,
                "image_count": len(
                    image_files
                ),
            },
        }

        image_index = {
            "version": 1,
            "images": image_items,
        }

        archive_buffer = (
            io.BytesIO()
        )

        with zipfile.ZipFile(
            archive_buffer,
            mode="w",
            compression=(
                zipfile.ZIP_DEFLATED
            ),
        ) as archive:
            archive.writestr(
                "manifest.json",
                json.dumps(
                    manifest,
                    ensure_ascii=False,
                    indent=2,
                ),
            )

            archive.writestr(
                "user_memory.json",
                json.dumps(
                    memory_data,
                    ensure_ascii=False,
                    indent=2,
                ),
            )

            archive.writestr(
                "image_memory.json",
                json.dumps(
                    image_index,
                    ensure_ascii=False,
                    indent=2,
                ),
            )

            for image_file in image_files:
                if not isinstance(
                    image_file,
                    dict,
                ):
                    continue

                file_name = str(
                    image_file.get(
                        "file_name",
                        "",
                    )
                ).strip()

                image_bytes = (
                    image_file.get(
                        "image_bytes",
                        b"",
                    )
                )

                if (
                    not file_name
                    or not image_bytes
                ):
                    continue

                safe_file_name = (
                    os.path.basename(
                        file_name
                    )
                )

                if not safe_file_name:
                    continue

                archive.writestr(
                    (
                        "images/"
                        f"{safe_file_name}"
                    ),
                    bytes(
                        image_bytes
                    ),
                )

        complete_archive = (
            archive_buffer.getvalue()
        )

        maximum_archive_size = (
            250 * 1024 * 1024
        )

        if len(
            complete_archive
        ) > maximum_archive_size:
            raise ValueError(
                "Complete memory archive exceeds "
                "the 250 MB export limit."
            )

        return complete_archive

    def import_simple(
        self,
        memory_file: bytes,
    ) -> dict[str, Any]:

        payload = self._read_json_file(
            memory_file
        )

        self._validate_envelope(
            payload,
            self.SIMPLE_FILE_FORMAT,
        )

        memory_data = payload.get(
            "memory"
        )

        self._validate_memory(
            memory_data
        )

        return {
            "status": "success",
            "owner_id": payload.get(
                "owner_id"
            ),
            "exported_at": payload.get(
                "exported_at"
            ),
            "privacy": "unencrypted",
            "memory": memory_data,
        }

    def export_encrypted(
        self,
        memory_data: dict[str, Any],
        user_id: str,
        password: str,
    ) -> bytes:

        self._validate_memory(
            memory_data
        )

        cleaned_password = str(
            password or ""
        )

        if len(cleaned_password) < 8:
            raise ValueError(
                "The memory password must contain "
                "at least 8 characters."
            )

        private_payload = {
            "format": self.FILE_FORMAT,
            "version": self.FILE_VERSION,
            "owner_id": str(
                user_id or "default_user"
            ),
            "exported_at": self._now(),
            "memory": memory_data,
        }

        plaintext = json.dumps(
            private_payload,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ).encode(
            "utf-8"
        )

        salt = os.urandom(16)
        nonce = os.urandom(12)

        key = self._derive_key(
            cleaned_password,
            salt,
            self.KDF_ITERATIONS,
        )

        ciphertext = AESGCM(
            key
        ).encrypt(
            nonce,
            plaintext,
            self.FILE_FORMAT.encode(
                "utf-8"
            ),
        )

        envelope = {
            "format": self.FILE_FORMAT,
            "version": self.FILE_VERSION,
            "encryption": "AES-256-GCM",
            "kdf": "PBKDF2-HMAC-SHA256",
            "iterations": self.KDF_ITERATIONS,
            "salt": self._encode(
                salt
            ),
            "nonce": self._encode(
                nonce
            ),
            "ciphertext": self._encode(
                ciphertext
            ),
        }

        return json.dumps(
            envelope,
            ensure_ascii=False,
            indent=2,
        ).encode(
            "utf-8"
        )

    def import_encrypted(
        self,
        encrypted_file: bytes,
        password: str,
    ) -> dict[str, Any]:

        cleaned_password = str(
            password or ""
        )

        if not cleaned_password:
            raise ValueError(
                "A memory password is required."
            )

        envelope = self._read_json_file(
            encrypted_file
        )

        self._validate_envelope(
            envelope,
            self.FILE_FORMAT,
        )

        try:
            iterations = int(
                envelope.get(
                    "iterations",
                    self.KDF_ITERATIONS,
                )
            )

            salt = self._decode(
                envelope["salt"]
            )

            nonce = self._decode(
                envelope["nonce"]
            )

            ciphertext = self._decode(
                envelope["ciphertext"]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "The encrypted memory envelope "
                "is incomplete or corrupted."
            ) from error

        key = self._derive_key(
            cleaned_password,
            salt,
            iterations,
        )

        try:
            plaintext = AESGCM(
                key
            ).decrypt(
                nonce,
                ciphertext,
                self.FILE_FORMAT.encode(
                    "utf-8"
                ),
            )

        except InvalidTag as error:
            raise ValueError(
                "Incorrect password or corrupted "
                "memory file."
            ) from error

        try:
            private_payload = json.loads(
                plaintext.decode(
                    "utf-8"
                )
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as error:
            raise ValueError(
                "The decrypted memory is invalid."
            ) from error

        if not isinstance(
            private_payload,
            dict,
        ):
            raise ValueError(
                "The decrypted memory is invalid."
            )

        self._validate_envelope(
            private_payload,
            self.FILE_FORMAT,
        )

        memory_data = private_payload.get(
            "memory"
        )

        self._validate_memory(
            memory_data
        )

        return {
            "status": "success",
            "owner_id": private_payload.get(
                "owner_id"
            ),
            "exported_at": private_payload.get(
                "exported_at"
            ),
            "privacy": "encrypted",
            "memory": memory_data,
        }

    def _read_json_file(
        self,
        file_data: bytes,
    ) -> dict[str, Any]:

        if not isinstance(
            file_data,
            bytes,
        ):
            raise ValueError(
                "The memory file is invalid."
            )

        if len(
            file_data
        ) > self.MAX_FILE_SIZE:
            raise ValueError(
                "The memory file is too large."
            )

        try:
            payload = json.loads(
                file_data.decode(
                    "utf-8"
                )
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as error:
            raise ValueError(
                "This is not a valid DeDe "
                "memory file."
            ) from error

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "The portable memory is invalid."
            )

        return payload

    def _validate_envelope(
        self,
        payload: dict[str, Any],
        expected_format: str,
    ) -> None:

        if payload.get(
            "format"
        ) != expected_format:
            raise ValueError(
                "Unsupported memory file format."
            )

        if payload.get(
            "version"
        ) != self.FILE_VERSION:
            raise ValueError(
                "Unsupported memory file version."
            )

    def _validate_memory(
        self,
        memory_data: Any,
    ) -> None:

        if not isinstance(
            memory_data,
            dict,
        ):
            raise ValueError(
                "Memory data must be a dictionary."
            )

    def _derive_key(
        self,
        password: str,
        salt: bytes,
        iterations: int,
    ) -> bytes:

        if iterations < 100_000:
            raise ValueError(
                "Unsafe key derivation configuration."
            )

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )

        return kdf.derive(
            password.encode(
                "utf-8"
            )
        )

    def _encode(
        self,
        value: bytes,
    ) -> str:

        return base64.b64encode(
            value
        ).decode(
            "ascii"
        )

    def _decode(
        self,
        value: str,
    ) -> bytes:

        return base64.b64decode(
            str(value),
            validate=True,
        )

    def _now(
        self,
    ) -> str:

        return datetime.now(
            timezone.utc,
        ).isoformat()
