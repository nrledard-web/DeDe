"""
DeDe - Dialogue Governor

Protects cognitive autonomy.
DeDe answers, then stops.
"""

import re


class DialogueGovernor:
    name = "dialogue_governor"

    def apply(self, text: str) -> str:
        if not text:
            return text

        lines = text.split("\n")
        cleaned = []

        forbidden_patterns = [
            r"^\s*souhaites-tu\b.*\?\s*$",
            r"^\s*veux-tu\b.*\?\s*$",
            r"^\s*aimerais-tu\b.*\?\s*$",
            r"^\s*te souviens-tu\b.*\?\s*$",
            r"^\s*que veux-tu\b.*\?\s*$",
            r"^\s*quel comportement\b.*\?\s*$",
            r"^\s*de quoi\b.*\?\s*$",

            r"^\s*quieres\b.*\?\s*$",
            r"^\s*quieres que\b.*\?\s*$",
            r"^\s*te gustaria\b.*\?\s*$",
            r"^\s*deseas\b.*\?\s*$",

            r"^\s*do you want\b.*\?\s*$",
            r"^\s*would you like\b.*\?\s*$",
            r"^\s*shall we\b.*\?\s*$",

            r"^\s*si tu veux\b.*$",
            r"^\s*si vous voulez\b.*$",
            r"^\s*la prochaine étape\b.*$",
            r"^\s*en continuité avec\b.*$",
        ]

        for line in lines:
            lowered = line.lower().strip()

            if any(re.match(pattern, lowered) for pattern in forbidden_patterns):
                continue

            cleaned.append(line)

        result = "\n".join(cleaned).strip()

        # sécurité finale : si le dernier paragraphe est une question, on le retire
        paragraphs = [p.strip() for p in result.split("\n\n") if p.strip()]

        if paragraphs and paragraphs[-1].endswith("?"):
            paragraphs = paragraphs[:-1]

        return "\n\n".join(paragraphs).strip()
