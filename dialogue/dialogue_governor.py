"""
DeDe - Dialogue Governor

Protects cognitive autonomy.

DeDe normally provides a complete answer and stops.
Closing questions and conversational invitations are preserved
only when the surrounding dialogue explicitly permits them.
"""

import re


class DialogueGovernor:

    name = "dialogue_governor"

    def apply(
        self,
        text: str,
        allow_closing_question: bool = False,
    ) -> str:

        if not text:
            return text

        cleaned_text = str(text).strip()

        if not cleaned_text:
            return cleaned_text

        if allow_closing_question:
            return cleaned_text

        # --------------------------------------------------
        # Split the response into sentences
        # --------------------------------------------------

        sentences = re.split(
            r"(?<=[.!?…])\s+|\n+",
            cleaned_text,
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if not sentences:
            return cleaned_text

        original_sentence_count = len(
            sentences
        )

        # --------------------------------------------------
        # Remove unnecessary closing questions
        # --------------------------------------------------

        while (
            sentences
            and self._is_closing_question(
                sentences[-1]
            )
        ):
            sentences.pop()

        # --------------------------------------------------
        # Remove indirect conversational invitations
        # --------------------------------------------------

        while (
            sentences
            and self._is_conversational_invitation(
                sentences[-1]
            )
        ):
            sentences.pop()

        if len(sentences) == original_sentence_count:
            return cleaned_text

        return " ".join(
            sentences
        ).strip()

    def _is_closing_question(
        self,
        sentence: str,
    ) -> bool:

        normalized = sentence.strip()

        return normalized.endswith(
            (
                "?",
                "？",
                "¿",
            )
        )

    def _is_conversational_invitation(
        self,
        sentence: str,
    ) -> bool:

        normalized = self._normalize(
            sentence
        )

        invitation_patterns = [
            # French
            r"\bje (?:serais|suis) (?:heureux|heureuse|interesse|interessee|ravi|ravie) "
            r"(?:d[' ]|de |a )?(?:en discuter|approfondir|connaitre|entendre)\b",

            r"\bdis[- ]moi si\b",
            r"\bindique[- ]moi si\b",
            r"\bn[' ]hesite pas a\b",
            r"\bsi tu (?:veux|souhaites|desires)\b",
            r"\bsi vous (?:voulez|souhaitez|desirez)\b",

            # English
            r"\bi (?:would be|am) (?:happy|interested|glad) "
            r"(?:to discuss|to explore|to hear|in discussing)\b",

            r"\blet me know if\b",
            r"\bfeel free to\b",
            r"\bif you (?:want|wish|would like)\b",

            # Spanish
            r"\b(?:estaria|estoy) (?:encantado|encantada|interesado|interesada) "
            r"(?:de|en) (?:hablar|discutir|profundizar|conocer)\b",

            r"\bdime si\b",
            r"\bsi quieres\b",
            r"\bsi desea(?:s)?\b",
            r"\bno dudes en\b",

            # Filipino / Tagalog
            r"\bkung gusto mo\b",
            r"\bsabihin mo sa akin kung\b",
            r"\bmaaari nating talakayin\b",
        ]

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in invitation_patterns
        )

    def _normalize(
        self,
        text: str,
    ) -> str:

        normalized = text.lower().strip()

        replacements = {
            "à": "a",
            "â": "a",
            "ä": "a",
            "á": "a",
            "ã": "a",
            "ç": "c",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "í": "i",
            "î": "i",
            "ï": "i",
            "ñ": "n",
            "ó": "o",
            "ô": "o",
            "ö": "o",
            "õ": "o",
            "ú": "u",
            "ù": "u",
            "û": "u",
            "ü": "u",
        }

        for source, target in replacements.items():
            normalized = normalized.replace(
                source,
                target,
            )

        return normalized
