"""
DeDe - Autobiographical Reasoner

Turns autobiographical memory into a compact continuity summary.
"""

from typing import Any


class AutobiographicalReasoner:

    name = "autobiographical_reasoner"

    def reason(
        self,
        persistent_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        persistent_memory = persistent_memory or {}
        autobiography = persistent_memory.get("autobiography", {})

        profile = autobiography.get("cognitive_profile", {})
        projects = autobiography.get("projects", {})
        interests = autobiography.get("interests", {})
        dialogue_style = autobiography.get("dialogue_style", {})
        evolution = autobiography.get("evolution", [])

        return {
            "reasoner": self.name,
            "status": "ready",
            "user_name": persistent_memory.get("preferred_name"),
            "interaction_count": autobiography.get("interaction_count", 0),
            "dominant_projects": self._top_items(projects),
            "dominant_interests": self._top_items(interests),
            "dominant_cognitive_traits": self._top_items(profile),
            "dialogue_preferences": self._top_items(dialogue_style),
            "recent_evolution": evolution[-5:],
            "continuity_summary": self._build_summary(
                persistent_memory=persistent_memory,
                autobiography=autobiography,
                projects=projects,
                interests=interests,
                profile=profile,
                dialogue_style=dialogue_style,
            ),
        }

    def _top_items(
        self,
        data: dict[str, int],
        limit: int = 5,
    ) -> list[dict[str, Any]]:

        sorted_items = sorted(
            data.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            {
                "name": name,
                "count": count,
            }
            for name, count in sorted_items[:limit]
            if count > 0
        ]

    def _build_summary(
        self,
        persistent_memory: dict[str, Any],
        autobiography: dict[str, Any],
        projects: dict[str, int],
        interests: dict[str, int],
        profile: dict[str, int],
        dialogue_style: dict[str, int],
    ) -> str:

        name = persistent_memory.get("preferred_name") or "the user"

        main_projects = self._names(self._top_items(projects, 3))
        main_interests = self._names(self._top_items(interests, 3))
        main_traits = self._names(self._top_items(profile, 3))
        main_style = self._names(self._top_items(dialogue_style, 3))

        parts = [
            f"DeDe is building a continuity model with {name}.",
        ]

        if main_projects:
            parts.append(
                "Recurring projects: " + ", ".join(main_projects) + "."
            )

        if main_interests:
            parts.append(
                "Recurring interests: " + ", ".join(main_interests) + "."
            )

        if main_traits:
            parts.append(
                "Observed cognitive tendencies: "
                + ", ".join(main_traits)
                + "."
            )

        if main_style:
            parts.append(
                "Dialogue preferences: " + ", ".join(main_style) + "."
            )

        interaction_count = autobiography.get("interaction_count", 0)

        parts.append(
            f"Recorded autobiographical interactions: {interaction_count}."
        )

        return " ".join(parts)

    def _names(
        self,
        items: list[dict[str, Any]],
    ) -> list[str]:

        return [
            item["name"]
            for item in items
        ]
