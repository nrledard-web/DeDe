"""
DeDe - Search Profiles

Maps user-facing knowledge profiles to technical providers.
"""


class SearchProfile:

    profiles = {
        "general": {
            "active": ["duckduckgo"],
            "planned": ["brave", "serpapi"],
            "description": (
                "General web search for everyday questions, products, "
                "services and broad information."
            ),
        },
        "scientific": {
            "active": ["duckduckgo", "arxiv", "crossref"],
            "planned": ["pubmed", "semantic_scholar"],
            "description": (
                "Scientific and academic search using papers, DOIs, "
                "preprints and research-oriented sources."
            ),
        },
        "shopping": {
            "active": ["duckduckgo"],
            "planned": ["brave", "google_shopping", "amazon"],
            "description": (
                "Product-oriented search for prices, availability, "
                "shops and buying options."
            ),
        },
        "news": {
            "active": ["duckduckgo"],
            "planned": ["newsapi", "gdelt", "brave"],
            "description": (
                "Current events and recent information sources."
            ),
        },
        "programming": {
            "active": ["duckduckgo"],
            "planned": ["github", "stackoverflow"],
            "description": (
                "Programming-oriented search for code, documentation, "
                "repositories and developer discussions."
            ),
        },
        "legal": {
            "active": ["duckduckgo"],
            "planned": ["official_legal_sources", "eur_lex"],
            "description": (
                "Legal-oriented search. Planned providers should favor "
                "official legal sources."
            ),
        },
    }

    def resolve(self, profile: str) -> dict:
        profile = profile or "general"

        if profile not in self.profiles:
            profile = "general"

        data = self.profiles[profile]

        return {
            "profile": profile,
            "active_providers": data["active"],
            "planned_providers": data["planned"],
            "description": data["description"],
        }
