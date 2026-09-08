"""Text normalization and tokenization.

Lowercases text, strips punctuation, splits on whitespace, and drops stop-words.
Each surviving token keeps its ordinal position in the original token stream so the
index can support positional queries and snippet generation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    term: str
    position: int


def tokenize(text: str) -> list[Token]:
    """Return the list of tokens for ``text``."""
    raise NotImplementedError
