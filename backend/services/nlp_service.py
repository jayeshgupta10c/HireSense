"""
services/nlp_service.py — Text extraction from PDFs/TXT + keyword extraction
"""
import re
import string
from pathlib import Path

import PyPDF2
import nltk

# Download NLTK data quietly on first import
for _pkg in ("stopwords", "punkt", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{_pkg}" if "punkt" in _pkg else f"corpora/{_pkg}")
    except LookupError:
        nltk.download(_pkg, quiet=True)

from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words("english"))

# Common resume section headers to keep as signal words
RESUME_SIGNAL_WORDS = {
    "experience", "education", "skills", "projects", "certifications",
    "achievements", "summary", "objective", "python", "java", "javascript",
    "typescript", "react", "angular", "flask", "django", "sql", "mongodb",
    "aws", "docker", "kubernetes", "machine", "learning", "tensorflow",
    "pytorch", "nlp", "api", "rest", "git", "agile", "scrum", "leadership",
    "communication", "management", "analytics", "data", "cloud", "devops",
}


# ── Text Extraction ──────────────────────────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> str:
    """Extract all text from a PDF file using PyPDF2."""
    text_parts = []
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
    except Exception as exc:
        print(f"[NLP] PDF extraction error for {filepath}: {exc}")
        return ""
    return "\n".join(text_parts)


def extract_text_from_txt(filepath: str) -> str:
    """Read a plain-text file safely."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as exc:
        print(f"[NLP] TXT read error for {filepath}: {exc}")
        return ""


def extract_text(filepath: str) -> str:
    """
    Auto-detect file type and extract text.
    Returns empty string on failure (never raises).
    """
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    return extract_text_from_txt(filepath)


# ── Text Cleaning ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Lowercase, remove punctuation/digits, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Keyword Extraction ────────────────────────────────────────────────────────

def extract_keywords(text: str, top_n: int = 30) -> list[str]:
    """
    Extract top_n keywords from text.
    Strategy: frequency-based with stop-word removal, boosted by resume signal words.
    """
    cleaned = clean_text(text)
    tokens = cleaned.split()

    freq: dict[str, int] = {}
    for token in tokens:
        if len(token) > 2 and token not in STOP_WORDS:
            freq[token] = freq.get(token, 0) + 1

    # Boost signal words by 3×
    for word in list(freq.keys()):
        if word in RESUME_SIGNAL_WORDS:
            freq[word] = freq[word] * 3

    sorted_words = sorted(freq, key=lambda w: freq[w], reverse=True)
    return sorted_words[:top_n]


def preprocess_for_tfidf(text: str) -> str:
    """Return cleaned text suitable for TF-IDF vectorizer input."""
    cleaned = clean_text(text)
    tokens = [t for t in cleaned.split() if len(t) > 2 and t not in STOP_WORDS]
    return " ".join(tokens)