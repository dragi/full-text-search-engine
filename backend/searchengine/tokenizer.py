"""Text normalization and tokenization.

The tokenizer lowercases text, drops apostrophes so contractions collapse
(``don't`` -> ``dont``), treats every other non-alphanumeric character as a
separator, and removes stop-words. Matching is Unicode-aware, so accented letters
survive (``café`` stays ``café``).

Each surviving token keeps its position: the ordinal index of the word in the
document, counted before stop-words are removed. Keeping the pre-removal index
means the gaps left by dropped stop-words are preserved, which keeps term
distances meaningful for snippet generation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from searchengine.stopwords import STOP_WORDS

_APOSTROPHES = str.maketrans("", "", "'’ʼ")
_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True)
class Token:
    term: str
    position: int


def normalize(text: str) -> str:
    """Lowercase ``text`` and strip apostrophes."""
    return text.lower().translate(_APOSTROPHES)


def analyze(text: str) -> list[str]:
    """Return the raw term sequence for ``text`` without removing stop-words."""
    return _WORD_RE.findall(normalize(text))


def tokenize(text: str) -> list[Token]:
    """Return the indexable tokens for ``text``, stop-words removed."""
    return [
        Token(term, position)
        for position, term in enumerate(analyze(text))
        if term not in STOP_WORDS
    ]
