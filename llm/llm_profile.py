"""
DeDe - LLM Profiles

Maps reasoning profiles to model providers.
"""


class LLMProfile:

    profiles = {
        "fast": {
            "active": ["openai"],
            "planned": [],
            "description": "Fast response using one active reasoning model.",
        },
        "balanced": {
            "active": ["openai"],
            "planned": ["gemini", "mistral"],
            "description": "Balanced reasoning with room for model comparison.",
        },
        "deep": {
            "active": ["openai"],
            "planned": ["gemini", "mistral", "deepseek", "qwen"],
            "description": "Deep multi-model reasoning profile, prepared for committee mode.",
        },
        "asian": {
            "active": [],
            "planned": ["deepseek", "qwen", "glm"],
            "description": "Asian AI model profile prepared for future integration.",
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
