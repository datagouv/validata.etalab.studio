"""Utility functions."""

import unicodedata


def strip_accents(s):
    """Remove accents from string, used to sort normalized strings."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )
