"""
DeDe - Read-Only GitHub Connector.

Reads repository trees and text files.
No write, commit, delete or publish operation exists.
"""

from __future__ import annotations

import base64
import os
import re

from typing import Any
from urllib.parse import quote

import requests


class GitHubReadOnly:
    """
    Read GitHub repository content safely.
    """

    name = "github_readonly"

    API_ROOT = "https://api.github.com"

    MAX_FILE_SIZE = 250_000

    BLOCKED_PATH_PARTS = {
        ".env",
        "secret",
        "secrets",
        "credential",
        "credentials",
        "private_key",
        "id_rsa",
        "id_ed25519",
    }

    def __init__(
        self,
        token: str | None = None,
    ) -> None:
        self.token = (
            token
            or os.environ.get(
                "GITHUB_READ_TOKEN"
            )
            or ""
        ).strip()

    def _headers(self) -> dict[str, str]:
        """
        Build GitHub API headers.
        """

        headers = {
            "Accept": (
                "application/vnd.github+json"
            ),
            "X-GitHub-Api-Version": (
                "2026-03-10"
            ),
            "User-Agent": (
                "DeDe-Cognitive-Daimon"
            ),
        }

        if self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        return headers

    @staticmethod
    def _valid_name(
        value: str,
    ) -> bool:
        """
        Validate an owner or repository name.
        """

        return bool(
            re.fullmatch(
                r"[A-Za-z0-9_.-]+",
                str(value or "").strip(),
            )
        )

    def _path_is_allowed(
        self,
        file_path: str,
    ) -> bool:
        """
        Block likely secret or credential files.
        """

        normalized_path = str(
            file_path or ""
        ).strip().lower()

        if not normalized_path:
            return False

        path_parts = {
            part.strip()
            for part in normalized_path.split("/")
            if part.strip()
        }

        for blocked_part in (
            self.BLOCKED_PATH_PARTS
        ):
            if any(
                blocked_part in path_part
                for path_part in path_parts
            ):
                return False

        return True

    def list_files(
        self,
        owner: str,
        repository: str,
        branch: str = "main",
    ) -> dict[str, Any]:
        """
        List repository files recursively.
        """

        owner = str(owner or "").strip()
        repository = str(
            repository or ""
        ).strip()
        branch = str(
            branch or "main"
        ).strip()

        if (
            not self._valid_name(owner)
            or not self._valid_name(
                repository
            )
        ):
            return {
                "status": "invalid_request",
                "error": (
                    "Invalid GitHub owner or "
                    "repository name."
                ),
                "files": [],
            }

        endpoint = (
            f"{self.API_ROOT}/repos/"
            f"{quote(owner)}/"
            f"{quote(repository)}/git/trees/"
            f"{quote(branch)}"
        )

        try:
            response = requests.get(
                endpoint,
                headers=self._headers(),
                params={
                    "recursive": "1",
                },
                timeout=30,
            )

        except requests.RequestException as error:
            return {
                "status": "network_error",
                "error": str(error),
                "files": [],
            }

        if not response.ok:
            return {
                "status": "github_error",
                "error": (
                    f"GitHub HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:500]}"
                ),
                "files": [],
            }

        response_data = response.json()

        files = []

        for item in response_data.get(
            "tree",
            [],
        ):
            if item.get("type") != "blob":
                continue

            file_path = str(
                item.get(
                    "path",
                    "",
                )
                or ""
            ).strip()

            if not self._path_is_allowed(
                file_path
            ):
                continue

            files.append(
                {
                    "path": file_path,
                    "size": int(
                        item.get(
                            "size",
                            0,
                        )
                        or 0
                    ),
                    "sha": str(
                        item.get(
                            "sha",
                            "",
                        )
                    ),
                }
            )

        return {
            "status": "success",
            "owner": owner,
            "repository": repository,
            "branch": branch,
            "files": files,
            "truncated": bool(
                response_data.get(
                    "truncated",
                    False,
                )
            ),
        }

    def read_file(
        self,
        owner: str,
        repository: str,
        file_path: str,
        branch: str = "main",
    ) -> dict[str, Any]:
        """
        Read one text file from GitHub.
        """

        owner = str(owner or "").strip()
        repository = str(
            repository or ""
        ).strip()
        file_path = str(
            file_path or ""
        ).strip()
        branch = str(
            branch or "main"
        ).strip()

        if (
            not self._valid_name(owner)
            or not self._valid_name(
                repository
            )
            or not self._path_is_allowed(
                file_path
            )
        ):
            return {
                "status": "invalid_request",
                "error": (
                    "Invalid or protected "
                    "GitHub file path."
                ),
            }

        endpoint = (
            f"{self.API_ROOT}/repos/"
            f"{quote(owner)}/"
            f"{quote(repository)}/contents/"
            f"{quote(file_path, safe='/')}"
        )

        try:
            response = requests.get(
                endpoint,
                headers=self._headers(),
                params={
                    "ref": branch,
                },
                timeout=30,
            )

        except requests.RequestException as error:
            return {
                "status": "network_error",
                "error": str(error),
            }

        if not response.ok:
            return {
                "status": "github_error",
                "error": (
                    f"GitHub HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:500]}"
                ),
            }

        response_data = response.json()

        file_size = int(
            response_data.get(
                "size",
                0,
            )
            or 0
        )

        if file_size > self.MAX_FILE_SIZE:
            return {
                "status": "file_too_large",
                "error": (
                    "The file is too large "
                    "for Coding Studio."
                ),
            }

        encoded_content = str(
            response_data.get(
                "content",
                "",
            )
            or ""
        ).replace(
            "\n",
            "",
        )

        try:
            file_bytes = base64.b64decode(
                encoded_content
            )

            file_content = file_bytes.decode(
                "utf-8"
            )

        except (
            ValueError,
            UnicodeDecodeError,
            base64.binascii.Error,
        ):
            return {
                "status": "unsupported_file",
                "error": (
                    "The selected file is not "
                    "a supported UTF-8 text file."
                ),
            }

        return {
            "status": "success",
            "owner": owner,
            "repository": repository,
            "branch": branch,
            "path": file_path,
            "sha": str(
                response_data.get(
                    "sha",
                    "",
                )
            ),
            "size": file_size,
            "content": file_content,
        }
