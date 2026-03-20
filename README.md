# HireSense AI — Resume Screening & Candidate Ranking System

> An intelligent resume screening system that automatically ranks candidates against a job description using TF-IDF vectorization and cosine similarity. Built with AngularJS, Python Flask, MongoDB, and scikit-learn.

![HireSense AI](https://img.shields.io/badge/HireSense-AI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb)
![AngularJS](https://img.shields.io/badge/AngularJS-1.8-red?style=for-the-badge&logo=angularjs)

---

## Live Demo

- **Frontend:** https://hiresense-ai-b2z4.onrender.com/#!/dashboard
- **Backend API:** https://hiresense-b2vw.onrender.com
- **Health Check:** https://hiresense-b2vw.onrender.com/api/resumes/health

> Note: The app is hosted on Render's free tier. If it hasn't been visited in 15 minutes, the first request takes 30–60 seconds to wake up. Please wait and refresh.

---

## What is this project?

HireSense AI solves a real problem faced by every HR department — manually reading hundreds of resumes for a single job posting is slow, inconsistent, and error-prone.

This system allows an HR person to:
1. Upload multiple resumes (PDF or TXT) in one go
2. Paste the job description
3. Get every candidate instantly ranked from best match to worst with a score out of 100

The ranking uses **TF-IDF vectorization** and **cosine similarity** — classical NLP techniques from scikit-learn — with no pre-trained model or external dataset required.

---

## Features

- Drag and drop resume upload (PDF + TXT support)
- Batch upload multiple resumes at once
- Automatic text extraction from PDFs using PyPDF2
- Keyword extraction with NLTK stopword removal
- TF-IDF + cosine similarity ranking engine
- Score out of 100 with match level labels (Excellent / Good / Fair / Low)
- Interactive dashboard with Chart.js analytics
- Score distribution bar chart and match quality doughnut chart
- Sortable and filterable ranking table
- Full MongoDB persistence — resumes stored with extracted text and keywords
- REST API with modular Flask blueprint architecture
- Single page application — no page reloads (AJAX throughout)

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | AngularJS 1.8 + TypeScript | Single page application, two-way data binding |
| Styling | HTML5 + CSS3 | Dark SaaS theme, CSS variables |
| Charts | Chart.js 4 | Score distribution and match quality charts |
| Backend | Python Flask 3.0 | REST API server, modular blueprint architecture |
| Database | MongoDB Atlas (PyMongo) | NoSQL document storage for resume data |
| ML / NLP | scikit-learn, NLTK | TF-IDF vectorization, cosine similarity ranking |
| PDF Parsing | PyPDF2 | Text extraction from PDF resumes |
| Server | Gunicorn | Production WSGI server |
| Hosting | Render | Cloud deployment (free tier) |
| Version Control | GitHub | Source code management |

---

## Machine Learning Explained

This project does **not** use deep learning, neural networks, or any pre-trained model. There is no training phase and no external dataset.

### TF-IDF (Term Frequency — Inverse Document Frequency)

TF-IDF converts each text document into a numerical vector. Each position in the vector represents a word's importance score for that specific document.

- **TF (Term Frequency):** How often does the word appear in this resume?
- **IDF (Inverse Document Frequency):** How rare is this word across all resumes? Rare words carry more signal.
- **TF-IDF Score = TF × IDF**

Configuration used:
```python
TfidfVectorizer(
    max_features=5000,   # consider top 5000 words
    ngram_range=(1, 2),  # single words AND two-word phrases
    sublinear_tf=True    # log scaling to prevent frequency dominance
)
```

### Cosine Similarity

After vectorization, each resume and the job description exist as vectors in a 5000-dimensional space. Cosine similarity measures the angle between two vectors.

- Angle = 0° → similarity = 1.0 → perfect keyword match
- Angle = 90° → similarity = 0.0 → no overlap at all

The similarity score is multiplied by 100 to produce the final percentage score shown in the dashboard.

### Why cosine and not word count?

A long resume with 1000 words naturally has more keyword matches than a focused 300-word resume. Cosine similarity normalises for document length, so a short precise resume scores fairly against a long padded one.

### Dataset

No external dataset is used. The system fits the TF-IDF vectorizer fresh on every ranking request using only:
- The job description typed by the user
- The resumes currently uploaded in the system

---

## Project Structure

```
hiresense/
│
├── backend/
│   ├── app.py                    # Flask app factory, CORS, blueprint registration
│   ├── Procfile                  # Gunicorn start command for Render
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (never commit this)
│   │
│   ├── config/
│   │   └── db.py                 # MongoDB Atlas connection singleton
│   │
│   ├── routes/
│   │   └── resume_routes.py      # All /api/resumes/* endpoints (Blueprint)
│   │
│   ├── services/
│   │   ├── resume_service.py     # Upload + ranking pipeline orchestrator
│   │   ├── nlp_service.py        # PDF text extraction + keyword extraction
│   │   └── ranking_service.py    # TF-IDF vectorization + cosine similarity
│   │
│   ├── models/
│   │   └── resume_model.py       # MongoDB CRUD operations
│   │
│   ├── utils/
│   │   └── file_utils.py         # File save, UUID naming, extension validation
│   │
│   └── uploads/                  # Uploaded files stored here (gitignored)
│
└── frontend/
    ├── index.html                # Main SPA shell, sidebar, ng-view
    ├── app.ts / app.js           # AngularJS module, routes, hs-file-input directive
    │
    ├── services/
    │   └── api.service.ts/.js    # All AJAX fetch calls to Flask backend
    │
    ├── controllers/
    │   ├── upload.controller.ts/.js    # Upload page logic, file queue, drag-drop
    │   └── dashboard.controller.ts/.js # Ranking, charts, table sort/filter
    │
    ├── views/
    │   ├── upload.html           # Upload page template
    │   └── dashboard.html        # Dashboard, ranking table, charts template
    │
    └── assets/
        └── styles.css            # Full dark SaaS design system
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root ping — confirms server is running |
| GET | `/test-db` | Tests MongoDB Atlas connection |
| GET | `/api/resumes/health` | Health check endpoint |
| POST | `/api/resumes/upload` | Upload a resume (form-data, field name: `file`) |
| GET | `/api/resumes/` | Get all uploaded resumes |
| GET | `/api/resumes/<id>` | Get a single resume by ID |
| DELETE | `/api/resumes/<id>` | Delete a resume by ID |
| POST | `/api/resumes/rank` | Rank all resumes against a job description |

### Rank request body
```json
{
  "job_description": "Looking for a Python developer with Flask, MongoDB, and ML experience..."
}
```

### Rank response
```json
{
  "ranked": [
    {
      "_id": "64f3ab...",
      "original_name": "arjun_resume.pdf",
      "score": 78.42,
      "rank": 1,
      "match_level": "Excellent",
      "keywords": ["python", "flask", "mongodb", "machine learning"],
      "word_count": 842
    }
  ],
  "analytics": {
    "total": 10,
    "average_score": 45.2,
    "max_score": 78.42,
    "match_levels": { "Excellent": 2, "Good": 4, "Fair": 3, "Low": 1 }
  }
}
```

---

## MongoDB Schema

Each resume is stored as a document in the `resumes` collection inside the `hiresense` database:

```json
{
  "_id": "ObjectId (auto-generated)",
  "original_name": "john_doe_resume.pdf",
  "filename": "a3f9c1d2e4b5.pdf",
  "raw_text": "Full extracted text from the resume...",
  "keywords": ["python", "flask", "react", "mongodb", "aws"],
  "word_count": 842,
  "file_type": "pdf",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "score": null
}
```

> The actual PDF/TXT file is saved on disk in `/backend/uploads/`. MongoDB stores only the extracted text and metadata.

---

## Local Setup — Run on Your Machine

### Prerequisites

Make sure you have these installed:
- Python 3.11+
- Node.js 18+ (for TypeScript compilation only)
- MongoDB locally OR a MongoDB Atlas free account
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/hiresense-ai.git
cd hiresense-ai
```

### Step 2 — Set up the backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (one time only)
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Step 3 — Configure environment variables

Create a file called `.env` inside the `backend/` folder:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=hiresense
PORT=5000
FLASK_DEBUG=true
```

If using MongoDB Atlas instead of local MongoDB:
```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/hiresense?retryWrites=true&w=majority
DB_NAME=hiresense
PORT=5000
FLASK_DEBUG=true
```

### Step 4 — Test the database connection

```bash
# From inside backend/ with venv activated
python config/db.py
```

You should see:
```
Testing MongoDB Atlas connection...
[DB] ✓ Connected to MongoDB Atlas successfully!
[DB] ✓ Test insert successful.
[DB] ✓ Connection fully working!
```

### Step 5 — Start the backend server

```bash
python app.py
```

Backend is running at: `http://localhost:5000`

Test it:
```
http://localhost:5000/test-db
http://localhost:5000/api/resumes/health
```

### Step 6 — Compile TypeScript (frontend)

Open a new terminal:

```bash
cd hiresense-ai/frontend

# Compile all TypeScript files to JavaScript
npx tsc --target ES2020 --lib ES2020,DOM --module None app.ts
npx tsc --target ES2020 --lib ES2020,DOM --module None services/api.service.ts
npx tsc --target ES2020 --lib ES2020,DOM --module None controllers/upload.controller.ts
npx tsc --target ES2020 --lib ES2020,DOM --module None controllers/dashboard.controller.ts
```

### Step 7 — Start the frontend server

```bash
# From inside the frontend/ folder
python -m http.server 4200
```

Frontend is running at: `http://localhost:4200`

---

## Deployment — Render + MongoDB Atlas

### MongoDB Atlas Setup

1. Go to [mongodb.com/atlas](https://mongodb.com/atlas) → create free account
2. Create a free M0 cluster
3. Database Access → Add user with read/write permissions
4. Network Access → Add IP Address → **Allow Access from Anywhere** (`0.0.0.0/0`)
5. Connect → Drivers → copy the connection string

### Deploy Backend on Render

1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repository
3. Fill in settings:

| Field | Value |
|-------|-------|
| Root Directory | `backend` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 "app:create_app()"` |
| Instance Type | `Free` |

4. Add environment variables:

| Key | Value |
|-----|-------|
| `MONGO_URI` | Your Atlas connection string |
| `DB_NAME` | `hiresense` |
| `FLASK_DEBUG` | `false` |
| `PYTHON_VERSION` | `3.11.0` |

### Deploy Frontend on Render

1. Update `frontend/services/api.service.js` — change `API_BASE` to your Render backend URL
2. Push to GitHub
3. Render → New → Static Site → connect same repo

| Field | Value |
|-------|-------|
| Root Directory | `frontend` |
| Build Command | *(leave empty)* |
| Publish Directory | `.` |

---

## Testing the API with curl

```bash
# Health check
curl https://hiresense-b2vw.onrender.com/api/resumes/health

# Upload a resume
curl -X POST https://hiresense-b2vw.onrender.com/api/resumes/upload \
     -F "file=@/path/to/resume.pdf"

# List all resumes
curl https://hiresense-b2vw.onrender.com/api/resumes/

# Rank candidates
curl -X POST https://hiresense-b2vw.onrender.com/api/resumes/rank \
     -H "Content-Type: application/json" \
     -d '{"job_description": "Python developer with Flask and MongoDB experience"}'

# Delete a resume
curl -X DELETE https://hiresense-b2vw.onrender.com/api/resumes/<resume_id>
```

---

## Limitations

- **Scanned PDFs not supported** — PyPDF2 extracts text only; image-based PDFs return empty text. OCR (e.g. Tesseract) would be needed for scanned documents.
- **Semantic understanding** — TF-IDF matches keywords, not meaning. "Python developer" and "Python programmer" score differently even though they mean the same thing.
- **Ephemeral file storage on Render** — uploaded files are deleted on every Render redeploy. Only extracted text persists in MongoDB. For permanent file storage, integrate AWS S3 or Cloudinary.
- **Relative scoring** — scores are relative to the current set of uploaded resumes, not absolute. Adding more resumes changes all scores.
- **Free tier cold starts** — Render free instances sleep after 15 minutes of inactivity. First request after sleep takes 30–60 seconds.

---

## Future Improvements

- Replace TF-IDF with BERT sentence embeddings for semantic matching
- Add OCR support for scanned PDF resumes
- Structured resume parsing — extract name, email, experience years, education separately
- Integrate AWS S3 for permanent file storage
- Add authentication so multiple HR users can have separate resume pools
- Feedback loop — HR marks hired candidates to improve future rankings
- Export ranked results as PDF or Excel report

---

## Author

**Jayesh Gupta**
- GitHub: [@jayeshgupta10c](https://github.com/jayeshgupta10c)
- Project: [HireSense AI](https://github.com/jayeshgupta10c/HireSense)

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Acknowledgements

- [scikit-learn](https://scikit-learn.org/) — TF-IDF vectorizer and cosine similarity
- [PyPDF2](https://pypdf2.readthedocs.io/) — PDF text extraction
- [NLTK](https://www.nltk.org/) — Natural language processing, stopwords
- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [MongoDB Atlas](https://www.mongodb.com/atlas) — Cloud database
- [AngularJS](https://angularjs.org/) — Frontend framework
- [Chart.js](https://www.chartjs.org/) — Data visualization
- [Render](https://render.com/) — Cloud hosting platform
