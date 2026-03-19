"""
routes/resume_routes.py — All /api/resumes/* endpoints
"""
from flask import Blueprint, request, jsonify
from services.resume_service import (
    process_upload,
    fetch_all_resumes,
    fetch_resume_by_id,
    remove_resume,
    run_ranking,
)

resume_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")


# ── Health ─────────────────────────────────────────────────────────────────────

@resume_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "HireSense API"}), 200


# ── Upload ─────────────────────────────────────────────────────────────────────

@resume_bp.post("/upload")
def upload_resume():
    """
    POST /api/resumes/upload
    Form-data: file (PDF or TXT)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use field name 'file'."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename."}), 400

    try:
        doc = process_upload(file)
        return jsonify({
            "message": "Resume uploaded and processed successfully.",
            "resume":  doc,
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        print(f"[Upload] Unexpected error: {exc}")
        return jsonify({"error": "Internal server error during upload."}), 500


# ── List All ───────────────────────────────────────────────────────────────────

@resume_bp.get("/")
def list_resumes():
    """GET /api/resumes/ — Return all stored resumes (no raw text to keep payload small)."""
    resumes = fetch_all_resumes()
    # Strip raw_text from list view to keep responses lean
    for r in resumes:
        r.pop("raw_text", None)
    return jsonify({"count": len(resumes), "resumes": resumes}), 200


# ── Single Resume ──────────────────────────────────────────────────────────────

@resume_bp.get("/<resume_id>")
def get_resume(resume_id: str):
    """GET /api/resumes/<id> — Return a single resume with full text."""
    doc = fetch_resume_by_id(resume_id)
    if not doc:
        return jsonify({"error": "Resume not found."}), 404
    return jsonify(doc), 200


# ── Delete ─────────────────────────────────────────────────────────────────────

@resume_bp.delete("/<resume_id>")
def delete_resume(resume_id: str):
    """DELETE /api/resumes/<id>"""
    success = remove_resume(resume_id)
    if not success:
        return jsonify({"error": "Resume not found."}), 404
    return jsonify({"message": "Resume deleted successfully."}), 200


# ── Rank ───────────────────────────────────────────────────────────────────────

@resume_bp.post("/rank")
def rank_resumes():
    """
    POST /api/resumes/rank
    JSON body:
    {
        "job_description": "...",
        "resume_ids": ["id1", "id2"]   // optional; omit to rank all
    }
    """
    data = request.get_json(silent=True) or {}
    jd   = data.get("job_description", "").strip()

    if not jd:
        return jsonify({"error": "Field 'job_description' is required."}), 400

    resume_ids = data.get("resume_ids")  # None = rank all

    try:
        result = run_ranking(jd, resume_ids)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        print(f"[Rank] Unexpected error: {exc}")
        return jsonify({"error": "Ranking failed due to an internal error."}), 500