"""
DeDe - Memory Governor

Applies privacy and retention policy to structured
memory candidates.

This governor does not inspect language-specific markers.
Semantic interpretation belongs to the upstream cognitive
routing layer.
"""

from __future__ import annotations

from typing import Any


class MemoryGovernor:

    name = "memory_governor"

    STORAGE_MODES = {
        "off",
        "session",
        "selective",
        "continuous",
    }

    MEMORY_TYPES = {
        "identity",
        "preference",
        "personal_fact",
        "project",
        "decision",
        "relationship",
        "interaction_note",
        "autobiographical",
        "temporary_task",
        "unknown",
    }

    STORAGE_SCOPES = {
        "none",
        "working",
        "session",
        "project",
        "personal",
        "persistent",
    }

    SENSITIVITY_LEVELS = {
        "low",
        "medium",
        "high",
    }

    DURABLE_MEMORY_TYPES = {
        "identity",
        "preference",
        "personal_fact",
        "project",
        "decision",
        "relationship",
        "autobiographical",
    }

    MINIMUM_CONFIDENCE = 0.75

    def evaluate(
        self,
        text: str,
        storage_mode: str = "selective",
        candidate: dict[str, Any] | None = None,
        user_approved: bool = False,
    ) -> dict[str, Any]:
        """
        Decide the retention scope of a structured candidate.

        The raw text is accepted only for compatibility and
        provenance. It is not searched for linguistic markers.
        """

        resolved_mode = str(
            storage_mode or "selective"
        ).strip().lower()

        if (
            resolved_mode
            not in self.STORAGE_MODES
        ):
            resolved_mode = "selective"

        normalized_candidate = (
            self._normalize_candidate(
                candidate
            )
        )

        if resolved_mode == "off":
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope="none",
                candidate=normalized_candidate,
                allow_persistent_storage=False,
                allow_autobiographical_storage=False,
                requires_confirmation=False,
                reason=(
                    "Persistent and session memory "
                    "are disabled by user policy."
                ),
            )

        if resolved_mode == "session":
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope="session",
                candidate=normalized_candidate,
                allow_persistent_storage=False,
                allow_autobiographical_storage=False,
                requires_confirmation=False,
                reason=(
                    "The information may remain in "
                    "the current session only."
                ),
            )

        if not normalized_candidate:
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope="session",
                candidate={},
                allow_persistent_storage=False,
                allow_autobiographical_storage=False,
                requires_confirmation=False,
                reason=(
                    "No structured durable-memory "
                    "candidate was supplied."
                ),
            )

        sensitivity = normalized_candidate[
            "sensitivity"
        ]

        confidence = normalized_candidate[
            "confidence"
        ]

        memory_type = normalized_candidate[
            "memory_type"
        ]

        proposed_scope = normalized_candidate[
            "proposed_scope"
        ]

        if sensitivity == "high":
            if not user_approved:
                return self._decision(
                    storage_mode=resolved_mode,
                    storage_scope="session",
                    candidate=normalized_candidate,
                    allow_persistent_storage=False,
                    allow_autobiographical_storage=False,
                    requires_confirmation=True,
                    reason=(
                        "Sensitive information requires "
                        "explicit user approval before "
                        "durable storage."
                    ),
                )

            return self._decision(
                storage_mode=resolved_mode,
                storage_scope=proposed_scope,
                candidate=normalized_candidate,
                allow_persistent_storage=True,
                allow_autobiographical_storage=(
                    memory_type
                    == "autobiographical"
                ),
                requires_confirmation=False,
                reason=(
                    "The user explicitly approved "
                    "durable storage of this sensitive "
                    "memory candidate."
                ),
            )

        if confidence < self.MINIMUM_CONFIDENCE:
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope="session",
                candidate=normalized_candidate,
                allow_persistent_storage=False,
                allow_autobiographical_storage=False,
                requires_confirmation=False,
                reason=(
                    "Candidate confidence is too low "
                    "for durable memory."
                ),
            )

        if (
            memory_type
            not in self.DURABLE_MEMORY_TYPES
        ):
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope="session",
                candidate=normalized_candidate,
                allow_persistent_storage=False,
                allow_autobiographical_storage=False,
                requires_confirmation=False,
                reason=(
                    "The candidate describes temporary "
                    "or non-durable information."
                ),
            )

        if proposed_scope not in {
            "project",
            "personal",
            "persistent",
        }:
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope="session",
                candidate=normalized_candidate,
                allow_persistent_storage=False,
                allow_autobiographical_storage=False,
                requires_confirmation=False,
                reason=(
                    "The proposed scope is not durable."
                ),
            )

        if resolved_mode == "selective":
            if not user_approved:
                return self._decision(
                    storage_mode=resolved_mode,
                    storage_scope="session",
                    candidate=normalized_candidate,
                    allow_persistent_storage=False,
                    allow_autobiographical_storage=False,
                    requires_confirmation=True,
                    reason=(
                        "Selective memory requires user "
                        "confirmation before durable storage."
                    ),
                )

            return self._decision(
                storage_mode=resolved_mode,
                storage_scope=proposed_scope,
                candidate=normalized_candidate,
                allow_persistent_storage=True,
                allow_autobiographical_storage=(
                    memory_type
                    == "autobiographical"
                ),
                requires_confirmation=False,
                reason=(
                    "The user approved this selective "
                    "memory candidate."
                ),
            )

        if resolved_mode == "continuous":
            return self._decision(
                storage_mode=resolved_mode,
                storage_scope=proposed_scope,
                candidate=normalized_candidate,
                allow_persistent_storage=True,
                allow_autobiographical_storage=(
                    memory_type
                    == "autobiographical"
                ),
                requires_confirmation=False,
                reason=(
                    "Continuous memory accepted a "
                    "high-confidence, non-sensitive, "
                    "durable candidate."
                ),
            )

        return self._decision(
            storage_mode=resolved_mode,
            storage_scope="session",
            candidate=normalized_candidate,
            allow_persistent_storage=False,
            allow_autobiographical_storage=False,
            requires_confirmation=False,
            reason=(
                "No durable storage rule applied."
            ),
        )

    def _normalize_candidate(
        self,
        candidate: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Validate and normalize structured memory metadata.
        """

        if not isinstance(
            candidate,
            dict,
        ):
            return {}

        content = str(
            candidate.get(
                "content",
                "",
            )
            or ""
        ).strip()

        if not content:
            return {}

        memory_type = str(
            candidate.get(
                "memory_type",
                "unknown",
            )
            or "unknown"
        ).strip().lower()

        if (
            memory_type
            not in self.MEMORY_TYPES
        ):
            memory_type = "unknown"

        proposed_scope = str(
            candidate.get(
                "proposed_scope",
                "session",
            )
            or "session"
        ).strip().lower()

        if (
            proposed_scope
            not in self.STORAGE_SCOPES
        ):
            proposed_scope = "session"

        sensitivity = str(
            candidate.get(
                "sensitivity",
                "medium",
            )
            or "medium"
        ).strip().lower()

        if (
            sensitivity
            not in self.SENSITIVITY_LEVELS
        ):
            sensitivity = "medium"

        try:
            confidence = float(
                candidate.get(
                    "confidence",
                    0.0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        source = str(
            candidate.get(
                "source",
                "conversation",
            )
            or "conversation"
        ).strip()

        project = candidate.get(
            "project"
        )

        if project is not None:
            project = str(
                project
            ).strip() or None

        return {
            "content": content,
            "memory_type": memory_type,
            "proposed_scope": (
                proposed_scope
            ),
            "sensitivity": sensitivity,
            "confidence": confidence,
            "source": source,
            "project": project,
        }

    def _decision(
        self,
        storage_mode: str,
        storage_scope: str,
        candidate: dict[str, Any],
        allow_persistent_storage: bool,
        allow_autobiographical_storage: bool,
        requires_confirmation: bool,
        reason: str,
    ) -> dict[str, Any]:

        return {
            "governor": self.name,
            "status": "ready",
            "storage_mode": storage_mode,
            "storage_scope": storage_scope,
            "candidate": candidate,
            "allow_working_storage": (
                storage_scope
                not in {
                    "none",
                }
            ),
            "allow_persistent_storage": (
                allow_persistent_storage
            ),
            "allow_autobiographical_storage": (
                allow_autobiographical_storage
            ),
            "requires_confirmation": (
                requires_confirmation
            ),
            "reason": reason,
        }
