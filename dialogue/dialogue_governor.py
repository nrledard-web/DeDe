"""
DeDe - Dialogue Governor

Controls the conversational policy.

Default philosophy:

- clarify
- never steer
- preserve user initiative
"""

import re


class DialogueGovernor:

    name = "dialogue_governor"

    def __init__(self):

        self.forbidden = [

            r"^souhaites-tu.*",

            r"^veux-tu.*",

            r"^aimerais-tu.*",

            r"^si tu veux.*",

            r"^je peux aussi.*",

            r"^la prochaine étape.*",

            r"^en continuité avec.*",

            r"^do you want.*",

            r"^would you like.*",

        ]

    def apply(self, text: str) -> str:

        if not text:
            return text

        paragraphs = []

        for line in text.split("\n"):

            stripped = line.strip()

            if not stripped:
                paragraphs.append("")
                continue

            lowered = stripped.lower()

            remove = False

            for pattern in self.forbidden:

                if re.match(pattern, lowered):

                    remove = True
                    break

            if not remove:

                paragraphs.append(line)

        return "\n".join(paragraphs).strip()
