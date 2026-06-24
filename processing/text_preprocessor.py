"""
DeDe - Text Preprocessor

Provides a shared text preprocessing layer for all detectors.
"""

from dataclasses import dataclass, field
import re


@dataclass
class ProcessedText:
    """
    Shared representation of an analyzed text.
    """

    raw_text: str
    normalized_text: str
    paragraphs: list[str] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)

    char_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    unique_word_count: int = 0
    lexical_diversity: float = 0.0


class TextPreprocessor:
    """
    Converts raw text into a reusable processed representation.
    """

    def process(self, text: str) -> ProcessedText:
        raw_text = text or ""
        normalized_text = self._normalize(raw_text)

        paragraphs = self._split_paragraphs(normalized_text)
        sentences = self._split_sentences(normalized_text)
        tokens = self._tokenize(normalized_text)

        word_count = len(tokens)
        unique_word_count = len(set(tokens))

        lexical_diversity = (
            unique_word_count / word_count
            if word_count > 0
            else 0.0
        )

        return ProcessedText(
            raw_text=raw_text,
            normalized_text=normalized_text,
            paragraphs=paragraphs,
            sentences=sentences,
            tokens=tokens,
            char_count=len(raw_text),
            word_count=word_count,
            sentence_count=len(sentences),
            paragraph_count=len(paragraphs),
            unique_word_count=unique_word_count,
            lexical_diversity=lexical_diversity,
        )

    def _normalize(self, text: str) -> str:
        """
        Normalize whitespace and lowercase text.
        """

        text = text.strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    def _split_paragraphs(self, text: str) -> list[str]:
        """
        Split text into paragraphs.
        """

        return [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

    def _split_sentences(self, text: str) -> list[str]:
        """
        Split text into simple sentences.
        """

        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if sentence.strip()
        ]

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenize text into simple word tokens.
        """

        return re.findall(r"\b\w+\b", text)
