"""
app.py — HireSense AI Flask entry point
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # Allow all origins during development
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Test DB connection on startup ─────────────────────────────────────────
    try:
        from config.db import get_db
        db = get_db()
        print("[APP] ✓ Database connected successfully on startup")
    except Exception as e:
        print(f"[APP] ✗ Database connection FAILED on startup: {e}")
        print("[APP] App will still start but database operations will fail")

    # ── Register routes ───────────────────────────────────────────────────────
    from routes.resume_routes import resume_bp
    app.register_blueprint(resume_bp)

    # ── Root endpoint ─────────────────────────────────────────────────────────
    @app.get("/")
    def root():
        return jsonify({
            "message": "HireSense AI Backend running",
            "status": "ok"
        }), 200

    # ── DB test endpoint (visit this in browser to check DB) ──────────────────
    @app.get("/test-db")
    def test_db():
        try:
            from config.db import get_db
            db = get_db()
            # Try a simple operation
            count = db["resumes"].count_documents({})
            return jsonify({
                "status": "connected",
                "database": "hiresense",
                "resumes_count": count,
                "message": "MongoDB Atlas connection working!"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "failed",
                "error": str(e),
                "message": "Database connection failed"
            }), 500

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", 5000))
    print(f"\n🚀 HireSense AI starting on http://localhost:{port}\n")
    application.run(host="0.0.0.0", port=port, debug=True)