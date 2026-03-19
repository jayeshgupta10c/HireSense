"""
services/ranking_service.py — TF-IDF vectorization + cosine similarity ranking
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from services.nlp_service import preprocess_for_tfidf


def rank_candidates(job_description: str, resumes: list[dict]) -> list[dict]:
    """
    Rank resumes against a job description using TF-IDF + cosine similarity.

    Parameters
    ----------
    job_description : str
        Raw JD text provided by the recruiter.
    resumes : list[dict]
        List of resume documents (must have 'raw_text', '_id', 'original_name').

    Returns
    -------
    list[dict]
        Ranked list from highest to lowest score, each item containing:
        { _id, original_name, score (0-100), rank, keywords, word_count, match_level }
    """
    if not resumes:
        return []

    # Preprocess texts
    jd_clean       = preprocess_for_tfidf(job_description)
    resume_texts   = [preprocess_for_tfidf(r.get("raw_text", "")) for r in resumes]

    # Guard: drop resumes with no extractable text
    valid_pairs = [(r, t) for r, t in zip(resumes, resume_texts) if t.strip()]
    if not valid_pairs:
        return []

    valid_resumes, valid_texts = zip(*valid_pairs)

    # Fit TF-IDF on corpus = [JD] + all resumes
    corpus     = [jd_clean] + list(valid_texts)
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),   # unigrams + bigrams for richer matching
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector      = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]

    # Cosine similarity of each resume vs JD
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]

    # Build ranked results
    ranked = []
    for idx, (resume, sim) in enumerate(zip(valid_resumes, similarities)):
        score = round(float(sim) * 100, 2)  # scale to 0-100
        ranked.append({
            "_id":           resume["_id"],
            "original_name": resume.get("original_name", "Unknown"),
            "score":         score,
            "keywords":      resume.get("keywords", [])[:15],
            "word_count":    resume.get("word_count", 0),
            "uploaded_at":   resume.get("uploaded_at", ""),
            "match_level":   _match_level(score),
        })

    # Sort descending by score
    ranked.sort(key=lambda x: x["score"], reverse=True)

    # Add rank position
    for position, item in enumerate(ranked, start=1):
        item["rank"] = position

    return ranked


def _match_level(score: float) -> str:
    """Qualitative label for the score bucket."""
    if score >= 75:
        return "Excellent"
    if score >= 50:
        return "Good"
    if score >= 25:
        return "Fair"
    return "Low"


def compute_analytics(ranked: list[dict]) -> dict:
    """
    Compute aggregate analytics from a ranked list.
    Returns stats consumed by the frontend charts.
    """
    if not ranked:
        return {}

    scores = [r["score"] for r in ranked]
    levels = {"Excellent": 0, "Good": 0, "Fair": 0, "Low": 0}
    for r in ranked:
        levels[r["match_level"]] += 1

    return {
        "total":        len(ranked),
        "average_score": round(float(np.mean(scores)), 2),
        "max_score":     round(float(np.max(scores)), 2),
        "min_score":     round(float(np.min(scores)), 2),
        "std_dev":       round(float(np.std(scores)), 2),
        "match_levels":  levels,
        "top_candidate": ranked[0] if ranked else None,
        "score_buckets": _score_buckets(scores),
    }


def _score_buckets(scores: list[float]) -> dict:
    """Bucket scores into ranges for histogram chart."""
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for s in scores:
        if s <= 20:
            buckets["0-20"]    += 1
        elif s <= 40:
            buckets["21-40"]   += 1
        elif s <= 60:
            buckets["41-60"]   += 1
        elif s <= 80:
            buckets["61-80"]   += 1
        else:
            buckets["81-100"]  += 1
    return buckets