"""
DeDe - Memory Portability

Creates and reads encrypted user-owned memory files.

Portable format:
- encrypted with AES-256-GCM;
- password-derived key with PBKDF2-HMAC-SHA256;
- no password is stored;
- no unencrypted memory content is exposed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import base64
import json
import os

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
    FILE_VERSION = 1
    KDF_ITERATIONS = 600_000
    MAX_FILE_SIZE = 25 * 1024 * 1024

    def export_encrypted(
        self,
        memory_data: dict[str, Any],
        user_id: str,
        password: str,
    ) -> bytes:
        """
        Export memory as an encrypted portable file.
        """

        cleaned_password = str(
            password or ""
        )

        if len(cleaned_password) < 8:
            raise ValueError(
                "The memory password must contain "
                "at least 8 characters."
            )

        if not isinstance(
            memory_data,
            dict,
        ):
            raise ValueError(
                "Memory data must be a dictionary."
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
            password=cleaned_password,
            salt=salt,
            iterations=self.KDF_ITERATIONS,
        )

        cipher = AESGCM(
            key
        )

        ciphertext = cipher.encrypt(
            nonce,
            plaintext,
            self.FILE_FORMAT.encode(
                "utf-8"
            ),
        )

        public_envelope = {
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
            public_envelope,
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
        """
        Decrypt and validate a portable memory file.
        """

        cleaned_password = str(
            password or ""
        )

        if not cleaned_password:
            raise ValueError(
                "A memory password is required."
            )

        if not isinstance(
            encrypted_file,
            bytes,
        ):
            raise ValueError(
                "The encrypted memory file is invalid."
            )

        if len(encrypted_file) > self.MAX_FILE_SIZE:
            raise ValueError(
                "The memory file is too large."
            )

        try:
            envelope = json.loads(
                encrypted_file.decode(
                    "utf-8"
                )
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as error:
            raise ValueError(
                "This is not a valid DeDe memory file."
            ) from error

        if not isinstance(
            envelope,
            dict,
        ):
            raise ValueError(
                "The DeDe memory envelope is invalid."
            )

        if envelope.get(
            "format"
        ) != self.FILE_FORMAT:
            raise ValueError(
                "Unsupported memory file format."
            )

        if envelope.get(
            "version"
        ) != self.FILE_VERSION:
            raise ValueError(
                "Unsupported memory file version."
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
            password=cleaned_password,
            salt=salt,
            iterations=iterations,
        )

        cipher = AESGCM(
            key
        )

        try:
            plaintext = cipher.decrypt(
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
                "The decrypted payload is invalid."
            )

        if private_payload.get(
            "format"
        ) != self.FILE_FORMAT:
            raise ValueError(
                "The decrypted memory format "
                "is invalid."
            )

        memory_data = private_payload.get(
            "memory"
        )

        if not isinstance(
            memory_data,
            dict,
        ):
            raise ValueError(
                "The portable file contains no "
                "valid memory data."
            )

        return {
            "status": "success",
            "owner_id": private_payload.get(
                "owner_id"
            ),
            "exported_at": private_payload.get(
                "exported_at"
            ),
            "memory": memory_data,
        }

    def _derive_key(
        self,
        password: str,
        salt: bytes,
        iterations: int,
    ) -> bytes:

        if iterations < 100_000:
            raise ValueError(
                "The memory file uses an unsafe "
                "key derivation configuration."
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
