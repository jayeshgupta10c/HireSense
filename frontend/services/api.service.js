/**
 * services/api.service.ts
 * Central AJAX service for all backend communication.
 */
const API_BASE = "http://localhost:5000/api";
// ── Low-level helpers ─────────────────────────────────────────────────────────
function apiFetch(path, options = {}) {
    return fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    }).then((res) => {
        if (!res.ok) {
            return res.json().then((body) => {
                throw new Error(body.error || `HTTP ${res.status}`);
            });
        }
        return res.json();
    });
}
// ── Public API ────────────────────────────────────────────────────────────────
const ApiService = {
    /**
     * Upload a resume file (PDF / TXT).
     */
    uploadResume(file) {
        const formData = new FormData();
        formData.append("file", file);
        return fetch(`${API_BASE}/resumes/upload`, {
            method: "POST",
            body: formData,
        }).then((res) => {
            if (!res.ok) {
                return res.json().then((b) => {
                    throw new Error(b.error || `HTTP ${res.status}`);
                });
            }
            return res.json();
        });
    },
    /**
     * Fetch all uploaded resumes.
     */
    getResumes() {
        return apiFetch("/resumes/");
    },
    /**
     * Rank all resumes against a job description.
     */
    rankCandidates(jobDescription, resumeIds) {
        const body = { job_description: jobDescription };
        if (resumeIds && resumeIds.length)
            body.resume_ids = resumeIds;
        return apiFetch("/resumes/rank", {
            method: "POST",
            body: JSON.stringify(body),
        });
    },
    /**
     * Delete a resume by ID.
     */
    deleteResume(id) {
        return apiFetch(`/resumes/${id}`, { method: "DELETE" });
    },
    /**
     * Health check.
     */
    health() {
        return apiFetch("/resumes/health");
    },
};
// Export for AngularJS DI via window global (no build step needed)
window.ApiService = ApiService;
