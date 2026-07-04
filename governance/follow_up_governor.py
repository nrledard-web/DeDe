"""
DeDe - Follow-Up Governor

Removes unsolicited follow-up questions and steering phrases.
DeDe clarifies, then returns initiative to the user.
"""

import re


class FollowUpGovernor:
    name = "follow_up_governor"

    def __init__(self) -> None:
        self.patterns = [
            r"^souhaites-tu\b.*\?$",
            r"^veux-tu\b.*\?$",
            r"^aimerais-tu\b.*\?$",
            r"^do you want\b.*\?$",
            r"^would you like\b.*\?$",
            r"^shall we\b.*\?$",
            r"^should we\b.*\?$",
            r"^en continuité avec\b.*$",
            r"^la prochaine étape pourrait être\b.*$",
            r"^si tu veux\b.*$",
            r"^je peux aussi\b.*$",
        ]

    def clean(self, text: str) -> str:
        if not text:
            return text

        paragraphs = text.split("\n")
        cleaned = []

        for paragraph in paragraphs:
            line = paragraph.strip()
            lowered = line.lower()

            if any(re.match(pattern, lowered) for pattern in self.patterns):
                continue

            cleaned.append(paragraph)

        return "\n".join(cleaned).strip()
