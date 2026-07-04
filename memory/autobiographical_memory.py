"""
DeDe - Autobiographical Memory

Builds a long-term profile of the relationship between DeDe and the user.
"""

from typing import Any
from datetime import datetime, timezone


class AutobiographicalMemory:

    name = "autobiographical_memory"

    def update(
        self,
        text: str,
        persistent_memory: dict[str, Any],
    ) -> dict[str, Any]:

        autobiography = persistent_memory.get(
            "autobiography",
            {},
        )

        default = self._default_autobiography()
        default.update(autobiography)
        autobiography = default

        lowered = text.lower()

        self._track_topic(
            autobiography,
            lowered,
        )

        self._track_project(
            autobiography,
            lowered,
        )

        autobiography["interaction_count"] += 1
        autobiography["last_updated"] = self._now()

        persistent_memory["autobiography"] = autobiography

        return persistent_memory

    def _default_autobiography(self) -> dict[str, Any]:

        return {
            "interaction_count": 0,
            "recurring_topics": {},
            "projects": {},
            "core_concepts": {},
            "relationship_notes": [],
            "last_updated": None,
        }

    def _track_topic(
        self,
        autobiography: dict[str, Any],
        lowered: str,
    ) -> None:

        topic_markers = {
            "mecroyance": ["mecroyance", "mécroyance"],
            "doxa": ["doxa"],
            "nouscope": ["nouscope"],
            "ai": ["ia", "ai", "llm", "intelligence artificielle"],
            "memory": ["mémoire", "memory"],
            "revisability": ["révisabilité", "revisability"],
            "cognitive_reduction": ["réduction", "reduction"],
            "religion": ["religion", "relihiyon"],
            "politics": ["politique", "politics"],
            "science": ["science", "scientifique"],
        }

        for topic, markers in topic_markers.items():
            if any(marker in lowered for marker in markers):
                self._increment(
                    autobiography["recurring_topics"],
                    topic,
                )

    def _track_project(
        self,
        autobiography: dict[str, Any],
        lowered: str,
    ) -> None:

        project_markers = {
            "DeDe": ["dede", "daimon", "daïmon"],
            "Doxa Detector": ["doxa detector"],
            "Cognitive Mechanics": ["mécanique cognitive", "cognitive mechanics"],
        }

        for project, markers in project_markers.items():
            if any(marker in lowered for marker in markers):
                self._increment(
                    autobiography["projects"],
                    project,
                )

    def _increment(
        self,
        store: dict[str, int],
        key: str,
    ) -> None:

        store[key] = store.get(key, 0) + 1

    def _now(self) -> str:

        return datetime.now(
            timezone.utc,
        ).isoformat()
