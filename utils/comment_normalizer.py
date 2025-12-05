import re
import unicodedata


def normalize_comment(text: str) -> str:
    text = text.strip()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.lower()
