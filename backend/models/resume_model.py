"""
models/resume_model.py — Resume document schema + CRUD helpers
"""
from datetime import datetime, timezone
from bson import ObjectId
from config.db import get_db

COLLECTION = "resumes"


def _col():
    return get_db()[COLLECTION]


def build_resume_doc(
    filename: str,
    original_name: str,
    raw_text: str,
    keywords: list[str],
    file_type: str,
) -> dict:
    """Build a clean resume document ready for insertion."""
    return {
        "filename":      filename,
        "original_name": original_name,
        "raw_text":      raw_text,
        "keywords":      keywords,
        "file_type":     file_type,
        "word_count":    len(raw_text.split()),
        "uploaded_at":   datetime.now(timezone.utc),
        "score":         None,   # populated after ranking
    }


def insert_resume(doc: dict) -> str:
    """Insert a resume document; return its string ID."""
    result = _col().insert_one(doc)
    return str(result.inserted_id)


def get_all_resumes() -> list[dict]:
    """Return all resumes, newest first, with _id converted to string."""
    docs = list(_col().find().sort("uploaded_at", -1))
    for d in docs:
        d["_id"] = str(d["_id"])
        if hasattr(d.get("uploaded_at"), "isoformat"):
            d["uploaded_at"] = d["uploaded_at"].isoformat()
    return docs


def get_resume_by_id(resume_id: str) -> dict | None:
    """Fetch a single resume by its string ID."""
    try:
        doc = _col().find_one({"_id": ObjectId(resume_id)})
    except Exception:
        return None
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def delete_resume(resume_id: str) -> bool:
    """Delete a resume; returns True if deleted."""
    try:
        result = _col().delete_one({"_id": ObjectId(resume_id)})
        return result.deleted_count > 0
    except Exception:
        return False


def clear_all_resumes() -> int:
    """Drop all resumes – useful for testing. Returns deleted count."""
    result = _col().delete_many({})
    return result.deleted_count