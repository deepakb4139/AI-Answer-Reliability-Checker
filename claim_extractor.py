
import re


def extract_claims(text):
    """
    Split an answer into individual claims.
    """

    if not text or not text.strip():
        return []

    # Split sentences using punctuation
    sentences = re.split(r'(?<=[.!?।])\s+', text.strip())

    # Remove empty sentences and clean whitespace
    claims = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return claims
