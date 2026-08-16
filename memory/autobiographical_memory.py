"""
DeDe - Autobiographical Memory

Builds a long-term cognitive profile of the relationship
between DeDe and the user.

AutobiographicalMemory does not perform language-specific
semantic detection.

It receives structured observations produced by upstream
cognitive components and integrates them over time.

This separation allows autobiographical memory to remain
multilingual by architecture rather than by lexical markers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class AutobiographicalMemory:

    name = "autobiographical_memory"

    def update(
        self,
        text: str,
        persistent_memory: dict[str, Any],
        canonical_concepts: list[str] | None = None,
        dialogue_profile: dict[str, Any] | None = None,
        memory_candidate: dict[str, Any] | None = None,
        cognitive_feedback: dict[str, Any] | None = None,
        project_signals: list[str] | None = None,
        interest_signals: list[str] | None = None,
        evolution_event: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Integrate structured autobiographical observations.

        The original text is preserved only as provenance.
        It is not searched for language-specific markers.

        All semantic classification should occur upstream.
        """

        persistent_memory = (
            persistent_memory
            if isinstance(
                persistent_memory,
                dict,
            )
            else {}
        )

        autobiography = persistent_memory.get(
            "autobiography",
            {},
        )

        if not isinstance(
            autobiography,
            dict,
        ):
            autobiography = {}

        autobiography = self._merge_defaults(
            autobiography
        )

        canonical_concepts = self._clean_strings(
            canonical_concepts
        )

        project_signals = self._clean_strings(
            project_signals
        )

        interest_signals = self._clean_strings(
            interest_signals
        )

        dialogue_profile = (
            dialogue_profile
            if isinstance(
                dialogue_profile,
                dict,
            )
            else {}
        )

        memory_candidate = (
            memory_candidate
            if isinstance(
                memory_candidate,
                dict,
            )
            else {}
        )

        cognitive_feedback = (
            cognitive_feedback
            if isinstance(
                cognitive_feedback,
                dict,
            )
            else {}
        )

        # --------------------------------------------------
        # Structured cognitive observations
        # --------------------------------------------------

        self._track_cognitive_profile(
            autobiography=autobiography,
            canonical_concepts=canonical_concepts,
            cognitive_feedback=cognitive_feedback,
        )

        # --------------------------------------------------
        # Structured projects
        # --------------------------------------------------

        self._track_named_signals(
            store=autobiography["projects"],
            signals=project_signals,
        )

        # --------------------------------------------------
        # Structured interests
        # --------------------------------------------------

        self._track_named_signals(
            store=autobiography["interests"],
            signals=interest_signals,
        )

        # --------------------------------------------------
        # Dialogue observations
        # --------------------------------------------------

        self._track_dialogue_style(
            autobiography=autobiography,
            dialogue_profile=dialogue_profile,
        )

        # --------------------------------------------------
        # Memory-derived autobiographical information
        # --------------------------------------------------

        self._track_memory_candidate(
            autobiography=autobiography,
            memory_candidate=memory_candidate,
        )

        # --------------------------------------------------
        # Long-term evolution
        # --------------------------------------------------

        if isinstance(
            evolution_event,
            dict,
        ):
            self._track_evolution(
                autobiography=autobiography,
                event=evolution_event,
            )

        # --------------------------------------------------
        # Provenance
        # --------------------------------------------------

        autobiography[
            "interaction_count"
        ] += 1

        autobiography[
            "last_updated"
        ] = self._now()

        autobiography[
            "last_observation"
        ] = {
            "timestamp": self._now(),
            "text_present": bool(
                str(text or "").strip()
            ),
            "canonical_concepts": (
                canonical_concepts[:20]
            ),
        }

        persistent_memory[
            "autobiography"
        ] = autobiography

        return persistent_memory

    # ======================================================
    # Defaults
    # ======================================================

    def _default_autobiography(
        self,
    ) -> dict[str, Any]:

        return {
            "interaction_count": 0,

            "cognitive_profile": {},

            "projects": {},

            "interests": {},

            "dialogue_style": {},

            "memory_types": {},

            "evolution": [],

            "last_observation": {},

            "last_updated": None,
        }

    def _merge_defaults(
        self,
        autobiography: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Preserve existing autobiography while ensuring
        that all expected structures exist.
        """

        default = self._default_autobiography()

        for key, default_value in default.items():

            if key not in autobiography:
                autobiography[key] = default_value

        for key in [
            "cognitive_profile",
            "projects",
            "interests",
            "dialogue_style",
            "memory_types",
            "last_observation",
        ]:
            if not isinstance(
                autobiography.get(key),
                dict,
            ):
                autobiography[key] = {}

        if not isinstance(
            autobiography.get(
                "evolution"
            ),
            list,
        ):
            autobiography[
                "evolution"
            ] = []

        try:
            autobiography[
                "interaction_count"
            ] = int(
                autobiography.get(
                    "interaction_count",
                    0,
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            autobiography[
                "interaction_count"
            ] = 0

        return autobiography

    # ======================================================
    # Cognitive Profile
    # ======================================================

    def _track_cognitive_profile(
        self,
        autobiography: dict[str, Any],
        canonical_concepts: list[str],
        cognitive_feedback: dict[str, Any],
    ) -> None:
        """
        Aggregate semantic concepts and cognitive observations.

        No language-specific lexical classification occurs here.
        """

        profile = autobiography[
            "cognitive_profile"
        ]

        for concept in canonical_concepts:
            self._increment(
                store=profile,
                key=concept,
            )

        observations = cognitive_feedback.get(
            "observations",
            [],
        )

        if isinstance(
            observations,
            dict,
        ):
            observations = list(
                observations.keys()
            )

        if isinstance(
            observations,
            list,
        ):
            for observation in observations:

                if isinstance(
                    observation,
                    str,
                ):
                    normalized = (
                        observation.strip()
                    )

                    if normalized:
                        self._increment(
                            store=profile,
                            key=normalized,
                        )

                elif isinstance(
                    observation,
                    dict,
                ):
                    observation_type = str(
                        observation.get(
                            "type",
                            "",
                        )
                    ).strip()

                    if observation_type:
                        self._increment(
                            store=profile,
                            key=observation_type,
                        )

    # ======================================================
    # Projects and Interests
    # ======================================================

    def _track_named_signals(
        self,
        store: dict[str, int],
        signals: list[str],
    ) -> None:
        """
        Aggregate canonical semantic labels produced upstream.
        """

        for signal in signals:
            self._increment(
                store=store,
                key=signal,
            )

    # ======================================================
    # Dialogue Style
    # ======================================================

    def _track_dialogue_style(
        self,
        autobiography: dict[str, Any],
        dialogue_profile: dict[str, Any],
    ) -> None:
        """
        Aggregate explicit dialogue-profile observations.

        DialogueProfile or another upstream component decides
        what the observation means.
        """

        style_store = autobiography[
            "dialogue_style"
        ]

        style_signals = dialogue_profile.get(
            "style_signals",
            [],
        )

        if isinstance(
            style_signals,
            dict,
        ):
            style_signals = [
                key
                for key, value
                in style_signals.items()
                if value
            ]

        if isinstance(
            style_signals,
            list,
        ):
            for signal in style_signals:

                normalized = str(
                    signal or ""
                ).strip()

                if normalized:
                    self._increment(
                        store=style_store,
                        key=normalized,
                    )

        tone = str(
            dialogue_profile.get(
                "tone",
                "",
            )
            or ""
        ).strip()

        if (
            tone
            and tone != "unknown"
        ):
            self._increment(
                store=style_store,
                key=f"tone:{tone}",
            )

        verbosity = str(
            dialogue_profile.get(
                "verbosity",
                "",
            )
            or ""
        ).strip()

        if (
            verbosity
            and verbosity != "unknown"
        ):
            self._increment(
                store=style_store,
                key=f"verbosity:{verbosity}",
            )

        language = str(
            dialogue_profile.get(
                "language",
                "",
            )
            or ""
        ).strip()

        if (
            language
            and language != "unknown"
        ):
            self._increment(
                store=style_store,
                key=f"language:{language}",
            )

    # ======================================================
    # Memory Candidate
    # ======================================================

    def _track_memory_candidate(
        self,
        autobiography: dict[str, Any],
        memory_candidate: dict[str, Any],
    ) -> None:
        """
        Track the categories of durable information observed.

        The autobiographical layer does not decide whether
        information is allowed to be stored.
        MemoryGovernor remains responsible for permission.
        """

        if not memory_candidate:
            return

        memory_type = str(
            memory_candidate.get(
                "memory_type",
                "",
            )
            or ""
        ).strip()

        if not memory_type:
            return

        self._increment(
            store=autobiography[
                "memory_types"
            ],
            key=memory_type,
        )

    # ======================================================
    # Evolution
    # ======================================================

    def _track_evolution(
        self,
        autobiography: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        """
        Store an explicitly classified evolution event.

        The event must already have been identified upstream.
        """

        event_type = str(
            event.get(
                "type",
                "",
            )
            or ""
        ).strip()

        note = str(
            event.get(
                "note",
                "",
            )
            or ""
        ).strip()

        if not event_type and not note:
            return

        normalized_event = {
            "timestamp": (
                event.get(
                    "timestamp"
                )
                or self._now()
            ),
            "type": (
                event_type
                or "observation"
            ),
            "note": note,
        }

        metadata = event.get(
            "metadata"
        )

        if isinstance(
            metadata,
            dict,
        ):
            normalized_event[
                "metadata"
            ] = metadata

        evolution = autobiography[
            "evolution"
        ]

        signature = (
            normalized_event["type"],
            normalized_event["note"],
        )

        recent_signatures = {
            (
                str(
                    item.get(
                        "type",
                        ""
                    )
                ),
                str(
                    item.get(
                        "note",
                        ""
                    )
                ),
            )
            for item in evolution[-10:]
            if isinstance(
                item,
                dict,
            )
        }

        if signature not in recent_signatures:
            evolution.append(
                normalized_event
            )

        if len(evolution) > 50:
            autobiography[
                "evolution"
            ] = evolution[-50:]

    # ======================================================
    # Helpers
    # ======================================================

    def _clean_strings(
        self,
        values: list[str] | None,
    ) -> list[str]:

        if not isinstance(
            values,
            list,
        ):
            return []

        cleaned = []

        seen = set()

        for value in values:

            normalized = str(
                value or ""
            ).strip()

            if (
                not normalized
                or normalized in seen
            ):
                continue

            seen.add(
                normalized
            )

            cleaned.append(
                normalized
            )

        return cleaned

    def _increment(
        self,
        store: dict[str, int],
        key: str,
    ) -> None:

        normalized_key = str(
            key or ""
        ).strip()

        if not normalized_key:
            return

        try:
            current_value = int(
                store.get(
                    normalized_key,
                    0,
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            current_value = 0

        store[
            normalized_key
        ] = current_value + 1

    def _now(
        self,
    ) -> str:

        return datetime.now(
            timezone.utc,
        ).isoformat()
