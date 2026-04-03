"""Hinglish (Roman Hindi) → Kruti Dev encoded text."""

from __future__ import annotations

import re
from functools import lru_cache

from hinlang import RomanToHindi

from kruti_dev import unicode_to_krutidev

# Common English words: do not transliterate (keep Latin in document).
_COMMON_ENGLISH = {
    "i", "me", "my", "we", "our", "you", "your", "he", "him", "his", "she", "her", "it", "its",
    "they", "them", "their", "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having",
    "do", "does", "did", "doing", "would", "should", "could", "ought", "need", "dare", "used",
    "may", "might", "must", "shall", "will", "can", "a", "an", "the", "and", "but", "if", "or",
    "because", "as", "until", "while", "although", "though", "of", "at", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after", "above",
    "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "just", "also", "now", "hello", "hi", "ok", "okay",
    "yes", "no", "thanks", "please", "email", "http", "https", "www", "com", "org", "net",
}

# Fix frequent roman spellings → Devanagari (hinlang misses some digraphs).
_EXTRA_ROMAN = {
    "bharat": "भारत",
    "Bharat": "भारत",
    "BHARAT": "भारत",
    "mahan": "महान",
    "Mahan": "महान",
    "MAHAN": "महान",
    "hindustan": "हिंदुस्तान",
    "Hindustan": "हिंदुस्तान",
}


@lru_cache(maxsize=1)
def _converter() -> RomanToHindi:
    c = RomanToHindi()
    for k, v in _EXTRA_ROMAN.items():
        c.add_word(k, v)
    return c


_ROMAN_TOKEN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def _is_roman_word(tok: str) -> bool:
    return bool(_ROMAN_TOKEN.fullmatch(tok))


def hinglish_document_to_krutidev(text: str) -> str:
    """
    Replace Latin-letter Hindi words with Kruti Dev font bytes; skip common English words.
    """

    conv = _converter()

    def repl(m: re.Match[str]) -> str:
        w = m.group(0)
        low = w.lower()
        if low in _COMMON_ENGLISH:
            return w
        if not _is_roman_word(w):
            return w
        dev = conv.transliterate(w)
        return unicode_to_krutidev(dev)

    return _ROMAN_TOKEN.sub(repl, text)


def hinglish_selection_to_krutidev(text: str) -> str:
    """Transliterate the whole selection as Hindi (Roman → Devanagari → Kruti Dev)."""

    conv = _converter()
    return unicode_to_krutidev(conv.transliterate(text.strip()))
