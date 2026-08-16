"""
DeDe - Dialogue Governor

Protects cognitive autonomy.

DeDe normally provides a complete answer and stops.

The LLM is responsible for understanding conversational intent
semantically and independently of language.

The DialogueGovernor acts only as a final structural safeguard.
It does not rely on language-specific expressions.
"""


class DialogueGovernor:

    name = "dialogue_governor"

    def apply(
        self,
        text: str,
        allow_closing_question: bool = False,
    ) -> str:
        """
        Apply the final dialogue safeguard.

        Semantic conversational behavior is governed upstream
        by DeDe's LLM instructions.

        This component deliberately avoids language-specific
        lexical rules.
        """

        if not text:
            return text

        cleaned_text = str(
            text
        ).strip()

        if not cleaned_text:
            return cleaned_text

        if allow_closing_question:
            return cleaned_text

        # --------------------------------------------------
        # Structural final-question safeguard
        # --------------------------------------------------
        #
        # DeDe normally answers and stops.
        #
        # If the final paragraph consists entirely of a
        # question, remove that paragraph.
        #
        # This is language-neutral because it relies only
        # on punctuation structure.
        #
        # Questions that are necessary for clarification
        # must be explicitly permitted upstream through
        # allow_closing_question=True.
        # --------------------------------------------------

        paragraphs = [
            paragraph.strip()
            for paragraph in cleaned_text.splitlines()
            if paragraph.strip()
        ]

        if len(paragraphs) <= 1:
            return cleaned_text

        final_paragraph = paragraphs[-1]

        if self._is_question(
            final_paragraph
        ):
            paragraphs.pop()

            return "\n\n".join(
                paragraphs
            ).strip()

        return cleaned_text

    def _is_question(
        self,
        text: str,
    ) -> bool:
        """
        Detect whether a text structurally ends as a question.

        No vocabulary or language-specific markers are used.
        """

        normalized = str(
            text or ""
        ).strip()

        if not normalized:
            return False

        return normalized.endswith(
            (
                "?",
                "？",
            )
        )
