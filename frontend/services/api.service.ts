/**
 * services/api.service.ts
 * Central AJAX service for all backend communication.
 */

const API_BASE = "https://hiresense-b2vw.onrender.com/api";
interface UploadResponse {
  message: string;
  resume: ResumeDoc;
}

interface ResumeDoc {
  _id: string;
  original_name: string;
  filename: string;
  keywords: string[];
  word_count: number;
  file_type: string;
  uploaded_at: string;
}

interface RankedCandidate {
  _id: string;
  original_name: string;
  score: number;
  rank: number;
  keywords: string[];
  word_count: number;
  match_level: "Excellent" | "Good" | "Fair" | "Low";
  uploaded_at: string;
}

interface Analytics {
  total: number;
  average_score: number;
  max_score: number;
  min_score: number;
  std_dev: number;
  match_levels: { Excellent: number; Good: number; Fair: number; Low: number };
  top_candidate: RankedCandidate | null;
  score_buckets: Record<string, number>;
}

interface RankResponse {
  ranked: RankedCandidate[];
  analytics: Analytics;
  jd_length: number;
}

interface ResumesListResponse {
  count: number;
  resumes: ResumeDoc[];
}

// ── Low-level helpers ─────────────────────────────────────────────────────────

function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  return fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  }).then((res) => {
    if (!res.ok) {
      return res.json().then((body) => {
        throw new Error(body.error || `HTTP ${res.status}`);
      });
    }
    return res.json() as Promise<T>;
  });
}

// ── Public API ────────────────────────────────────────────────────────────────

const ApiService = {
  /**
   * Upload a resume file (PDF / TXT).
   */
  uploadResume(file: File): Promise<UploadResponse> {
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
  getResumes(): Promise<ResumesListResponse> {
    return apiFetch<ResumesListResponse>("/resumes/");
  },

  /**
   * Rank all resumes against a job description.
   */
  rankCandidates(jobDescription: string, resumeIds?: string[]): Promise<RankResponse> {
    const body: Record<string, unknown> = { job_description: jobDescription };
    if (resumeIds && resumeIds.length) body.resume_ids = resumeIds;
    return apiFetch<RankResponse>("/resumes/rank", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  /**
   * Delete a resume by ID.
   */
  deleteResume(id: string): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/resumes/${id}`, { method: "DELETE" });
  },

  /**
   * Health check.
   */
  health(): Promise<{ status: string }> {
    return apiFetch<{ status: string }>("/resumes/health");
  },
};

// Export for AngularJS DI via window global (no build step needed)
(window as any).ApiService = ApiService;