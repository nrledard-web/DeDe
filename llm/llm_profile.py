"""
DeDe - LLM Profiles

Maps reasoning profiles to model providers.
"""


class LLMProfile:

    profiles = {
        "fast": {
            "active": ["nvidia"],
            "planned": [],
            "description": (
                "Fast response using NVIDIA Nemotron 3 Nano."
            ),
        },
        "balanced": {
            "active": ["nvidia", "kimi"],
            "planned": [],
            "description": (
                "Balanced reasoning using Nemotron and KIMI."
            ),
        },
        "deep": {
            "active": [
                "openai",
                "gemini",
                "mistral",
                "kimi",
                "nvidia",
            ],
            "planned": [
                "deepseek",
                "qwen",
            ],
            "description": (
                "Deep multi-model reasoning with all connected "
                "providers."
            ),
        },
        "asian": {
            "active": [
                "kimi",
                "nvidia",
            ],
            "planned": [
                "deepseek",
                "qwen",
                "glm",
            ],
            "description": (
                "Asian and open-model reasoning profile."
            ),
        },
    }

    def resolve(self, profile: str) -> dict:
        profile = profile or "fast"

        if profile not in self.profiles:
            profile = "fast"

        data = self.profiles[profile]

        return {
            "profile": profile,
            "active_providers": data["active"],
            "planned_providers": data["planned"],
            "description": data["description"],
        }
