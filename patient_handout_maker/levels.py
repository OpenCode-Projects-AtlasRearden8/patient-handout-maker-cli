"""A rough reading-grade estimator, used to sanity-check plain language.

This is a lightweight Flesch-Kincaid style approximation for internal
feedback only. It is not a research-grade readability tool, and it is
absolutely not a clinical instrument.
"""

from __future__ import annotations

import re
from typing import Tuple

_SyllableFallbackRE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _count_syllables(word: str) -> int:
    """Very small heuristic syllable counter (English-ish)."""
    word = word.lower().strip(".,!?;:\"'()-")
    if not word:
        return 0
    vowels = _SyllableFallbackRE.findall(word)
    count = len(vowels)
    if word.endswith("e") and count > 1 and not word.endswith(("le", "ee")):
        count -= 1
    return max(1, count)


def text_stats(text: str) -> Tuple[int, int, int]:
    """Return (words, sentences, syllables) for a block of text."""
    sentences = len([s for s in re.split(r"[.!?]+\s|\n\n", text) if s.strip()])
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    syllables = sum(_count_syllables(word) for word in words)
    return len(words), max(1, sentences), syllables


def estimated_grade(text: str) -> float:
    """Rough Flesch-Kincaid grade estimate for a block of text."""
    words, sentences, syllables = text_stats(text)
    if words == 0:
        return 0.0
    words_per_sentence = words / sentences
    syllables_per_word = syllables / words
    grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    return max(0.0, round(grade, 1))
