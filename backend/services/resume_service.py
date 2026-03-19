"""
services/resume_service.py — High-level business logic for resume operations
"""
from utils.file_utils import save_uploaded_file, get_file_path, delete_file
from services.nlp_service import extract_text, extract_keywords
from services.ranking_service import rank_candidates, compute_analytics
from models.resume_model import (
    build_resume_doc,
    insert_resume,
    get_all_resumes,
    get_resume_by_id,
    delete_resume as db_delete_resume,
)


# ── Upload Pipeline ───────────────────────────────────────────────────────────

def process_upload(file_storage) -> dict:
    """
    Full upload pipeline:
    1. Save file to disk
    2. Extract text
    3. Extract keywords
    4. Persist to MongoDB
    Returns the inserted resume doc (with _id as string).
    """
    # 1. Save
    filename, original_name = save_uploaded_file(file_storage)
    filepath = get_file_path(filename)
    ext = filename.rsplit(".", 1)[-1].lower()

    # 2. Extract text
    raw_text = extract_text(filepath)
    if not raw_text.strip():
        # Clean up file if extraction failed
        delete_file(filename)
        raise ValueError(f"Could not extract text from '{original_name}'. Is it a scanned image PDF?")

    # 3. Keywords
    keywords = extract_keywords(raw_text)

    # 4. Build + insert document
    doc = build_resume_doc(
        filename=filename,
        original_name=original_name,
        raw_text=raw_text,
        keywords=keywords,
        file_type=ext,
    )
    resume_id = insert_resume(doc)
    doc["_id"] = resume_id
    if hasattr(doc.get("uploaded_at"), "isoformat"):
        doc["uploaded_at"] = doc["uploaded_at"].isoformat()

    return doc


# ── Fetch Resumes ─────────────────────────────────────────────────────────────

def fetch_all_resumes() -> list[dict]:
    return get_all_resumes()


def fetch_resume_by_id(resume_id: str) -> dict | None:
    return get_resume_by_id(resume_id)


# ── Delete ────────────────────────────────────────────────────────────────────

def remove_resume(resume_id: str) -> bool:
    doc = get_resume_by_id(resume_id)
    if not doc:
        return False
    delete_file(doc.get("filename", ""))
    return db_delete_resume(resume_id)


# ── Ranking Pipeline ──────────────────────────────────────────────────────────

def run_ranking(job_description: str, resume_ids: list[str] | None = None) -> dict:
    """
    Rank all (or a subset of) stored resumes against the given JD.
    Returns { ranked: [...], analytics: {...} }
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    all_resumes = get_all_resumes()

    # Optionally filter to specific IDs
    if resume_ids:
        id_set = set(resume_ids)
        all_resumes = [r for r in all_resumes if r["_id"] in id_set]

    if not all_resumes:
        raise ValueError("No resumes found to rank. Upload resumes first.")

    ranked     = rank_candidates(job_description, all_resumes)
    analytics  = compute_analytics(ranked)

    return {
        "ranked":    ranked,
        "analytics": analytics,
        "jd_length": len(job_description.split()),
    }