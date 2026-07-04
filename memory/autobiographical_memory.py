"""
DeDe - Autobiographical Memory

Builds a long-term cognitive profile of the relationship
between DeDe and the user.

This memory does not store everything.
It tracks recurring structures:
- cognitive profile
- user projects
- interests
- dialogue style
- long-term evolution
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

        self._track_cognitive_profile(
            autobiography,
            lowered,
        )

        self._track_projects(
            autobiography,
            lowered,
        )

        self._track_interests(
            autobiography,
            lowered,
        )

        self._track_dialogue_style(
            autobiography,
            text,
            lowered,
        )

        self._track_evolution(
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
            "cognitive_profile": {
                "revisability_focus": 0,
                "systems_thinking": 0,
                "concept_creation": 0,
                "philosophical_reasoning": 0,
                "technical_building": 0,
                "epistemic_caution": 0,
            },
            "projects": {},
            "interests": {},
            "dialogue_style": {
                "prefers_step_by_step": 0,
                "prefers_copy_paste_code": 0,
                "asks_for_architecture": 0,
                "tests_by_reboot": 0,
                "uses_multilingual_context": 0,
            },
            "evolution": [],
            "last_updated": None,
        }

    # --------------------------------------------------
    # Cognitive Profile
    # --------------------------------------------------

    def _track_cognitive_profile(
        self,
        autobiography: dict[str, Any],
        lowered: str,
    ) -> None:

        markers = {
            "revisability_focus": [
                "révisabilité",
                "revisability",
                "révisable",
                "revisable",
            ],
            "systems_thinking": [
                "architecture",
                "pipeline",
                "système",
                "system",
                "module",
                "orchestrateur",
            ],
            "concept_creation": [
                "concept",
                "formule",
                "mécroyance",
                "mecroyance",
                "nouscope",
                "doxa",
                "gnosis",
            ],
            "philosophical_reasoning": [
                "philosophie",
                "philosophical",
                "ontologie",
                "réel",
                "cognition",
                "croyance",
            ],
            "technical_building": [
                "code",
                "implémentation",
                "implementation",
                "github",
                "streamlit",
                "python",
            ],
            "epistemic_caution": [
                "source",
                "preuve",
                "vérifier",
                "verify",
                "incertitude",
                "nuance",
                "hallucination",
            ],
        }

        self._increment_markers(
            autobiography["cognitive_profile"],
            lowered,
            markers,
        )

    # --------------------------------------------------
    # Projects
    # --------------------------------------------------

    def _track_projects(
        self,
        autobiography: dict[str, Any],
        lowered: str,
    ) -> None:

        markers = {
            "DeDe": [
                "dede",
                "daimon",
                "daïmon",
                "compagnon cognitif",
            ],
            "Doxa Detector": [
                "doxa detector",
                "doxa-detector",
                "détecteur",
                "detector",
            ],
            "Cognitive Mechanics": [
                "mécanique cognitive",
                "cognitive mechanics",
                "m=(g+n)-d",
            ],
            "NOUSCOPE": [
                "nouscope",
                "filtre cognitif",
                "cognitive filter",
            ],
            "Autobiographical Memory": [
                "mémoire autobiographique",
                "autobiographical memory",
                "mémoire persistante",
                "persistent memory",
            ],
            "Multi LLM Architecture": [
                "multi-llm",
                "plusieurs llm",
                "gpt",
                "claude",
                "gemini",
                "nemotron",
            ],
            "Search Engine Connection": [
                "moteur de recherche",
                "internet",
                "web search",
                "recherche web",
                "tavily",
                "brave search",
            ],
        }

        self._increment_markers(
            autobiography["projects"],
            lowered,
            markers,
        )

    # --------------------------------------------------
    # Interests
    # --------------------------------------------------

    def _track_interests(
        self,
        autobiography: dict[str, Any],
        lowered: str,
    ) -> None:

        markers = {
            "AI": [
                "ia",
                "ai",
                "llm",
                "intelligence artificielle",
            ],
            "Philosophy": [
                "philosophie",
                "ontologie",
                "vérité",
                "réel",
                "croyance",
            ],
            "Science": [
                "science",
                "scientifique",
                "relativité",
                "climat",
                "physique",
            ],
            "Politics": [
                "politique",
                "patriotisme",
                "communisme",
                "nazisme",
            ],
            "Religion": [
                "religion",
                "foi",
                "croyance religieuse",
                "relihiyon",
            ],
            "Language": [
                "langue",
                "anglais",
                "français",
                "filipino",
                "tagalog",
                "traduction",
            ],
            "Memory": [
                "mémoire",
                "memory",
                "souvenir",
                "persistante",
            ],
        }

        self._increment_markers(
            autobiography["interests"],
            lowered,
            markers,
        )

    # --------------------------------------------------
    # Dialogue Style
    # --------------------------------------------------

    def _track_dialogue_style(
        self,
        autobiography: dict[str, Any],
        text: str,
        lowered: str,
    ) -> None:

        style = autobiography["dialogue_style"]

        if any(
            marker in lowered
            for marker in [
                "pas à pas",
                "étape",
                "explique",
                "explique moi",
                "step by step",
            ]
        ):
            self._increment(style, "prefers_step_by_step")

        if any(
            marker in lowered
            for marker in [
                "copier collé",
                "copier-coller",
                "remplace tout",
                "fais moi le code",
                "go code",
            ]
        ):
            self._increment(style, "prefers_copy_paste_code")

        if any(
            marker in lowered
            for marker in [
                "architecture",
                "pipeline",
                "module",
                "orchestrateur",
                "structure",
            ]
        ):
            self._increment(style, "asks_for_architecture")

        if any(
            marker in lowered
            for marker in [
                "reboot",
                "rafraichissement",
                "refresh",
                "redémarrage",
            ]
        ):
            self._increment(style, "tests_by_reboot")

        multilingual_markers = [
            "english",
            "anglais",
            "français",
            "filipino",
            "tagalog",
            "spanish",
            "espagnol",
        ]

        if any(marker in lowered for marker in multilingual_markers):
            self._increment(style, "uses_multilingual_context")

        if len(text) > 1500:
            self._increment(style, "prefers_step_by_step")

    # --------------------------------------------------
    # Evolution
    # --------------------------------------------------

    def _track_evolution(
        self,
        autobiography: dict[str, Any],
        lowered: str,
    ) -> None:

        important_markers = [
            "ça fonctionne",
            "test réussi",
            "c'est bon",
            "super",
            "magnifique",
            "phase",
            "nouvelle étape",
            "prochaine étape",
            "on a trouvé",
            "ça marche",
        ]

        if not any(marker in lowered for marker in important_markers):
            return

        event = {
            "timestamp": self._now(),
            "note": self._summarize_event(lowered),
        }

        evolution = autobiography["evolution"]

        if event["note"] not in [
            item.get("note")
            for item in evolution[-10:]
        ]:
            evolution.append(event)

        if len(evolution) > 50:
            autobiography["evolution"] = evolution[-50:]

    def _summarize_event(
        self,
        lowered: str,
    ) -> str:

        if "test réussi" in lowered:
            return "A test was reported as successful."

        if "ça fonctionne" in lowered or "ça marche" in lowered:
            return "A functional milestone was reached."

        if "magnifique" in lowered or "super" in lowered:
            return "The user expressed strong satisfaction with progress."

        if "phase" in lowered:
            return "A project phase or transition was discussed."

        if "on a trouvé" in lowered:
            return "A bug or architectural issue was identified."

        return "A meaningful project evolution was mentioned."

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _increment_markers(
        self,
        store: dict[str, int],
        lowered: str,
        markers: dict[str, list[str]],
    ) -> None:

        for key, marker_list in markers.items():
            if any(marker in lowered for marker in marker_list):
                self._increment(
                    store,
                    key,
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
